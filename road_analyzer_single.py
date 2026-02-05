import cv2
import numpy as np
import time
from ultralytics import YOLO

# =========================
# LOAD YOLO MODEL
# =========================
model = YOLO("yolov8n.pt", verbose=False)

# =========================
# VIDEO SOURCE
# =========================
video_path = "videos/highway.mp4"  # or 0 for webcam
cap = cv2.VideoCapture(video_path)

# =========================
# VEHICLE CLASSES
# =========================
VEHICLE_CLASSES = ["car", "bus", "truck", "motorcycle"]

# =========================
# TRACK MEMORY
# =========================
bbox_history = {}          # track_id -> last bbox height
approach_counter = {}     # track_id -> consecutive approach frames

# =========================
# ALERT CONTROL
# =========================
APPROACH_FRAMES_REQUIRED = 1     # confirmation frames
ALERT_HOLD_TIME = 2.0            # seconds
last_alert_time = 0
alert_active = False

# =========================
# MAIN LOOP
# =========================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (960, 540))
    current_time = time.time()
    approach_detected_this_frame = False

    # YOLO detection + tracking
    results = model.track(
        frame,
        persist=True,
        conf=0.4,
        classes=[2, 3, 5, 7]
    )

    if results and results[0].boxes is not None:
        boxes = results[0].boxes

        for box in boxes:
            if box.id is None:
                continue

            track_id = int(box.id.item())
            cls_id = int(box.cls.item())
            class_name = model.names[cls_id]

            if class_name not in VEHICLE_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox_height = y2 - y1

            # Initialize memory
            if track_id not in bbox_history:
                bbox_history[track_id] = bbox_height
                approach_counter[track_id] = 0
                continue

            prev_height = bbox_history[track_id]

            # -------------------------
            # APPROACH LOGIC (SMOOTHED)
            # -------------------------
            if bbox_height > prev_height + 3:
                approach_counter[track_id] += 1
            else:
                approach_counter[track_id] = max(0, approach_counter[track_id] - 1)

            if approach_counter[track_id] >= APPROACH_FRAMES_REQUIRED:
                approach_detected_this_frame = True

            bbox_history[track_id] = bbox_height

            # Draw detection
            color = (0, 255, 255) if approach_counter[track_id] >= APPROACH_FRAMES_REQUIRED else (0, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                f"{class_name} ID:{track_id}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

    # =========================
    # ALERT STATE LOGIC
    # =========================
    if approach_detected_this_frame:
        alert_active = True
        last_alert_time = current_time
    elif current_time - last_alert_time > ALERT_HOLD_TIME:
        alert_active = False

    # =========================
    # LED BOARD WINDOW
    # =========================
    led_board = np.ones((300, 300, 3), dtype="uint8") * 255

    if alert_active:
        led_board[:] = (0, 255, 255)  # YELLOW
        text = "VEHICLE APPROACHING"
    else:
        led_board[:] = (0, 255, 0)    # GREEN
        text = "SAFE TO MERGE"

    cv2.putText(
        led_board,
        text,
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2
    )

    # =========================
    # DISPLAY
    # =========================
    cv2.imshow("Vehicle Detection & Analysis", frame)
    cv2.imshow("Service Road LED Alert Board", led_board)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
