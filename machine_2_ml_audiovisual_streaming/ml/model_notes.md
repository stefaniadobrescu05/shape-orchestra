# Shape Orchestra - Machine Learning Model Notes

## 1. Overview
Shape Orchestra uses Wekinator in Machine 2 as the mapping layer between live gesture features and the audiovisual renderer. Machine 1 sends OSC gesture features to Wekinator at `/shape/features`, and Wekinator predicts two control values that are forwarded to Processing as `/shape/control <state> <intensity>`. The Processing renderer then uses `state` to select the current expressive mode and `intensity` to modulate visual and audio parameters continuously.

## 2. OSC Input Configuration
The input side is configured for OSC messages received by Wekinator on port `6448` with the address `/shape/features`. The project uses `7` input values in the order expected by the training and sender scripts.

| Index | Feature | Type | Description |
| --- | --- | --- | --- |
| 1 | `hand_x` | numeric | Horizontal hand position. |
| 2 | `hand_y` | numeric | Vertical hand position. |
| 3 | `speed` | numeric | Overall gesture speed. |
| 4 | `direction_x` | numeric | Horizontal direction component. |
| 5 | `direction_y` | numeric | Vertical direction component. |
| 6 | `openness` | numeric | How open the hand is. |
| 7 | `energy` | numeric | Gesture energy or expressiveness. |

## 3. Input Feature Semantics
The input features describe the performer's live movement stream as a compact gesture summary. `hand_x` and `hand_y` locate the hand in the sensing space, while `speed` captures how fast the movement is evolving. `direction_x` and `direction_y` represent the movement direction on the two axes. `openness` captures whether the hand is more closed or open, and `energy` summarizes the overall intensity of the gesture. The repository does not document the exact feature-extraction formula, so this notes file only records the semantic meaning used by the project.

## 4. OSC Output Configuration
Wekinator sends its predictions to `localhost` on port `12000` using the OSC address `/shape/control`.

The payload order is:

`/shape/control <state> <intensity>`

| Index | Output | Type | Meaning |
| --- | --- | --- | --- |
| 1 | `state` | classification | Discrete expressive class used by the renderer. |
| 2 | `intensity` | real-valued numeric | Continuous control value intended to span `0.0` to `1.0`. |

## 5. Expressive State Model
The renderer and test sender use four expressive states. In the Processing code, these are mapped to integer codes `1` to `4`.

| Class ID | State | Gesture Characteristics | Audiovisual Role |
| --- | --- | --- | --- |
| 1 | CALM | Slow, fluid movement with low speed, low energy, and a relatively closed hand. | Calm visuals use a slow drifting circle whose size depends on `intensity`; the audio engine plays a soft low-frequency sinusoid with gentle breathing modulation. |
| 2 | PULSE | Repetitive rhythmic movement with short cycles, medium energy, and a more pointed finger-up style. | Pulse visuals use a pulsing square whose size follows an oscillation driven by `intensity`; the audio engine plays a beat-like sinusoid with an amplitude envelope and pitch drop. |
| 3 | TENSION | Fast motion with frequent direction changes and high energy. | Tension visuals draw multiple random triangles, with the number of shapes driven by `intensity`; the audio engine switches to a layered square-wave pattern with faster note changes and rhythmic gating. |
| 4 | CLIMAX | Large, high-energy, open-hand expressive motion. | Climax visuals render a constellation of stars whose count, size, and radius depend on `intensity`; the audio engine layers six drifting sine-wave voices with amplitude and frequency modulation. |

The saved dataset schema in `current/currentData.arff` includes a `state` attribute with values `{0,1,2,3,4}`, but the renderer and the test sender operate with the project's four visible states `1` to `4`.

## 6. Model Configuration
The saved Wekinator project confirms two outputs:

- `state`: `OSCClassificationOutput` with `4` classes.
- `intensity`: `OSCNumericOutput` with real-valued output type, minimum `0.0`, maximum `1.0`, and soft limits.

The saved model files show that the state output uses a k-nearest-neighbor model builder with `numNeighbors` set to `1`, while the intensity output uses a neural-network model builder with `1` hidden layer and `NUM_FEATURES` as the hidden-layer type. The repository does not provide an additional trained-model explanation beyond these saved configuration values.

## 7. Training Strategy
Training examples were recorded from live gesture features sent by Machine 1 to Wekinator. The intended gesture patterns were:

- CALM: slow movements, fluid motion, low speed, low energy, relatively closed hand, with a target reference intensity around `0.2`.
- PULSE: repetitive movement, rhythmic motion, finger-up style gestures, short movement cycles, medium energy, with a target reference intensity around `0.5`.
- TENSION: fast movement, frequent direction changes, short movement intervals, high energy, with a target reference intensity around `0.7`.
- CLIMAX: large movements, high energy, open hand, strong expressive motion, with a target reference intensity around `1.0`.

These values should be understood as training targets or references, not as claimed learned predictions. The repository does not document the number of recordings or examples, so no dataset size is stated here.

## 8. Processing Integration
Processing receives the control stream on port `12000` and expects `/shape/control <state> <intensity>`. The `state` value selects the current mode in `drawVisualState()` and `updateAudio()`, while `intensity` continuously shapes the audiovisual response.

In the visual renderer, `intensity` controls the CALM circle size and position, the PULSE pulse speed and square size, the TENSION shape count and triangle size, and the CLIMAX star count, star size, and orbital radius. In the audio engine, `intensity` controls the CALM volume and slight frequency drift, the PULSE tempo, envelope, pitch offset, and amplitude, the TENSION step duration, periodic variation, note envelope, and amplitudes of the three voices, and the CLIMAX voice breathing, small frequency drift, and amplitude balance across the six choir voices.

## 9. Saved Model Files
The Wekinator project is stored under `ml/wekinator_project/WekinatorProject/` and includes the following main files:

- `WekinatorProject.wekproj`: the saved project metadata, including the configured OSC receive port `6448`.
- `inputConfig.xml`: the input OSC definition for `/shape/features` with `7` inputs.
- `outputConfig.xml`: the output OSC definition for `/shape/control` with `state` and `intensity`.
- `current/currentData.arff`: the saved dataset snapshot used by the project; in the inspected repository state, only the ARFF header is present.
- `current/models/model0.xml`: saved model configuration for the `state` classification output using k-nearest neighbor.
- `current/models/model1.xml`: saved model configuration for the `intensity` numeric output using a neural-network builder.

## 10. Testing and Validation
The repository includes two local OSC sender tests:

- `tests/test_feature_sender.py` sends the seven feature values to Wekinator at `/shape/features` on port `6448`.
- `tests/test_osc_sender.py` sends `/shape/control <state> <intensity>` to Processing on port `12000`.

The project documentation and test scripts indicate that the integration was also validated across two machines on the local network, with Machine 1 sending `/shape/features` to Wekinator and Processing receiving `/shape/control`.

## 11. Limitations and Future Improvements
This pipeline depends on the quality and balance of the recorded training examples, so performance can vary with performer style, speed, and spatial setup. The current project could benefit from more balanced examples across states, possible prediction smoothing, and further refinement of the intensity regression if additional training data becomes available.
