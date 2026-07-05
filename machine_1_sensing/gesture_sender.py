"""Run the Machine 1 webcam, feature extraction, and OSC transmission."""

import cv2
import mediapipe.python.solutions.drawing_utils as mp_draw
import mediapipe.python.solutions.hands as mp_hands

from config import (
    CAMERA_INDEX,
    FEATURE_DEAD_BANDS,
    MACHINE_2_IP,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MOVEMENT_DEAD_ZONE,
    OSC_FEATURE_ADDRESS,
    OSC_PORT,
    SEND_EVERY_N_FRAMES,
    SMOOTHING_FACTOR,
    validate_config,
)
from feature_extractor import FeatureSmoother, HandFeatureExtractor
from osc_sender import OscFeatureSender


WINDOW_TITLE = "Shape Orchestra - Machine 1"
TEXT_COLOR = (0, 255, 0)
TEXT_OUTLINE_COLOR = (0, 0, 0)


def draw_text(frame, text, position):
    """Draw readable text with a black outline on the webcam frame."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(
        frame,
        text,
        position,
        font,
        0.62,
        TEXT_OUTLINE_COLOR,
        4,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        text,
        position,
        font,
        0.62,
        TEXT_COLOR,
        1,
        cv2.LINE_AA,
    )


def draw_feature_overlay(frame, features, packet_sent):
    """Display the live values that are being prepared for Machine 2."""
    rows = (
        f"Position: ({features['x']:.3f}, {features['y']:.3f})",
        f"Speed: {features['speed']:.4f}",
        (
            "Direction: "
            f"({features['direction_x']:.4f}, {features['direction_y']:.4f})"
        ),
        f"Openness: {features['openness']:.3f}",
        f"Energy: {features['energy']:.4f}",
        "OSC: sent" if packet_sent else "OSC: waiting for send interval",
    )

    for row_index, row in enumerate(rows):
        draw_text(frame, row, (20, 35 + row_index * 28))


def main():
    """Capture the hand, extract features, and stream them to Machine 2."""
    validate_config()

    feature_extractor = HandFeatureExtractor(MOVEMENT_DEAD_ZONE)
    feature_smoother = FeatureSmoother(
        SMOOTHING_FACTOR,
        FEATURE_DEAD_BANDS,
    )
    osc_sender = OscFeatureSender(
        MACHINE_2_IP,
        OSC_PORT,
        OSC_FEATURE_ADDRESS,
    )

    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        print(f"Error: could not open webcam index {CAMERA_INDEX}.")
        return 1

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )

    detected_frame_count = 0
    print(
        f"Sending {OSC_FEATURE_ADDRESS} to "
        f"{MACHINE_2_IP}:{OSC_PORT}. Press 'q' to quit."
    )

    try:
        while True:
            frame_received, frame = camera.read()
            if not frame_received:
                print("Error: could not read a frame from the webcam.")
                break

            # Mirror the image so movement feels natural to the performer.
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                )

                raw_features = feature_extractor.extract(hand_landmarks)
                features = feature_smoother.update(raw_features)

                detected_frame_count += 1
                packet_sent = detected_frame_count % SEND_EVERY_N_FRAMES == 0
                if packet_sent:
                    osc_sender.send(features)

                draw_feature_overlay(frame, features, packet_sent)
            else:
                # Reset history so reacquiring the hand does not create a
                # false movement spike from an old position.
                feature_extractor.reset()
                feature_smoother.reset()
                detected_frame_count = 0
                draw_text(frame, "No hand detected", (20, 35))

            cv2.imshow(WINDOW_TITLE, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        print("Stopping Machine 1.")
    finally:
        hands.close()
        camera.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
