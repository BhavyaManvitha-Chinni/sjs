import cv2
import time
from ultralytics import YOLO


class RoadAnalyzer:
    def __init__(self, road_name, video_path):

        self.road_name = road_name
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        # Load YOLO model
        self.model = YOLO("yolov8n.pt", verbose=False)

        # Vehicle class IDs (car, bike, bus, truck)
        self.vehicle_classes = [2, 3, 5, 7]

        # Tracking memory
        self.bbox_history = {}       # track_id → last bbox height
        self.approach_counter = {}   # track_id → approach frames

        # Alert control
        self.alert_active = False
        self.last_alert_time = 0

        # Parameters
        self.APPROACH_FRAMES_REQUIRED = 2
        self.ALERT_HOLD_TIME = 2.0

        # Status values
        self.vehicle_count = 0

    def process_frame(self):

        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.resize(frame, (640, 384))
        current_time = time.time()

        approach_detected = False
        vehicle_count = 0

        # YOLO detection + tracking
        results = self.model.track(
            frame,
            persist=True,
            conf=0.4,
            classes=self.vehicle_classes
        )

        if results and results[0].boxes is not None:
            boxes = results[0].boxes

            for box in boxes:

                if box.id is None:
                    continue

                track_id = int(box.id.item())

                # Bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bbox_height = y2 - y1

                vehicle_count += 1

                # Initialize memory
                if track_id not in self.bbox_history:
                    self.bbox_history[track_id] = bbox_height
                    self.approach_counter[track_id] = 0
                    continue

                prev_height = self.bbox_history[track_id]

                # Approach detection using bbox growth
                if bbox_height > prev_height + 3:
                    self.approach_counter[track_id] += 1
                else:
                    self.approach_counter[track_id] = max(
                        0, self.approach_counter[track_id] - 1
                    )

                # Confirm approaching vehicle
                #if y2 > frame.shape[0] * 0.65:
                    #approach_detected = True
                if self.approach_counter[track_id] >= self.APPROACH_FRAMES_REQUIRED:
                    approach_detected = True

                self.bbox_history[track_id] = bbox_height

                # Draw bounding box
                color = (0, 255, 255) if approach_detected else (0, 255, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                cv2.putText(
                    frame,
                    f"ID:{track_id}",
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

        # Alert smoothing
        if approach_detected:
            self.alert_active = True
            self.last_alert_time = current_time
        elif current_time - self.last_alert_time > self.ALERT_HOLD_TIME:
            self.alert_active = False

        self.vehicle_count = vehicle_count
        return frame

    def get_status(self):

        return {
            "road": self.road_name,
            "alert": self.alert_active and self.vehicle_count > 0,
            "vehicle_count": self.vehicle_count
        }
