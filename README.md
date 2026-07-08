# Shape Orchestra

Shape Orchestra is an interactive audiovisual project made to run on two
computers. The user moves one hand in front of a webcam and the movement is
used to control the visuals and sound in real time.

The main idea was to use the hand like an instrument. Instead of pressing
buttons, the user can change the result through the position, speed, direction
and openness of the hand.

## How it works

The project is divided into two parts:

- **Machine 1** uses the webcam to detect the hand and calculate the gesture
  data.
- **Machine 2** receives the data, uses Wekinator to recognize the type of
  gesture, and generates the visuals and sound in Processing.

The final Processing window can also be captured with OBS and streamed using
MediaMTX.

```text
Webcam
  -> OpenCV + MediaPipe
  -> gesture features
  -> OSC /shape/features
  -> Wekinator
  -> OSC /shape/control
  -> Processing visuals and sound
  -> OBS
  -> MediaMTX
  -> browser
```

Both computers need to be connected to the same local network.

## Visual and sound states

Wekinator chooses one of four states. It also sends an intensity value which
changes the size, speed, number of shapes and sound volume.

| ID | State | Visual | Sound |
| ---: | --- | --- | --- |
| 1 | CALM | A blue circle moving slowly | A soft low sine sound |
| 2 | PULSE | A pulsing square | A rhythmic pulse sound |
| 3 | TENSION | Red triangles appearing randomly | Faster layered square waves |
| 4 | CLIMAX | Yellow stars moving around the screen | Six sine voices played together |

## OSC communication

The two parts communicate using OSC messages over UDP.

### Machine 1 to Wekinator

```text
Address: /shape/features
Port: 6448
Values: [x, y, speed, direction_x, direction_y, openness, energy]
```

The seven values have the following meaning:

| Value | Meaning |
| --- | --- |
| `x` | Horizontal hand position |
| `y` | Vertical hand position |
| `speed` | How fast the hand is moving |
| `direction_x` | Horizontal movement direction |
| `direction_y` | Vertical movement direction |
| `openness` | How open the hand is |
| `energy` | Speed multiplied by openness |

The values are smoothed before they are sent so that small camera detection
errors do not make the result shake. Machine 1 normally sends around 15
messages per second when the camera runs at 30 FPS.

### Wekinator to Processing

```text
Address: /shape/control
Port: 12000
Values: [state, intensity]
```

`state` is a number from 1 to 4 and selects the current visual and sound mode.
`intensity` is a value between 0.0 and 1.0 and changes how strong the result is.

## Technologies used

- Python 3.11
- OpenCV
- MediaPipe Hands
- NumPy
- python-osc
- Wekinator
- Processing with the `oscP5` and `Sound` libraries
- OBS Studio
- MediaMTX

## What needs to be installed

### Machine 1

- Python 3.11
- A working webcam
- The Python libraries from `machine_1_sensing/requirements.txt`

### Machine 2

- Wekinator
- Processing
- The Processing libraries `oscP5` and `Sound`
- MediaMTX
- OBS Studio
- A browser

## Initial setup

### Machine 1

Open PowerShell in the main project folder and create the Python environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r machine_1_sensing\requirements.txt
```

On Machine 2, run `ipconfig` and find its IPv4 address. Put this address in
`machine_1_sensing/config.py` on Machine 1:

```python
MACHINE_2_IP = "172.20.10.2"  # example; use the actual Machine 2 address
OSC_PORT = 6448
OSC_FEATURE_ADDRESS = "/shape/features"
```

If everything is tested on one computer, use `127.0.0.1`. If Windows asks for
firewall permission, allow Python on the private network.

### Machine 2

1. Open this project in Wekinator:

   ```text
   machine_2_ml_audiovisual_streaming/ml/wekinator_project/
   WekinatorProject/WekinatorProject.wekproj
   ```

   Press **Train** if the model needs to be rebuilt, then press **Run**.

2. Open this file in Processing and run it:

   ```text
   machine_2_ml_audiovisual_streaming/rendering/
   ShapeOrchestraRenderer/ShapeOrchestraRenderer.pde
   ```

3. Start MediaMTX using the provided configuration:

   ```powershell
   .\mediamtx.exe machine_2_ml_audiovisual_streaming\streaming\mediamtx.yml
   ```

4. In OBS, capture the `ShapeOrchestraRenderer` window and its audio. Use these
   stream settings:

   ```text
   Resolution: 1280 x 720
   FPS: 60
   Service: Custom
   Server: rtmp://localhost/shapeorchestra
   Stream key: empty
   ```

5. Start streaming in OBS. The result can be opened at:

   ```text
   http://localhost:8889/shapeorchestra
   ```

## Running the project

The applications should be started in this order:

1. Connect both computers to the same network.
2. Start MediaMTX on Machine 2.
3. Start the Processing sketch on Machine 2.
4. Open the Wekinator project and press **Run**.
5. On Machine 1, run:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python machine_1_sensing\gesture_sender.py
   ```

6. Move one hand in front of the webcam. The Processing visuals and sound
   should change based on the gesture.
7. Start streaming in OBS if the browser output is needed.

Press `q` in the webcam window to stop Machine 1.
