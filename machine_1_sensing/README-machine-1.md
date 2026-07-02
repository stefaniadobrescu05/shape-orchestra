# Machine 1 - Sensing

Machine 1 is the sensing entity of **Shape Orchestra**. It observes one hand
through a webcam, converts the MediaPipe landmarks into seven expressive
features, smooths those features, and sends them to Machine 2 over OSC.

This component deliberately does not perform Machine Learning, audiovisual
rendering, or streaming. Those responsibilities belong to the other parts of
the distributed system.

## Architecture

```text
Webcam
  |
  v
OpenCV + MediaPipe (21 hand landmarks)
  |
  v
Feature extraction + smoothing
  |
  v
OSC /shape/features (7 floats over UDP)
  |
  v
Machine 2 at port 6448
```

## Files

- `gesture_sender.py` owns the webcam loop and coordinates the modules.
- `feature_extractor.py` calculates and smooths the seven features.
- `osc_sender.py` creates the ordered OSC payload and sends it over UDP.
- `config.py` contains camera, smoothing, transmission, and destination values.
- `tests/` verifies feature calculations and the OSC message contract.

Keeping these responsibilities separate prevents camera code, feature logic,
and networking code from becoming tangled together.

## Extracted Features

MediaPipe coordinates are normalized relative to the camera image. The OSC
payload always contains these values in this exact order:

| Position | Name | Meaning |
| ---: | --- | --- |
| 1 | `x` | Horizontal wrist position; normally between 0 and 1 |
| 2 | `y` | Vertical wrist position; normally between 0 and 1 |
| 3 | `speed` | Wrist movement magnitude since the previous frame |
| 4 | `direction_x` | Signed horizontal movement since the previous frame |
| 5 | `direction_y` | Signed vertical movement since the previous frame |
| 6 | `openness` | Mean wrist-to-fingertip distance divided by palm size |
| 7 | `energy` | `speed * openness` |

Normalizing openness by palm size reduces changes caused only by moving the
hand closer to or farther from the webcam. Exponential smoothing reduces small
frame-to-frame landmark fluctuations.

## OSC Contract

Machine 1 sends one OSC message with the following contract:

```text
Transport: UDP
Address:   /shape/features
Port:      6448
Payload:   [x, y, speed, direction_x, direction_y, openness, energy]
Types:     seven 32-bit OSC floats
```

The custom receiver on Machine 2 must listen for this address and interpret the
payload in the documented order. If it then feeds Wekinator, the Wekinator
project should be configured with seven inputs.

`SEND_EVERY_N_FRAMES = 2` sends approximately every second detected webcam
frame. At a 30 FPS camera rate, this is roughly 15 OSC messages per second.

## Setup

Python 3.11 is recommended because it is compatible with the pinned MediaPipe
version.

From the repository root, create a virtual environment:

```powershell
py -3.11 -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r machine_1_sensing\requirements.txt
```

Verify that the active interpreter is Python 3.11:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

## Configure the Two Machines

1. Connect both physical machines to the same local network.
2. On Machine 2, run `ipconfig` and find its IPv4 address.
3. In `config.py`, replace the local-testing value:

   ```python
   MACHINE_2_IP = "127.0.0.1"
   ```

   with the IPv4 address of Machine 2, for example:

   ```python
   MACHINE_2_IP = "192.168.1.42"
   ```

4. Ensure the Machine 2 receiver listens on UDP port `6448` and accepts
   `/shape/features`.
5. If Windows Firewall asks for permission, allow Python on the private
   network. Machine 2 may also need an inbound UDP rule for port `6448`.

Keep `127.0.0.1` only when testing the sender and receiver on the same computer.

## Run Machine 1

Start the Machine 2 OSC receiver first. Then, from the repository root, run:

```powershell
python machine_1_sensing\gesture_sender.py
```

The terminal reports the OSC destination. The webcam window displays the hand
skeleton, live feature values, and whether the current frame sent a packet.
Press `q` in the webcam window to quit.

## Adjust Stability and Send Rate

The main tuning values are in `config.py`:

```python
SMOOTHING_FACTOR = 0.1
MOVEMENT_DEAD_ZONE = 0.004
SEND_EVERY_N_FRAMES = 2
```

- Lower `SMOOTHING_FACTOR` for steadier but slower values.
- Raise it for faster but less stable values.
- Raise `MOVEMENT_DEAD_ZONE` if a still hand produces false movement.
- Adjust `FEATURE_DEAD_BANDS` to control how much each value must change
  before its displayed and transmitted value is updated.
- Raise `SEND_EVERY_N_FRAMES` to reduce OSC traffic.

Start with small tuning changes. Very large dead zones can hide intentional
slow gestures, while very small values allow landmark jitter through.

## Run the Tests

From the repository root:

```powershell
python -m unittest discover -s machine_1_sensing\tests -v
```

The tests do not open the webcam or send network packets.

## Troubleshooting

### `ModuleNotFoundError: No module named 'mediapipe'`

The wrong Python interpreter is active. Activate `.venv` or run the script
directly with:

```powershell
.\.venv\Scripts\python.exe machine_1_sensing\gesture_sender.py
```

### The webcam does not open

Close other applications using the camera. If needed, change `CAMERA_INDEX`
in `config.py` from `0` to `1` or `2`.

### Machine 2 receives nothing

- Confirm that `MACHINE_2_IP` is the address of Machine 2, not Machine 1.
- Confirm both machines are on the same network.
- Confirm the receiver uses UDP port `6448` and `/shape/features`.
- Check the firewall on Machine 2.
- Test with `ping <MACHINE_2_IP>` before debugging OSC.
