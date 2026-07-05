"""Hand-feature extraction and smoothing for Machine 1.

MediaPipe produces 21 normalized hand landmarks. This module converts them
into the seven compact values sent to Machine 2. It intentionally contains no
camera or network code, which makes the feature calculations easy to test.
"""

import math


# The order is part of the OSC contract and must also be used on Machine 2.
FEATURE_NAMES = (
    "x",
    "y",
    "speed",
    "direction_x",
    "direction_y",
    "openness",
    "energy",
)

FINGERTIP_IDS = (4, 8, 12, 16, 20)
MIDDLE_FINGER_MCP_ID = 9
EXPECTED_LANDMARK_COUNT = 21
MINIMUM_PALM_SIZE = 1e-6


def landmark_distance(point_1, point_2):
    """Return the three-dimensional distance between two landmarks."""
    delta_x = point_1.x - point_2.x
    delta_y = point_1.y - point_2.y
    delta_z = point_1.z - point_2.z
    return math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)


class HandFeatureExtractor:
    """Extract motion and pose features while remembering the previous frame."""

    def __init__(self, movement_dead_zone=0.0):
        if movement_dead_zone < 0:
            raise ValueError("movement_dead_zone cannot be negative.")
        self._movement_dead_zone = movement_dead_zone
        self._previous_center = None

    def reset(self):
        """Forget motion history, for example after the hand disappears."""
        self._previous_center = None

    def extract(self, hand_landmarks):
        """Extract the seven Machine 1 features from MediaPipe landmarks."""
        landmarks = hand_landmarks.landmark
        if len(landmarks) != EXPECTED_LANDMARK_COUNT:
            raise ValueError(
                f"Expected {EXPECTED_LANDMARK_COUNT} hand landmarks, "
                f"received {len(landmarks)}."
            )

        wrist = landmarks[0]
        center = (wrist.x, wrist.y)

        # Normalize openness by palm size. This makes the value less dependent
        # on how close the performer's hand is to the webcam.
        palm_size = max(
            landmark_distance(wrist, landmarks[MIDDLE_FINGER_MCP_ID]),
            MINIMUM_PALM_SIZE,
        )
        fingertip_distances = [
            landmark_distance(wrist, landmarks[index])
            for index in FINGERTIP_IDS
        ]
        openness = sum(fingertip_distances) / len(fingertip_distances)
        openness /= palm_size

        if self._previous_center is None:
            direction_x = 0.0
            direction_y = 0.0
            self._previous_center = center
        else:
            previous_x, previous_y = self._previous_center
            direction_x = center[0] - previous_x
            direction_y = center[1] - previous_y

            # MediaPipe landmarks move slightly even when the hand is still.
            # Ignore that jitter, but keep the old center so real slow motion
            # accumulates until it crosses the threshold.
            movement = math.hypot(direction_x, direction_y)
            if movement < self._movement_dead_zone:
                direction_x = 0.0
                direction_y = 0.0
            else:
                self._previous_center = center

        speed = math.hypot(direction_x, direction_y)

        # Energy combines how quickly the hand moves with how open it is.
        energy = speed * openness

        return {
            "x": center[0],
            "y": center[1],
            "speed": speed,
            "direction_x": direction_x,
            "direction_y": direction_y,
            "openness": openness,
            "energy": energy,
        }


class FeatureSmoother:
    """Apply exponential smoothing to reduce landmark jitter."""

    def __init__(self, smoothing_factor, dead_bands=None):
        if not 0 < smoothing_factor <= 1:
            raise ValueError("smoothing_factor must be greater than 0 and at most 1.")
        self._factor = smoothing_factor
        self._dead_bands = {
            name: float((dead_bands or {}).get(name, 0.0))
            for name in FEATURE_NAMES
        }
        if any(value < 0 for value in self._dead_bands.values()):
            raise ValueError("dead-band values cannot be negative.")
        self._smoothed_features = None
        self._stable_features = None

    def reset(self):
        """Forget the previous smoothed values."""
        self._smoothed_features = None
        self._stable_features = None

    def update(self, features):
        """Return a smoothed copy of a complete feature dictionary."""
        missing_features = set(FEATURE_NAMES) - set(features)
        if missing_features:
            missing = ", ".join(sorted(missing_features))
            raise ValueError(f"Cannot smooth features; missing: {missing}.")

        if self._smoothed_features is None:
            smoothed = {name: float(features[name]) for name in FEATURE_NAMES}
        else:
            smoothed = {
                name: (
                    self._factor * float(features[name])
                    + (1 - self._factor) * self._smoothed_features[name]
                )
                for name in FEATURE_NAMES
            }

        self._smoothed_features = smoothed

        if self._stable_features is None:
            stable = smoothed.copy()
        else:
            stable = {
                name: (
                    smoothed[name]
                    if abs(smoothed[name] - self._stable_features[name])
                    >= self._dead_bands[name]
                    else self._stable_features[name]
                )
                for name in FEATURE_NAMES
            }

        self._stable_features = stable
        return stable.copy()
