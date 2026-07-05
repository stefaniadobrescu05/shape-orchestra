"""Configuration for the Machine 1 sensing application.

Change ``MACHINE_2_IP`` before the two-machine demo. The remaining defaults
define the OSC contract agreed with Machine 2.
"""

# Webcam configuration. The built-in camera is usually index 0.
CAMERA_INDEX = 0

# MediaPipe detection/tracking confidence thresholds.
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Exponential smoothing factor for the extracted features.
# Lower values reduce jitter but react more slowly; 1.0 disables smoothing.
SMOOTHING_FACTOR = 0.1

# Ignore wrist displacement smaller than this normalized-image distance.
# The ignored displacement accumulates, so deliberate slow motion is still
# detected once it becomes larger than the threshold.
MOVEMENT_DEAD_ZONE = 0.004

# Hold a feature's last output until its smoothed value changes by at least the
# configured amount. These values reduce visible and transmitted flicker.
FEATURE_DEAD_BANDS = {
    "x": 0.003,
    "y": 0.003,
    "speed": 0.0015,
    "direction_x": 0.0015,
    "direction_y": 0.0015,
    "openness": 0.02,
    "energy": 0.003,
}

# OSC destination on Machine 2.
# Keep 127.0.0.1 for local testing, then replace it with Machine 2's LAN IP.
MACHINE_2_IP = "172.20.10.2"
OSC_PORT = 6448
OSC_FEATURE_ADDRESS = "/shape/features"

# Send one OSC packet every N frames in which a hand is detected
SEND_EVERY_N_FRAMES = 2


def validate_config():
    """Raise a clear error when a configuration value is invalid."""
    if not 0 < SMOOTHING_FACTOR <= 1:
        raise ValueError("SMOOTHING_FACTOR must be greater than 0 and at most 1.")
    if MOVEMENT_DEAD_ZONE < 0:
        raise ValueError("MOVEMENT_DEAD_ZONE cannot be negative.")
    if any(value < 0 for value in FEATURE_DEAD_BANDS.values()):
        raise ValueError("FEATURE_DEAD_BANDS values cannot be negative.")
    if not 1 <= OSC_PORT <= 65535:
        raise ValueError("OSC_PORT must be between 1 and 65535.")
    if not OSC_FEATURE_ADDRESS.startswith("/"):
        raise ValueError("OSC_FEATURE_ADDRESS must start with '/'.")
    if SEND_EVERY_N_FRAMES < 1:
        raise ValueError("SEND_EVERY_N_FRAMES must be at least 1.")
