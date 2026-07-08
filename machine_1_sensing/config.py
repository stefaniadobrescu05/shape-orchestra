"""Configuration for the Machine 1 sensing application.

Change ``MACHINE_2_IP`` before the two-machine demo. The remaining defaults
define the OSC contract agreed with Machine 2.
"""

# Select which webcam OpenCV should open; the built-in laptop camera is usually 0.
CAMERA_INDEX = 0

# Require MediaPipe to be at least 70% confident before accepting a new hand detection.
MIN_DETECTION_CONFIDENCE = 0.7
# Require MediaPipe to be at least 70% confident while tracking the hand between frames.
MIN_TRACKING_CONFIDENCE = 0.7

# Blend each new feature value with the previous value so the output moves smoothly.
SMOOTHING_FACTOR = 0.1

# Ignore tiny wrist movements below this normalized distance so camera jitter is not sent.
MOVEMENT_DEAD_ZONE = 0.004

# Keep the previous sent value when a feature only changes by a very small amount.
FEATURE_DEAD_BANDS = {
    "x": 0.003,  # Require the x hand position to change by at least this much.
    "y": 0.003,  # Require the y hand position to change by at least this much.
    "speed": 0.0015,  # Require hand speed to change by at least this much.
    "direction_x": 0.0015,  # Require horizontal movement direction to change enough.
    "direction_y": 0.0015,  # Require vertical movement direction to change enough.
    "openness": 0.02,  # Require the hand-open value to change enough.
    "energy": 0.003,  # Require the combined speed/openness value to change enough.
}

# Tell Machine 1 where Machine 2 is on the local network.
MACHINE_2_IP = "172.20.10.2"
# Send OSC feature packets to Wekinator's input port.
OSC_PORT = 6448
# Use this OSC address so Wekinator knows these messages contain shape features.
OSC_FEATURE_ADDRESS = "/shape/features"

# Send one OSC packet every two detected frames, reducing network traffic slightly.
SEND_EVERY_N_FRAMES = 2


def validate_config():
    """Raise a clear error when a configuration value is invalid."""
    if not 0 < SMOOTHING_FACTOR <= 1:  # Smoothing must be a useful fraction.
        raise ValueError("SMOOTHING_FACTOR must be greater than 0 and at most 1.")
    if MOVEMENT_DEAD_ZONE < 0:  # A distance threshold cannot be negative.
        raise ValueError("MOVEMENT_DEAD_ZONE cannot be negative.")
    if any(value < 0 for value in FEATURE_DEAD_BANDS.values()):  # Dead bands must be positive or zero.
        raise ValueError("FEATURE_DEAD_BANDS values cannot be negative.")
    if not 1 <= OSC_PORT <= 65535:  # UDP ports must be in the valid port range.
        raise ValueError("OSC_PORT must be between 1 and 65535.")
    if not OSC_FEATURE_ADDRESS.startswith("/"):  # OSC addresses always begin with a slash.
        raise ValueError("OSC_FEATURE_ADDRESS must start with '/'.")
    if SEND_EVERY_N_FRAMES < 1:  # Sending every zero frames would be impossible.
        raise ValueError("SEND_EVERY_N_FRAMES must be at least 1.")
