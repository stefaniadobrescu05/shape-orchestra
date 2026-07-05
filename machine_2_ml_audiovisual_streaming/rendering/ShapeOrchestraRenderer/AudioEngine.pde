import processing.sound.*;

SinOsc calm;
SinOsc pulse;
SqrOsc tension1;
SqrOsc tension2;
SqrOsc tension3;
SinOsc choir1;
SinOsc choir2;
SinOsc choir3;
SinOsc choir4;
SinOsc choir5;
SinOsc choir6;

boolean audioInitialized = false;
int lastAudioState = -1;

void setupAudio(){
    // calm
    calm = new SinOsc(this);
    calm.freq(130.81);   // C3
    calm.amp(0);
    calm.play();
    // pulse
    pulse = new SinOsc(this);
    pulse.freq(72.0);
    pulse.amp(0);
    pulse.play();
    // tension
    tension1 = new SqrOsc(this);
    tension2 = new SqrOsc(this);
    tension3 = new SqrOsc(this);
    tension1.freq(110.0);
    tension2.freq(165.0);
    tension3.freq(220.0);
    tension1.amp(0);
    tension2.amp(0);
    tension3.amp(0);
    tension1.play();
    tension2.play();
    tension3.play();
    // climax
    choir1 = new SinOsc(this);
    choir2 = new SinOsc(this);
    choir3 = new SinOsc(this);
    choir4 = new SinOsc(this);
    choir5 = new SinOsc(this);
    choir6 = new SinOsc(this);

    choir1.freq(174.61);   // F3
    choir2.freq(261.63);   // C4
    choir3.freq(349.23);   // F4
    choir4.freq(440.00);   // A4
    choir5.freq(523.25);   // C5
    choir6.freq(659.25);   // E5
    choir1.amp(0);
    choir2.amp(0);
    choir3.amp(0);
    choir4.amp(0);
    choir5.amp(0);
    choir6.amp(0);
    choir1.play();
    choir2.play();
    choir3.play();
    choir4.play();
    choir5.play();
    choir6.play();

    audioInitialized = true;

    println("Audio engine initialized");
}

void updateAudio(int state, float intensity){
    if (!audioInitialized){
        return;
    }
    intensity = constrain(intensity, MIN_INTENSITY, MAX_INTENSITY);
        // totul pe mut
    calm.amp(0);
    pulse.amp(0);
    tension1.amp(0);
    tension2.amp(0);
    tension3.amp(0);
    choir1.amp(0);
    choir2.amp(0);
    choir3.amp(0);
    choir4.amp(0);
    choir5.amp(0);
    choir6.amp(0);

    // schimbare de stare
    if (state != lastAudioState){
        if (DEBUG_OSC) {
        println("Audio state changed: "+ lastAudioState+ " -> "+ state);
        }
        lastAudioState = state;
    }
    // aleg audio in functie de stare
    switch(state){
        case STATE_CALM:
            updateCalmAudio(intensity);
            break;
        case STATE_PULSE:
            updatePulseAudio(intensity);
            break;
        case STATE_TENSION:
            updateTensionAudio(intensity);
            break;
        case STATE_CLIMAX:
            updateClimaxAudio(intensity);
            break;
    }
}

// calm
void updateCalmAudio(float intensity) {
  float breathing = 0.80 + 0.20*sin(millis()*0.0008);
  // frecventa joasa si placuta
  float calmFrequency = 130.81 +2.0*sin(millis()*0.0005);
  calm.freq(calmFrequency);
  // volum
    float master =map(intensity, 0, 1, 0.06, 0.18);
  calm.amp(master*breathing);
}
// pulse
void updatePulseAudio(float intensity) {
    float bpm =map(intensity, 0, 1, 60, 120);
    float beatDurationMs =60000.0/bpm;
    float beatPhase =(millis() % beatDurationMs)/beatDurationMs;
    float envelope =exp(-beatPhase*14.0);
    float baseFrequency =map(intensity, 0, 1, 68, 82);
     float pitchDrop =18.0*exp(-beatPhase*18.0); // incepe putin mai sus si coboara
    pulse.freq(baseFrequency+pitchDrop);
    float master =map(intensity, 0, 1, 0.16, 0.40);
    pulse.amp(envelope*master);
}
// tension
void updateTensionAudio(float intensity){
    // intensitate mica->note mai lente
    // intensitate mare->note mai rapide
    float stepDurationMs =map(intensity,0,1,700,120);
    int step=int(millis()/stepDurationMs);// nr pasului curent
    // arpegiu 8bit
    float[] notes = {110.00, 130.81, 146.83, 155.56, 196.00, 207.65, 146.83, 130.81};
    int noteIndex = step % notes.length;
    float currentNote = notes[noteIndex];

    float tensionPeriodMs = map(intensity, 0, 1, 5000, 900);
    float phase = TWO_PI * (millis() % tensionPeriodMs) / tensionPeriodMs;
    float periodicWave = 0.5 + 0.5 * sin(phase);

    periodicWave = pow(periodicWave, 1.6);

    tension1.freq(currentNote);

    tension2.freq(currentNote * 2.0);

    tension3.freq(currentNote * 1.50);

    float localStepPhase = (millis() % stepDurationMs) / stepDurationMs;

    float noteEnvelope = exp(-localStepPhase * 4.5);

    float master = map(intensity, 0, 1, 0.035, 0.11);

    tension1.amp(master * noteEnvelope * (0.35 + 0.65 * periodicWave));
    tension2.amp(master * noteEnvelope * 0.38);
    tension3.amp(master * noteEnvelope * (0.15 + 0.35 * periodicWave));
}

// climax
void updateClimaxAudio(float intensity){

  float breath1 = 0.82 + 0.18 * sin(millis() * 0.0010);
  float breath2 = 0.84 + 0.16 * sin(millis() * 0.0013 + 0.7);
  float breath3 = 0.80 + 0.20 * sin(millis() * 0.0017 + 1.4);
  float breath4 = 0.85 + 0.15 * sin(millis() * 0.0011 + 2.1);
  float breath5 = 0.84 + 0.16 * sin(millis() * 0.0015 + 2.8);
  float breath6 = 0.86 + 0.14 * sin(millis() * 0.0019 + 3.5);

  choir1.freq(174.61 + 0.25 * sin(millis() * 0.0008));
  choir2.freq(261.63 + 0.40 * sin(millis() * 0.0010));
  choir3.freq(349.23 + 0.55 * sin(millis() * 0.0012));
  choir4.freq(440.00 + 0.70 * sin(millis() * 0.0009));
  choir5.freq(523.25 + 0.85 * sin(millis() * 0.0011));
  choir6.freq(659.25 + 1.00 * sin(millis() * 0.0013));

  float master = map(intensity, 0, 1, 0.045, 0.125);
  choir1.amp(master * 0.48 * breath1);
  choir2.amp(master * 0.62 * breath2);
  choir3.amp(master * 0.72 * breath3);
  choir4.amp(master * 0.66 * breath4);
  choir5.amp(master * 0.48 * breath5);
  choir6.amp(master * 0.25 * breath6);
}
// cleanup audio engine
void stopAudio(){
  if (!audioInitialized) {
    return;
  }
  calm.stop();
  pulse.stop();
  tension1.stop();
  tension2.stop();
  tension3.stop();
  choir1.stop();
  choir2.stop();
  choir3.stop();
  choir4.stop();
  choir5.stop();
  choir6.stop();
}