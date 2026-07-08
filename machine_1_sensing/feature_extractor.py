"""Hand-feature extraction and smoothing for Machine 1.

MediaPipe produces 21 normalized hand landmarks. This module converts them
into the seven compact values sent to Machine 2. It intentionally contains no
camera or network code, which makes the feature calculations easy to test.
"""

# Import math functions such as square root, hypotenuse, and powers.
import math


# Keep the feature order fixed because Wekinator expects values in this exact order.
FEATURE_NAMES = (
    "x",  # Horizontal wrist position in the camera image.
    "y",  # Vertical wrist position in the camera image.
    "speed",  # How far the wrist moved since the previous accepted frame.
    "direction_x",  # Horizontal part of the movement from the previous frame.
    "direction_y",  # Vertical part of the movement from the previous frame.
    "openness",  # How spread out the fingertips are compared with the palm.
    "energy",  # Speed multiplied by openness, used as an expressive intensity cue.
)

# MediaPipe landmark indices for thumb, index, middle, ring, and pinky fingertips.
FINGERTIP_IDS = (4, 8, 12, 16, 20)
# MediaPipe landmark index for the middle finger base, used to estimate palm size.
MIDDLE_FINGER_MCP_ID = 9
# MediaPipe Hands should always give exactly 21 landmarks for one detected hand.
EXPECTED_LANDMARK_COUNT = 21
# Prevent division by zero if the palm-size measurement is extremely tiny.
MINIMUM_PALM_SIZE = 1e-6


def landmark_distance(point_1, point_2):
    """Return the three-dimensional distance between two landmarks."""
    delta_x = point_1.x - point_2.x  # Measure the horizontal difference between landmarks.
    delta_y = point_1.y - point_2.y  # Measure the vertical difference between landmarks.
    delta_z = point_1.z - point_2.z  # Measure the depth difference between landmarks.
    return math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)  # Convert the 3D difference into one distance.


class HandFeatureExtractor:
    """Extract motion and pose features while remembering the previous frame."""

    def __init__(self, movement_dead_zone=0.0):
        if movement_dead_zone < 0:  # A movement threshold cannot be negative.
            raise ValueError("movement_dead_zone cannot be negative.")
        self._movement_dead_zone = movement_dead_zone  # Store the smallest movement worth reporting.
        self._previous_center = None  # Remember the previous wrist position for speed/direction.

    def reset(self):
        """Forget motion history, for example after the hand disappears."""
        self._previous_center = None  # Remove the old wrist position so the next detection starts fresh.

    def extract(self, hand_landmarks):
        """Extract the seven Machine 1 features from MediaPipe landmarks."""
        landmarks = hand_landmarks.landmark  # Get the list of 21 landmark objects from MediaPipe.
        if len(landmarks) != EXPECTED_LANDMARK_COUNT:  # Validate that the hand has the expected structure.
            raise ValueError(
                f"Expected {EXPECTED_LANDMARK_COUNT} hand landmarks, "
                f"received {len(landmarks)}."
            )

        wrist = landmarks[0]  # Landmark 0 is the wrist, used as the hand center.
        center = (wrist.x, wrist.y)  # Store only the 2D position for motion tracking.

        palm_size = max(  # Compute palm size, but never let it become zero.
            landmark_distance(wrist, landmarks[MIDDLE_FINGER_MCP_ID]),  # Distance from wrist to middle-finger base.
            MINIMUM_PALM_SIZE,  # Small fallback value that avoids division by zero.
        )
        fingertip_distances = [  # Build a list with wrist-to-fingertip distances.
            landmark_distance(wrist, landmarks[index])  # Measure the distance to one fingertip.
            for index in FINGERTIP_IDS  # Repeat for all five fingertip landmark IDs.
        ]
        openness = sum(fingertip_distances) / len(fingertip_distances)  # Average the five fingertip distances.
        openness /= palm_size  # Normalize openness so distance from the webcam matters less.

        if self._previous_center is None:  # First frame has no previous position to compare with.
            direction_x = 0.0  # No horizontal motion can be measured yet.
            direction_y = 0.0  # No vertical motion can be measured yet.
            self._previous_center = center  # Save this center for the next frame.
        else:
            previous_x, previous_y = self._previous_center  # Unpack the previous wrist position.
            direction_x = center[0] - previous_x  # Compute horizontal movement since the previous accepted center.
            direction_y = center[1] - previous_y  # Compute vertical movement since the previous accepted center.

            movement = math.hypot(direction_x, direction_y)  # Combine x/y movement into one distance.
            if movement < self._movement_dead_zone:  # Treat tiny movement as camera/landmark jitter.
                direction_x = 0.0  # Remove tiny horizontal movement from the output.
                direction_y = 0.0  # Remove tiny vertical movement from the output.
            else:
                self._previous_center = center  # Accept this position as the new motion reference.

        speed = math.hypot(direction_x, direction_y)  # Convert x/y movement into one speed value.
        energy = speed * openness  # Make a combined value that is high for fast, open-hand motion.

        return {  # Return a dictionary so later code can use names instead of remembering positions.
            "x": center[0],  # Send the wrist x position.
            "y": center[1],  # Send the wrist y position.
            "speed": speed,  # Send the movement size.
            "direction_x": direction_x,  # Send the horizontal movement direction/amount.
            "direction_y": direction_y,  # Send the vertical movement direction/amount.
            "openness": openness,  # Send the normalized hand openness.
            "energy": energy,  # Send the expressive energy value.
        }


class FeatureSmoother:
    """Apply exponential smoothing to reduce landmark jitter."""

    def __init__(self, smoothing_factor, dead_bands=None):
        if not 0 < smoothing_factor <= 1:  # The factor must be a fraction from just above 0 to 1.
            raise ValueError("smoothing_factor must be greater than 0 and at most 1.")
        self._factor = smoothing_factor  # Store how strongly new values affect the smoothed output.
        self._dead_bands = {  # Build a dead-band value for every known feature.
            name: float((dead_bands or {}).get(name, 0.0))  # Use the configured value or 0 if absent.
            for name in FEATURE_NAMES  # Repeat for every feature in the OSC contract.
        }
        if any(value < 0 for value in self._dead_bands.values()):  # Negative dead bands do not make sense.
            raise ValueError("dead-band values cannot be negative.")
        self._smoothed_features = None  # Store the latest exponential-smoothed values.
        self._stable_features = None  # Store the latest values that passed the dead-band filter.

    def reset(self):
        """Forget the previous smoothed values."""
        self._smoothed_features = None  # Clear smoothing memory.
        self._stable_features = None  # Clear dead-band memory.

    def update(self, features):
        """Return a smoothed copy of a complete feature dictionary."""
        missing_features = set(FEATURE_NAMES) - set(features)  # Detect missing required feature names.
        if missing_features:  # Refuse to smooth incomplete data.
            missing = ", ".join(sorted(missing_features))  # Format missing feature names for the error.
            raise ValueError(f"Cannot smooth features; missing: {missing}.")

        if self._smoothed_features is None:  # First frame cannot be blended with older values.
            smoothed = {name: float(features[name]) for name in FEATURE_NAMES}  # Start from the raw values.
        else:
            smoothed = {  # Blend each new value with its previous smoothed value.
                name: (
                    self._factor * float(features[name])  # Weight the new measurement.
                    + (1 - self._factor) * self._smoothed_features[name]  # Weight the previous smoothed value.
                )
                for name in FEATURE_NAMES  # Repeat for every feature.
            }

        self._smoothed_features = smoothed  # Save the smoothed values for the next update.

        if self._stable_features is None:  # First frame has no dead-band reference yet.
            stable = smoothed.copy()  # Use the smoothed values directly.
        else:
            stable = {  # Decide feature by feature whether the change is big enough to output.
                name: (
                    smoothed[name]  # Use the new smoothed value when it changed enough.
                    if abs(smoothed[name] - self._stable_features[name])  # Measure the change from the last stable value.
                    >= self._dead_bands[name]  # Compare that change to the configured dead band.
                    else self._stable_features[name]  # Otherwise keep the old stable value.
                )
                for name in FEATURE_NAMES  # Repeat for every feature.
            }

        self._stable_features = stable  # Save the stable values for the next update.
        return stable.copy()  # Return a copy so callers cannot accidentally change internal memory.
