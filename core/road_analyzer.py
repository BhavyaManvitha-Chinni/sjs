import cv2
import time


class RoadAnalyzer:
    """
    FINAL Road Analyzer (Paper Complete)

    Shared YOLO model (loaded once)
    Detection + Tracking IDs (ByteTrack)
    Temporal approach validation
    Calibration-style distance estimation (0–200m)
    Relative speed trend score
    Distance + Speed overlay on video
    Clear WARNING trigger for demo
    Frame skipping for speed
    """

    def __init__(self, road_name, video_path, shared_model):

        self.road_name = road_name
        self.cap = cv2.VideoCapture(video_path)

        # Shared YOLO model
        self.model = shared_model

        # Vehicle classes: car, motorcycle, bus, truck
        self.vehicle_classes = [2, 3, 5, 7]

        # Tracking memory
        self.bbox_history = {}
        self.approach_counter = {}

        # Alert smoothing
        self.alert_active = False
        self.last_alert_time = 0

        # Parameters (Demo-friendly)
        self.APPROACH_FRAMES_REQUIRED = 2
        self.ALERT_HOLD_TIME = 6.0

        # Outputs
        self.vehicle_count = 0
        self.min_distance = 200
        self.speed_score = 0

        # Performance boost
        self.frame_skip = 1
        self.frame_count = 0


    # Distance Estimation (Calibration Approximation)
    
    def estimate_distance(self, bbox_height):
        
        if bbox_height <= 0:
            return 200

        dist = 200 - (bbox_height * 0.8)
        return max(10, min(200, dist))

    
    # Speed Trend Estimation
    
    def estimate_speed(self, current_h, prev_h):
        
        #Relative speed score based on bbox growth rate.
        
        return max(0, (current_h - prev_h) / 5)

    
    # Main Frame Processing
    
    def process_frame(self):

        # Frame skipping for faster execution
        self.frame_count += 1
        if self.frame_count % self.frame_skip != 0:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.resize(frame, (480, 320))
        current_time = time.time()

        approach_detected = False
        vehicle_count = 0
        min_distance = 200
        max_speed = 0

        # YOLO Detection + Tracking
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.4,
            classes=self.vehicle_classes
        )

        if results and results[0].boxes is not None:

            for box in results[0].boxes:

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

                prev_h = self.bbox_history[track_id]

                # Temporal persistence approach validation
                if bbox_height > prev_h + 3:
                    self.approach_counter[track_id] += 1
                else:
                    self.approach_counter[track_id] = max(
                        0, self.approach_counter[track_id] - 1
                    )

                # Approaching decision
                is_approaching = (
                    self.approach_counter[track_id] >= self.APPROACH_FRAMES_REQUIRED
                )

                # Distance + Speed only for approaching vehicles
                if is_approaching:

                    # Distance estimation
                    dist = self.estimate_distance(bbox_height)
                    min_distance = min(min_distance, dist)

                    # Speed estimation
                    speed = self.estimate_speed(bbox_height, prev_h)
                    max_speed = max(max_speed, speed)

                    # Clear WARNING trigger for demo
                    if dist < 195:
                        approach_detected = True

                    # Overlay Distance + Speed
                    cv2.putText(
                        frame,
                        f"D:{int(dist)}m",
                        (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (255, 255, 255),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"S:{speed:.2f}",
                        (x1, y2 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (255, 255, 255),
                        2
                    )

                # Update bbox history
                self.bbox_history[track_id] = bbox_height

                # Draw bounding box + ID
                color = (0, 255, 255) if is_approaching else (0, 255, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"ID:{track_id}",
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

        # Alert smoothing (hold time)
        if approach_detected:
            self.alert_active = True
            self.last_alert_time = current_time
        elif current_time - self.last_alert_time > self.ALERT_HOLD_TIME:
            self.alert_active = False

        # Save outputs
        self.vehicle_count = vehicle_count
        self.min_distance = min_distance
        self.speed_score = max_speed

        return frame

    
    # Road Status Output
    
    def get_status(self):

        return {
            "road": self.road_name,
            "alert": self.alert_active and self.vehicle_count > 0,
            "vehicle_count": self.vehicle_count,
            "min_distance": self.min_distance,
            "speed": self.speed_score
        }
