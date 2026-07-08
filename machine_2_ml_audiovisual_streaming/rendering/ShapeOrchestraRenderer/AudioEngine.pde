import processing.sound.*; // Import Processing Sound oscillator classes.

SinOsc calm; // Sine oscillator used for the calm state.
SinOsc pulse; // Sine oscillator used for the pulse state.
SqrOsc tension1; // First square oscillator used for the tension state.
SqrOsc tension2; // Second square oscillator used for the tension state.
SqrOsc tension3; // Third square oscillator used for the tension state.
SinOsc choir1; // First sine oscillator used for the climax chord.
SinOsc choir2; // Second sine oscillator used for the climax chord.
SinOsc choir3; // Third sine oscillator used for the climax chord.
SinOsc choir4; // Fourth sine oscillator used for the climax chord.
SinOsc choir5; // Fifth sine oscillator used for the climax chord.
SinOsc choir6; // Sixth sine oscillator used for the climax chord.

boolean audioInitialized = false; // Track whether setupAudio() has created the oscillators.
int lastAudioState = -1; // Remember the last state so state changes can be logged once.


void setupAudio(){ // Create every oscillator and start it muted.
    calm = new SinOsc(this); // Create the calm sine oscillator.
    calm.freq(130.81); // Set calm to C3.
    calm.amp(0); // Start calm muted.
    calm.play(); // Start the oscillator so volume changes can be heard later.

    pulse = new SinOsc(this); // Create the pulse sine oscillator.
    pulse.freq(72.0); // Set a low starting pulse frequency.
    pulse.amp(0); // Start pulse muted.
    pulse.play(); // Start the oscillator so volume changes can be heard later.

    tension1 = new SqrOsc(this); // Create the first tension square oscillator.
    tension2 = new SqrOsc(this); // Create the second tension square oscillator.
    tension3 = new SqrOsc(this); // Create the third tension square oscillator.
    tension1.freq(110.0); // Set the first starting tension frequency.
    tension2.freq(165.0); // Set the second starting tension frequency.
    tension3.freq(220.0); // Set the third starting tension frequency.
    tension1.amp(0); // Start the first tension oscillator muted.
    tension2.amp(0); // Start the second tension oscillator muted.
    tension3.amp(0); // Start the third tension oscillator muted.
    tension1.play(); // Start the first tension oscillator.
    tension2.play(); // Start the second tension oscillator.
    tension3.play(); // Start the third tension oscillator.

    choir1 = new SinOsc(this); // Create the first climax sine oscillator.
    choir2 = new SinOsc(this); // Create the second climax sine oscillator.
    choir3 = new SinOsc(this); // Create the third climax sine oscillator.
    choir4 = new SinOsc(this); // Create the fourth climax sine oscillator.
    choir5 = new SinOsc(this); // Create the fifth climax sine oscillator.
    choir6 = new SinOsc(this); // Create the sixth climax sine oscillator.

    choir1.freq(174.61); // Set choir voice 1 to F3.
    choir2.freq(261.63); // Set choir voice 2 to C4.
    choir3.freq(349.23); // Set choir voice 3 to F4.
    choir4.freq(440.00); // Set choir voice 4 to A4.
    choir5.freq(523.25); // Set choir voice 5 to C5.
    choir6.freq(659.25); // Set choir voice 6 to E5.
    choir1.amp(0); // Start choir voice 1 muted.
    choir2.amp(0); // Start choir voice 2 muted.
    choir3.amp(0); // Start choir voice 3 muted.
    choir4.amp(0); // Start choir voice 4 muted.
    choir5.amp(0); // Start choir voice 5 muted.
    choir6.amp(0); // Start choir voice 6 muted.
    choir1.play(); // Start choir voice 1.
    choir2.play(); // Start choir voice 2.
    choir3.play(); // Start choir voice 3.
    choir4.play(); // Start choir voice 4.
    choir5.play(); // Start choir voice 5.
    choir6.play(); // Start choir voice 6.

    audioInitialized = true; // Mark the audio engine as ready.

    println("Audio engine initialized"); // Confirm audio setup in the console.
}


void updateAudio(int state, float intensity){ // Update audio every frame from the current state/intensity.
    if(!audioInitialized){ // Avoid touching oscillators before setupAudio() has run.
        return; // Leave early if audio is not ready.
    }
    intensity = constrain(intensity, MIN_INTENSITY, MAX_INTENSITY); // Keep intensity inside 0..1.

    calm.amp(0); // Mute calm before enabling the selected state.
    pulse.amp(0); // Mute pulse before enabling the selected state.
    tension1.amp(0); // Mute tension voice 1 before enabling the selected state.
    tension2.amp(0); // Mute tension voice 2 before enabling the selected state.
    tension3.amp(0); // Mute tension voice 3 before enabling the selected state.
    choir1.amp(0); // Mute choir voice 1 before enabling the selected state.
    choir2.amp(0); // Mute choir voice 2 before enabling the selected state.
    choir3.amp(0); // Mute choir voice 3 before enabling the selected state.
    choir4.amp(0); // Mute choir voice 4 before enabling the selected state.
    choir5.amp(0); // Mute choir voice 5 before enabling the selected state.
    choir6.amp(0); // Mute choir voice 6 before enabling the selected state.

    if(state != lastAudioState){ // Detect when Wekinator changes to a different state.
        if(DEBUG_OSC){ // Print state changes only when debug logging is enabled.
            println("Audio state changed: " + lastAudioState + " -> " + state); // Show old and new audio state.
        }
        lastAudioState = state; // Save the new state so this message does not repeat every frame.
    }

    switch(state){ // Choose the audio behavior for the current state.
        case STATE_CALM: // If the state is calm.
            updateCalmAudio(intensity); // Update calm audio.
            break; // Stop this switch case.
        case STATE_PULSE: // If the state is pulse.
            updatePulseAudio(intensity); // Update pulse audio.
            break; // Stop this switch case.
        case STATE_TENSION: // If the state is tension.
            updateTensionAudio(intensity); // Update tension audio.
            break; // Stop this switch case.
        case STATE_CLIMAX: // If the state is climax.
            updateClimaxAudio(intensity); // Update climax audio.
            break; // Stop this switch case.
    }
}


void updateCalmAudio(float intensity){ // Shape the calm sound.
    float breathing = 0.80 + 0.20 * sin(millis() * 0.0008); // Slowly move volume up and down.
    float calmFrequency = 130.81 + 2.0 * sin(millis() * 0.0005); // Slightly wobble the C3 pitch.
    calm.freq(calmFrequency); // Apply the current calm pitch.
    float master = map(intensity, 0, 1, 0.06, 0.18); // Convert intensity into calm volume range.
    calm.amp(master * breathing); // Apply volume with the breathing movement.
}


void updatePulseAudio(float intensity){ // Shape the pulse sound.
    float bpm = map(intensity, 0, 1, 60, 120); // Convert intensity into beats per minute.
    float beatDurationMs = 60000.0 / bpm; // Convert BPM into milliseconds per beat.
    float beatPhase = (millis() % beatDurationMs) / beatDurationMs; // Find position inside the current beat.
    float envelope = exp(-beatPhase * 14.0); // Make the beat loud at the start and quickly fade.
    float baseFrequency = map(intensity, 0, 1, 68, 82); // Raise the base pitch as intensity increases.
    float pitchDrop = 18.0 * exp(-beatPhase * 18.0); // Start each beat higher and drop down quickly.
    pulse.freq(baseFrequency + pitchDrop); // Apply the moving pulse pitch.
    float master = map(intensity, 0, 1, 0.16, 0.40); // Convert intensity into pulse volume range.
    pulse.amp(envelope * master); // Apply the fading beat envelope.
}


void updateTensionAudio(float intensity){ // Shape the tension sound.
    float stepDurationMs = map(intensity, 0, 1, 700, 120); // Make note changes faster at high intensity.
    int step = int(millis() / stepDurationMs); // Count which arpeggio step is currently active.
    float[] notes = {110.00, 130.81, 146.83, 155.56, 196.00, 207.65, 146.83, 130.81}; // Store the arpeggio notes.
    int noteIndex = step % notes.length; // Wrap the step number around the note list.
    float currentNote = notes[noteIndex]; // Pick the current arpeggio note.

    float tensionPeriodMs = map(intensity, 0, 1, 5000, 900); // Make the larger volume wave faster at high intensity.
    float phase = TWO_PI * (millis() % tensionPeriodMs) / tensionPeriodMs; // Find position inside that wave.
    float periodicWave = 0.5 + 0.5 * sin(phase); // Convert the sine wave from -1..1 into 0..1.

    periodicWave = pow(periodicWave, 1.6); // Sharpen the wave so peaks feel more tense.

    tension1.freq(currentNote); // Set voice 1 to the current note.
    tension2.freq(currentNote * 2.0); // Set voice 2 one octave above the current note.
    tension3.freq(currentNote * 1.50); // Set voice 3 a fifth above the current note.

    float localStepPhase = (millis() % stepDurationMs) / stepDurationMs; // Find position inside this arpeggio step.
    float noteEnvelope = exp(-localStepPhase * 4.5); // Make each note attack then fade.
    float master = map(intensity, 0, 1, 0.035, 0.11); // Convert intensity into tension volume range.

    tension1.amp(master * noteEnvelope * (0.35 + 0.65 * periodicWave)); // Apply main tension voice volume.
    tension2.amp(master * noteEnvelope * 0.38); // Apply quieter octave voice volume.
    tension3.amp(master * noteEnvelope * (0.15 + 0.35 * periodicWave)); // Apply moving fifth voice volume.
}


void updateClimaxAudio(float intensity){ // Shape the climax chord sound.
    float breath1 = 0.82 + 0.18 * sin(millis() * 0.0010); // Give voice 1 a slow volume movement.
    float breath2 = 0.84 + 0.16 * sin(millis() * 0.0013 + 0.7); // Give voice 2 a different movement.
    float breath3 = 0.80 + 0.20 * sin(millis() * 0.0017 + 1.4); // Give voice 3 a different movement.
    float breath4 = 0.85 + 0.15 * sin(millis() * 0.0011 + 2.1); // Give voice 4 a different movement.
    float breath5 = 0.84 + 0.16 * sin(millis() * 0.0015 + 2.8); // Give voice 5 a different movement.
    float breath6 = 0.86 + 0.14 * sin(millis() * 0.0019 + 3.5); // Give voice 6 a different movement.

    choir1.freq(174.61 + 0.25 * sin(millis() * 0.0008)); // Slightly detune choir voice 1.
    choir2.freq(261.63 + 0.40 * sin(millis() * 0.0010)); // Slightly detune choir voice 2.
    choir3.freq(349.23 + 0.55 * sin(millis() * 0.0012)); // Slightly detune choir voice 3.
    choir4.freq(440.00 + 0.70 * sin(millis() * 0.0009)); // Slightly detune choir voice 4.
    choir5.freq(523.25 + 0.85 * sin(millis() * 0.0011)); // Slightly detune choir voice 5.
    choir6.freq(659.25 + 1.00 * sin(millis() * 0.0013)); // Slightly detune choir voice 6.

    float master = map(intensity, 0, 1, 0.045, 0.125); // Convert intensity into climax volume range.
    choir1.amp(master * 0.48 * breath1); // Apply volume to choir voice 1.
    choir2.amp(master * 0.62 * breath2); // Apply volume to choir voice 2.
    choir3.amp(master * 0.72 * breath3); // Apply volume to choir voice 3.
    choir4.amp(master * 0.66 * breath4); // Apply volume to choir voice 4.
    choir5.amp(master * 0.48 * breath5); // Apply volume to choir voice 5.
    choir6.amp(master * 0.25 * breath6); // Apply volume to choir voice 6.
}


void stopAudio(){ // Stop all oscillators when the audio engine is being cleaned up.
    if(!audioInitialized){ // If setupAudio() never finished, there is nothing to stop.
        return; // Leave safely.
    }
    calm.stop(); // Stop the calm oscillator.
    pulse.stop(); // Stop the pulse oscillator.
    tension1.stop(); // Stop tension voice 1.
    tension2.stop(); // Stop tension voice 2.
    tension3.stop(); // Stop tension voice 3.
    choir1.stop(); // Stop choir voice 1.
    choir2.stop(); // Stop choir voice 2.
    choir3.stop(); // Stop choir voice 3.
    choir4.stop(); // Stop choir voice 4.
    choir5.stop(); // Stop choir voice 5.
    choir6.stop(); // Stop choir voice 6.
}
