final int OSC_RECEIVE_PORT = 12000; // Listen on this UDP port for OSC messages from Wekinator.
final String OSC_CONTROL_ADDRESS = "/shape/control"; // Accept only OSC messages with this address.
final int WINDOW_WIDTH = 1280; // Set the Processing window width in pixels.
final int WINDOW_HEIGHT = 720; // Set the Processing window height in pixels.
final int TARGET_FRAME_RATE = 60; // Ask Processing to draw 60 frames per second.

final int STATE_CALM = 1; // Numeric code for the calm visual/audio state.
final int STATE_PULSE = 2; // Numeric code for the pulse visual/audio state.
final int STATE_TENSION = 3; // Numeric code for the tension visual/audio state.
final int STATE_CLIMAX = 4; // Numeric code for the climax visual/audio state.

final int DEFAULT_STATE = STATE_CALM; // Start in the calm state before OSC messages arrive.
final float DEFAULT_INTENSITY = 0.2; // Start with a low intensity before OSC messages arrive.

final float MIN_INTENSITY = 0.0; // Lowest allowed intensity value.
final float MAX_INTENSITY = 1.0; // Highest allowed intensity value.
final int MIN_STATE = STATE_CALM; // Lowest valid state number.
final int MAX_STATE = STATE_CLIMAX; // Highest valid state number.

final boolean DEBUG_OSC = true; // Print useful OSC/audio messages to the console when true.
