import oscP5.*;

OscP5 oscP5; // osc receiver

int currentState;
float currentIntensity;


// setez dimensiunea ferestrei
void settings(){
    size(WINDOW_WIDTH, WINDOW_HEIGHT);
}


// initializez aplicatia
void setup(){
    frameRate(TARGET_FRAME_RATE);

    // setez valorile initiale
    currentState = DEFAULT_STATE;
    currentIntensity = DEFAULT_INTENSITY;

    // pornesc receiver-ul OSC
    oscP5 = new OscP5(this, OSC_RECEIVE_PORT);

    // info pt debug
    println("Shape Orchestra Renderer started");
    println("OSC port: " + OSC_RECEIVE_PORT);
    println("OSC address: " + OSC_CONTROL_ADDRESS);
}
// bucla principala de rendering
void draw(){
    background(20);//gri inchis
    drawDebugScreen(); //afis temporar valorile primite
}

// apelata automat cand se primeste un mesaj OSC
void oscEvent(OscMessage message){
    // ignora mesajele cu alta adresa OSC
    if(!message.checkAddrPattern(OSC_CONTROL_ADDRESS)){
        if(DEBUG_OSC){
        println("Ignored message: "+message.addrPattern());
        }
        return;
    }
    //exista state si intensity?
    if(message.arguments().length<2){
        if (DEBUG_OSC) {
        println("Invalid message: 2 arguments required");
        }
        return;
    }
    // citesc starea primita
    int receivedState = round(
        message.get(0).floatValue()
    );
    // citesc intensitatea primita
    float receivedIntensity = message.get(1).floatValue();

    // limitez starea intre valorile permise si intensitatea intre 0 si 1
    receivedState = constrain(receivedState,MIN_STATE,MAX_STATE);
    receivedIntensity = constrain(receivedIntensity,MIN_INTENSITY,MAX_INTENSITY);

    // actualizez valorile rendererului
    currentState = receivedState;
    currentIntensity = receivedIntensity;

    // afisez valorile primite in consola
    if (DEBUG_OSC){
        println("State: "+ currentState+ " | Intensity: "+ nf(currentIntensity, 1, 3));
    }
}

// afiseaza temporar informatiile pt testare
void drawDebugScreen(){
    fill(255);
    textAlign(CENTER, CENTER);

    // titlul aplicatiei
    textSize(32);
    text("Shape Orchestra Renderer",width / 2,height / 2 - 120);
    // portul OSC
    textSize(24);
    text("OSC port: " + OSC_RECEIVE_PORT,width / 2,height / 2 - 50);
    // starea curenta
    text("State: "+ currentState+ " ("+ getStateName(currentState)+ ")",width / 2,height / 2);
    // intensitatea curenta
    text("Intensity: "+ nf(currentIntensity, 1, 3),width / 2,height / 2 + 50);

    // mesajul OSC asteptat
    textSize(16);
    fill(170);
    text("Waiting for "+ OSC_CONTROL_ADDRESS+ " <state> <intensity>",width / 2,height / 2 + 120);
}

//cod -> stare
String getStateName(int state){
    switch(state){
        case STATE_CALM:
        return "CALM";
        case STATE_PULSE:
        return "PULSE";
        case STATE_TENSION:
        return "TENSION";
        case STATE_CLIMAX:
        return "CLIMAX";
        default:
        return "UNKNOWN";
    }
}