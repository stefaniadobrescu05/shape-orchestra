void drawVisualState(){ // Choose which visual scene to draw for the current state.
    switch(currentState){ // Branch based on the latest state received from Wekinator.
        case STATE_CALM: // State 1 means calm.
            drawCalm(); // Draw the calm circle scene.
            break; // Stop this switch case.
        case STATE_PULSE: // State 2 means pulse.
            drawPulse(); // Draw the pulsing square scene.
            break; // Stop this switch case.
        case STATE_TENSION: // State 3 means tension.
            drawTension(); // Draw the random triangle scene.
            break; // Stop this switch case.
        case STATE_CLIMAX: // State 4 means climax.
            drawClimax(); // Draw the orbiting star scene.
            break; // Stop this switch case.
        default: // If the state is unknown.
            background(20); // Draw a neutral dark background.
            break; // Stop this switch case.
    }
}


void drawCalm(){ // Draw the calm visual state.
    background(15, 25, 35); // Clear the screen with a dark blue background.
    noStroke(); // Draw shapes without outlines.
    float circleSize = map(currentIntensity, 0.0, 1.0, 120, 320); // Make the circle bigger as intensity rises.
    float x = width / 2 + sin(frameCount * 0.01) * 120; // Move the circle slowly left and right.
    float y = height / 2 + cos(frameCount * 0.008) * 60; // Move the circle slowly up and down.
    fill(120, 180, 220, 180); // Use a soft translucent blue fill.
    ellipse(x, y, circleSize, circleSize); // Draw the calm circle.
}


void drawPulse(){ // Draw the pulse visual state.
    background(25, 15, 35); // Clear the screen with a dark purple background.
    noStroke(); // Draw the square without an outline.
    float pulseSpeed = map(currentIntensity, 0.0, 1.0, 0.03, 0.15); // Increase pulse speed with intensity.
    float pulse = sin(frameCount * pulseSpeed); // Create an oscillating value between -1 and 1.
    float shapeSize = map(pulse, -1, 1, 100, 300); // Convert the pulse wave into square size.
    fill(220, 100, 200, 200); // Use a bright translucent pink fill.
    rectMode(CENTER); // Draw rectangles from their center point.
    rect(width / 2, height / 2, shapeSize, shapeSize); // Draw the pulsing square in the center.
}


void drawTension(){ // Draw the tension visual state.
    background(35, 15, 20); // Clear the screen with a dark red background.
    noFill(); // Draw triangles as outlines only.
    stroke(255, 90, 90); // Use a bright red outline.
    int shapeCount = int(map(currentIntensity, 0.0, 1.0, 4, 20)); // Draw more triangles when intensity rises.

    for(int i = 0; i < shapeCount; i++){ // Repeat once for each triangle.
        float x = random(width); // Choose a random horizontal position.
        float y = random(height); // Choose a random vertical position.
        float shapeSize = random(30, 120); // Choose a random triangle size.
        triangle(x, y - shapeSize, x - shapeSize, y + shapeSize, x + shapeSize, y + shapeSize); // Draw one triangle.
    }
}


void drawStar(float x, float y, float size){ // Draw one star centered at x/y.
    pushMatrix(); // Save the current drawing transform.
    translate(x, y); // Move the drawing origin to the star center.
    beginShape(); // Start building a custom polygon.
    for(int i = 0; i < 10; i++){ // Use 10 points alternating outer and inner radius.
        float angle = i * PI / 5.0; // Calculate the angle for this star point.
        float r; // Store the radius for this point.
        if(i % 2 == 0){ // Even points are outer star tips.
            r = size; // Use the full radius for outer tips.
        }else{ // Odd points are inner valleys.
            r = size * 0.45; // Use a smaller radius for inner valleys.
        }
        float sx = cos(angle - HALF_PI) * r; // Convert angle/radius into x position.
        float sy = sin(angle - HALF_PI) * r; // Convert angle/radius into y position.
        vertex(sx, sy); // Add this point to the star polygon.
    }
    endShape(CLOSE); // Close and draw the star polygon.
    popMatrix(); // Restore the previous drawing transform.
}


void drawClimax(){ // Draw the climax visual state.
    background(10); // Clear the screen with an almost-black background.
    noStroke(); // Draw stars without outlines.
    fill(255, 220, 60); // Use a yellow star color.

    int starCount = int(map(currentIntensity, 0.0, 1.0, 6, 30)); // Draw more stars at higher intensity.
    float starSize = map(currentIntensity, 0.0, 1.0, 12, 28); // Make stars bigger at higher intensity.

    for(int i = 0; i < starCount; i++){ // Repeat once for each star.
        float angle = TWO_PI / starCount * i; // Spread the stars evenly around a circle.
        float radius = map(sin(frameCount * 0.03 + i), -1, 1, 80, width * 0.45); // Move each star in and out.
        float x = width / 2 + cos(angle) * radius; // Calculate the star's horizontal position.
        float y = height / 2 + sin(angle) * radius; // Calculate the star's vertical position.
        drawStar(x, y, starSize); // Draw the star at the calculated position.
    }
}
