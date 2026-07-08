import oscP5.*; // Import the oscP5 library so Processing can receive OSC messages.
import processing.sound.*; // Import Processing Sound so the sketch can generate audio.

OscP5 oscP5; // Store the OSC receiver object.

int currentState; // Store the visual/audio state currently selected by Wekinator.
float currentIntensity; // Store the current intensity value from Wekinator.


void settings(){ // Processing calls settings() before setup() to configure the sketch.
    size(WINDOW_WIDTH, WINDOW_HEIGHT); // Create the renderer window using the configured dimensions.
}


void setup(){ // Processing calls setup() once when the sketch starts.
    frameRate(TARGET_FRAME_RATE); // Set the requested animation speed.

    currentState = DEFAULT_STATE; // Use a safe starting state until OSC data arrives.
    currentIntensity = DEFAULT_INTENSITY; // Use a safe starting intensity until OSC data arrives.

    oscP5 = new OscP5(this, OSC_RECEIVE_PORT); // Start listening for OSC messages on the configured UDP port.

    setupAudio(); // Create and start the audio oscillators at zero volume.

    println("Shape Orchestra Renderer started"); // Confirm in the console that Processing started.
    println("OSC port: " + OSC_RECEIVE_PORT); // Show which UDP port is being listened to.
    println("OSC address: " + OSC_CONTROL_ADDRESS); // Show which OSC address is expected.
}


void draw(){ // Processing calls draw() repeatedly to animate the sketch.
    drawVisualState(); // Draw the visuals for the current state and intensity.
    updateAudio(currentState, currentIntensity); // Update the sound to match the current state and intensity.
}


void oscEvent(OscMessage message){ // oscP5 calls this automatically whenever an OSC message arrives.
    if(!message.checkAddrPattern(OSC_CONTROL_ADDRESS)){ // Ignore messages that are not /shape/control.
        if(DEBUG_OSC){ // Only print ignored messages when debug logging is enabled.
            println("Ignored message: " + message.addrPattern()); // Show the unexpected OSC address.
        }
        return; // Stop processing this message.
    }

    if(message.arguments().length < 2){ // Require both state and intensity values.
        if(DEBUG_OSC){ // Only print invalid-message info when debug logging is enabled.
            println("Invalid message: 2 arguments required"); // Explain that the OSC packet was incomplete.
        }
        return; // Stop processing this incomplete message.
    }

    int receivedState = round( // Convert Wekinator's first value into an integer state.
        message.get(0).floatValue() // Read argument 0 as a float before rounding.
    );
    float receivedIntensity = message.get(1).floatValue(); // Read argument 1 as the intensity value.

    receivedState = constrain(receivedState, MIN_STATE, MAX_STATE); // Keep the state inside the valid range.
    receivedIntensity = constrain(receivedIntensity, MIN_INTENSITY, MAX_INTENSITY); // Keep intensity between 0 and 1.

    currentState = receivedState; // Store the received state for the next draw() call.
    currentIntensity = receivedIntensity; // Store the received intensity for visuals and audio.

    if(DEBUG_OSC){ // Print received data only when debug logging is enabled.
        println("State: " + currentState + " | Intensity: " + nf(currentIntensity, 1, 3)); // Show latest values.
    }
}


void drawDebugScreen(){ // Draw a simple text screen that is useful while testing OSC input.
    fill(255); // Use white text for the main debug information.
    textAlign(CENTER, CENTER); // Center each debug text line around its x/y position.

    textSize(32); // Use a large font for the title.
    text("Shape Orchestra Renderer", width / 2, height / 2 - 120); // Draw the sketch title.
    textSize(24); // Use a medium font for values.
    text("OSC port: " + OSC_RECEIVE_PORT, width / 2, height / 2 - 50); // Draw the OSC receive port.
    text("State: " + currentState + " (" + getStateName(currentState) + ")", width / 2, height / 2); // Draw state.
    text("Intensity: " + nf(currentIntensity, 1, 3), width / 2, height / 2 + 50); // Draw formatted intensity.

    textSize(16); // Use a smaller font for the help line.
    fill(170); // Use gray text for secondary debug information.
    text("Waiting for " + OSC_CONTROL_ADDRESS + " <state> <intensity>", width / 2, height / 2 + 120); // Draw expected OSC format.
}


String getStateName(int state){ // Convert a numeric state code into a readable name.
    switch(state){ // Choose a name based on the state number.
        case STATE_CALM: // If the state is 1.
            return "CALM"; // Return the calm label.
        case STATE_PULSE: // If the state is 2.
            return "PULSE"; // Return the pulse label.
        case STATE_TENSION: // If the state is 3.
            return "TENSION"; // Return the tension label.
        case STATE_CLIMAX: // If the state is 4.
            return "CLIMAX"; // Return the climax label.
        default: // If the state is outside the known values.
            return "UNKNOWN"; // Return a fallback label.
    }
}
