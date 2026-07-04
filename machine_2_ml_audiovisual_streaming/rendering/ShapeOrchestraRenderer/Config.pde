final int OSC_RECEIVE_PORT = 12000; // portul pe care se asteapta mesajele OSC de la Wekinator
final String OSC_CONTROL_ADDRESS = "/shape/control";// adresa OSC pentru mesajele de control(stare si intensitate)
final int WINDOW_WIDTH = 1280; // latimea ferestrei de rendering
final int WINDOW_HEIGHT = 720; // inaltimea ferestrei de rendering
final int TARGET_FRAME_RATE = 60;// nr de cadre/sec
// stari
final int STATE_CALM = 1; // codul pt starea calm
final int STATE_PULSE = 2; // codul pt starea pulse
final int STATE_TENSION = 3; // codul pt starea tension
final int STATE_CLIMAX = 4; // codul pt starea climax
// setari initiale folosite de renderer
final int DEFAULT_STATE = STATE_CALM;
final float DEFAULT_INTENSITY = 0.2;

final float MIN_INTENSITY = 0.0;
final float MAX_INTENSITY = 1.0;
final int MIN_STATE = STATE_CALM;
final int MAX_STATE = STATE_CLIMAX;
// setari pentru debug
final boolean DEBUG_OSC = true;