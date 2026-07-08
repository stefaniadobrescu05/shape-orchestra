"""Run the Machine 1 webcam, feature extraction, and OSC transmission."""

# Import OpenCV for webcam capture, drawing text, and showing the preview window.
import cv2
# Import MediaPipe's drawing helpers so the detected hand skeleton can be shown.
import mediapipe.python.solutions.drawing_utils as mp_draw
# Import MediaPipe Hands so the webcam image can be converted into hand landmarks.
import mediapipe.python.solutions.hands as mp_hands

# Import all configuration values used by the live sensing program.
from config import (
    CAMERA_INDEX,  # Which webcam OpenCV should open.
    FEATURE_DEAD_BANDS,  # Minimum value changes before output updates.
    MACHINE_2_IP,  # IP address where Wekinator is running.
    MIN_DETECTION_CONFIDENCE,  # Minimum confidence for detecting a hand.
    MIN_TRACKING_CONFIDENCE,  # Minimum confidence for tracking an already-detected hand.
    MOVEMENT_DEAD_ZONE,  # Minimum wrist movement before motion is counted.
    OSC_FEATURE_ADDRESS,  # OSC address for feature messages.
    OSC_PORT,  # UDP port where Wekinator receives feature messages.
    SEND_EVERY_N_FRAMES,  # How often to send feature packets.
    SMOOTHING_FACTOR,  # How much smoothing to apply to feature values.
    validate_config,  # Function that checks whether the config values are valid.
)
# Import the class that turns landmarks into features and the class that smooths them.
from feature_extractor import FeatureSmoother, HandFeatureExtractor
# Import the class that sends the feature dictionary over OSC/UDP.
from osc_sender import OscFeatureSender


# Name displayed at the top of the OpenCV preview window.
WINDOW_TITLE = "Shape Orchestra - Machine 1"
# Bright green text color in BGR order, because OpenCV uses blue/green/red.
TEXT_COLOR = (0, 255, 0)
# Black outline color behind the green text so the overlay stays readable.
TEXT_OUTLINE_COLOR = (0, 0, 0)


def draw_text(frame, text, position):
    """Draw readable text with a black outline on the webcam frame."""
    font = cv2.FONT_HERSHEY_SIMPLEX  # Choose OpenCV's simple built-in font.
    cv2.putText(  # Draw a thick black version first to act as an outline.
        frame,  # Draw directly onto the current webcam frame.
        text,  # Use the text passed by the caller.
        position,  # Place the text at the requested pixel coordinates.
        font,  # Use the font selected above.
        0.62,  # Set text size.
        TEXT_OUTLINE_COLOR,  # Use black for the outline.
        4,  # Make the outline thick.
        cv2.LINE_AA,  # Use anti-aliased edges for smoother text.
    )
    cv2.putText(  # Draw the readable green text on top of the outline.
        frame,  # Draw onto the same webcam frame.
        text,  # Use the same text again.
        position,  # Use the same position again.
        font,  # Use the same font again.
        0.62,  # Use the same text size again.
        TEXT_COLOR,  # Use bright green for the foreground.
        1,  # Make the foreground thinner than the outline.
        cv2.LINE_AA,  # Keep edges smooth.
    )


def draw_feature_overlay(frame, features, packet_sent):
    """Display the live values that are being prepared for Machine 2."""
    rows = (  # Prepare one overlay row for each important live value.
        f"Position: ({features['x']:.3f}, {features['y']:.3f})",  # Show wrist x/y position.
        f"Speed: {features['speed']:.4f}",  # Show movement speed.
        (
            "Direction: "
            f"({features['direction_x']:.4f}, {features['direction_y']:.4f})"
        ),  # Show horizontal and vertical movement.
        f"Openness: {features['openness']:.3f}",  # Show how open the hand is.
        f"Energy: {features['energy']:.4f}",  # Show speed multiplied by openness.
        "OSC: sent" if packet_sent else "OSC: waiting for send interval",  # Show whether this frame sent UDP.
    )

    for row_index, row in enumerate(rows):  # Draw each overlay row with its row number.
        draw_text(frame, row, (20, 35 + row_index * 28))  # Place rows evenly down the left side.


def main():
    """Capture the hand, extract features, and stream them to Machine 2."""
    validate_config()  # Fail early if a config value is impossible or malformed.

    feature_extractor = HandFeatureExtractor(MOVEMENT_DEAD_ZONE)  # Create the landmark-to-feature converter.
    feature_smoother = FeatureSmoother(  # Create the smoother that reduces jitter.
        SMOOTHING_FACTOR,  # Pass the smoothing strength.
        FEATURE_DEAD_BANDS,  # Pass the minimum-change thresholds.
    )
    osc_sender = OscFeatureSender(  # Create the OSC/UDP sender.
        MACHINE_2_IP,  # Send packets to Machine 2.
        OSC_PORT,  # Use Wekinator's OSC input port.
        OSC_FEATURE_ADDRESS,  # Use the agreed OSC feature address.
    )

    camera = cv2.VideoCapture(CAMERA_INDEX)  # Open the selected webcam.
    if not camera.isOpened():  # Check whether OpenCV successfully opened the webcam.
        print(f"Error: could not open webcam index {CAMERA_INDEX}.")  # Tell the user what failed.
        return 1  # Return a non-zero code to signal an error.

    hands = mp_hands.Hands(  # Create the MediaPipe hand detector/tracker.
        static_image_mode=False,  # Treat input as video so tracking can reuse previous frames.
        max_num_hands=1,  # Track only one hand for this instrument.
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,  # Set new-hand detection confidence.
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,  # Set continuing-hand tracking confidence.
    )

    detected_frame_count = 0  # Count frames where a hand is visible.
    print(  # Print a startup message so the user knows where packets are going.
        f"Sending {OSC_FEATURE_ADDRESS} to "
        f"{MACHINE_2_IP}:{OSC_PORT}. Press 'q' to quit."
    )

    try:  # Make sure cleanup runs even if the loop is interrupted.
        while True:  # Keep processing webcam frames until the user quits.
            frame_received, frame = camera.read()  # Ask OpenCV for one frame from the webcam.
            if not frame_received:  # Stop if OpenCV could not read the frame.
                print("Error: could not read a frame from the webcam.")  # Explain the failure.
                break  # Leave the main loop.

            frame = cv2.flip(frame, 1)  # Mirror the camera image so movement feels natural.
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for MediaPipe.
            results = hands.process(rgb_frame)  # Run MediaPipe hand detection/tracking on the frame.

            if results.multi_hand_landmarks:  # Continue only when at least one hand is detected.
                hand_landmarks = results.multi_hand_landmarks[0]  # Use the first detected hand.
                mp_draw.draw_landmarks(  # Draw the hand skeleton on the preview frame.
                    frame,  # Draw on the OpenCV frame.
                    hand_landmarks,  # Draw the detected landmarks.
                    mp_hands.HAND_CONNECTIONS,  # Draw the standard hand bone connections.
                )

                raw_features = feature_extractor.extract(hand_landmarks)  # Convert landmarks into seven raw features.
                features = feature_smoother.update(raw_features)  # Smooth the raw values before sending.

                detected_frame_count += 1  # Count this hand-detected frame.
                packet_sent = detected_frame_count % SEND_EVERY_N_FRAMES == 0  # Decide whether this frame should send.
                if packet_sent:  # Send only on the chosen interval.
                    osc_sender.send(features)  # Send the feature packet to Wekinator.

                draw_feature_overlay(frame, features, packet_sent)  # Show live values in the preview window.
            else:
                feature_extractor.reset()  # Clear old position history when the hand disappears.
                feature_smoother.reset()  # Clear smoothing history so reacquisition starts cleanly.
                detected_frame_count = 0  # Restart the send interval counter.
                draw_text(frame, "No hand detected", (20, 35))  # Tell the user the camera sees no hand.

            cv2.imshow(WINDOW_TITLE, frame)  # Display the annotated webcam frame.
            if cv2.waitKey(1) & 0xFF == ord("q"):  # Check whether the user pressed q.
                break  # Exit the loop when q is pressed.
    except KeyboardInterrupt:  # Handle Ctrl+C cleanly in the terminal.
        print("Stopping Machine 1.")  # Print a friendly stop message.
    finally:
        hands.close()  # Release MediaPipe resources.
        camera.release()  # Release the webcam.
        cv2.destroyAllWindows()  # Close OpenCV preview windows.

    return 0  # Signal successful shutdown.


if __name__ == "__main__":  # Run this block only when this file is executed directly.
    raise SystemExit(main())  # Run main() and use its return value as the process exit code.
