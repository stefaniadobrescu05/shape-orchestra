// aleg vizualul in functie de stare
void drawVisualState(){
    switch(currentState){
        case STATE_CALM:
            drawCalm();
            break;
        case STATE_PULSE:
            drawPulse();
            break;
        case STATE_TENSION:
            drawTension();
            break;
        case STATE_CLIMAX:
            drawClimax();
            break;
        default:
            background(20);
            break;
    }
}

// CALM
void drawCalm(){
    background(15, 25, 35);
    noStroke();
    // dimensiunea cercului depinde de intensitate
    float circleSize = map(currentIntensity, 0.0, 1.0, 120, 320);
    // miscare lenta pe orizontala
    float x = width/2 + sin(frameCount*0.01)*120;
    float y = height/2 + cos(frameCount*0.008)*60;
    fill(120, 180, 220, 180);
    ellipse(x, y, circleSize, circleSize);
}


// PULSE
void drawPulse(){
    background(25, 15, 35);
    noStroke();
    // viteza pulsatiei depinde de intensitate
    float pulseSpeed = map(currentIntensity, 0.0, 1.0, 0.03, 0.15);
    // valoare oscilanta intre -1 si 1
    float pulse = sin(frameCount*pulseSpeed);
    // dimensiunea formei pulseaza
    float shapeSize = map(pulse, -1, 1, 100, 300);
    fill(220, 100, 200, 200);
    rectMode(CENTER);
    rect(width/2, height/2, shapeSize, shapeSize);
}

// TENSION
void drawTension(){
    background(35, 15, 20);
    noFill();
    stroke(255, 90, 90);
    // nr de forme depinde de intensitate
    int shapeCount = int(map(currentIntensity, 0.0, 1.0, 4, 20));

    for (int i = 0; i < shapeCount; i++){
        float x = random(width);
        float y = random(height);
        float shapeSize = random(30, 120);
        triangle(x, y-shapeSize, x-shapeSize, y+shapeSize, x+shapeSize, y+shapeSize);
    }
}

// steluta
void drawStar(float x, float y, float size){
    pushMatrix();
    translate(x, y);
    beginShape();
    for (int i=0; i < 10; i++){
        float angle = i*PI/5.0;
        float r;
        if (i%2 == 0){
            r=size;
        }else{
            r=size * 0.45;
        }
        float sx=cos(angle - HALF_PI)*r;
        float sy=sin(angle - HALF_PI)*r;
        vertex(sx, sy);
    }
    endShape(CLOSE);
    popMatrix();
}
// CLIMAX
void drawClimax(){
    background(10);
    noStroke();
    fill(255, 220, 60); // galben

    // cu cat creste intensitatea, cu atat sunt mai multe stelute
    int starCount = int(map(currentIntensity, 0.0, 1.0, 6, 30));
    // marimea stelutelor
    float starSize = map(currentIntensity, 0.0, 1.0, 12, 28);

    for (int i=0; i < starCount; i++){
        // unghi diferit pentru fiecare steluta
        float angle = TWO_PI / starCount * i;
        // miscarea inainte-inapoi
        float radius = map(sin(frameCount * 0.03 + i),-1,1,80,width * 0.45);
        // pozitia stelutei
        float x=width/2 + cos(angle)*radius;
        float y=height/2 + sin(angle)*radius;
        drawStar(x, y, starSize);
    }
}