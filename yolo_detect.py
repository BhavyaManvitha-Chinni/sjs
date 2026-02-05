from ultralytics import YOLO
import cv2

# ----------------------------
# Load YOLO model
# ----------------------------
model = YOLO("yolov8n.pt")

# ----------------------------
# Video path
# ----------------------------
video_path = "videos/highway.mp4"
cap = cv2.VideoCapture(video_path)

# ----------------------------
# Vehicle classes
# ----------------------------
VEHICLE_CLASSES = ["car", "bus", "truck", "motorcycle"]

# ----------------------------
# WARNING ZONE (simulated 200m)
# ----------------------------
WARNING_ZONE_Y = 300   # adjust this value up/down as needed

# ----------------------------
# Main loop
# ----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    approaching_vehicle_detected = False

    # Run YOLO
    results = model(frame, verbose=False)

    # Draw warning zone line
    cv2.line(
        frame,
        (0, WARNING_ZONE_Y),
        (frame.shape[1], WARNING_ZONE_Y),
        (0, 0, 255),
        2
    )
    cv2.putText(
        frame,
        "200m WARNING ZONE",
        (10, WARNING_ZONE_Y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]

        if class_name in VEHICLE_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            # EARLY WARNING LOGIC
            if y2 > WARNING_ZONE_Y:
                approaching_vehicle_detected = True

            label = f"{class_name} {conf:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    # ----------------------------
    # LED BOARD SIMULATION
    # ----------------------------
    if approaching_vehicle_detected:
        status_text = "ALERT: VEHICLE APPROACHING"
        color = (0, 255, 255)  # YELLOW
    else:
        status_text = "CLEAR: NO VEHICLE"
        color = (0, 255, 0)    # GREEN

    cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), color, -1)
    cv2.putText(
        frame,
        status_text,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 0),
        2
    )

    cv2.imshow("Highway Safety Early Warning System", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
