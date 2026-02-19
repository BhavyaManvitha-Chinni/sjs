import cv2
from ultralytics import YOLO

from core.road_analyzer import RoadAnalyzer
from ui.led_board import LedBoard
from core.junction_controller import JunctionLogic
from core.logger import CSVLogger


def main():

    print("\n[INFO] Smart Junction Safety Alert System Started...\n")

    # Load YOLO once
    shared_model = YOLO("yolov8n.pt", verbose=False)

    # Junction type selection
    JUNCTION_TYPE = "Y_JUNCTION"   # FOUR_WAY / T_JUNCTION / Y_JUNCTION
    print("[INFO] Junction Type:", JUNCTION_TYPE)

    # Select road streams based on junction
    if JUNCTION_TYPE == "FOUR_WAY":
        analyzers = [
            RoadAnalyzer("NORTH", "videos/north.mp4", shared_model),
            RoadAnalyzer("SOUTH", "videos/south.mp4", shared_model),
            RoadAnalyzer("EAST", "videos/east.mp4", shared_model),
            RoadAnalyzer("WEST", "videos/west.mp4", shared_model),
        ]
        blind_roads = ["NORTH", "SOUTH", "EAST", "WEST"]

    elif JUNCTION_TYPE == "T_JUNCTION":
        analyzers = [
            RoadAnalyzer("NORTH", "videos/north.mp4", shared_model),
            RoadAnalyzer("EAST", "videos/east.mp4", shared_model),
            RoadAnalyzer("WEST", "videos/west.mp4", shared_model),
        ]
        blind_roads = ["NORTH", "EAST", "WEST"]

    elif JUNCTION_TYPE == "Y_JUNCTION":
        analyzers = [
            RoadAnalyzer("LEFT", "videos/east.mp4", shared_model),
            RoadAnalyzer("RIGHT", "videos/west.mp4", shared_model),
            RoadAnalyzer("MAIN", "videos/highway.mp4", shared_model),
        ]
        blind_roads = ["LEFT", "RIGHT", "MAIN"]

    # LED dashboard
    led_board = LedBoard(JUNCTION_TYPE)

    # Junction fusion logic
    junction_logic = JunctionLogic(blind_roads)

    # CSV logging
    logger = CSVLogger()
    print("[INFO] Logging Enabled → logs/run_log.csv")
    print("[INFO] Press 'q' or 'Esc' to quit.\n")

    while True:

        road_status_dict = {}
        full_statuses = []

        for analyzer in analyzers:

            frame = analyzer.process_frame()
            status = analyzer.get_status()

            full_statuses.append(status)
            road_status_dict[status["road"]] = status["alert"]

            # Log results
            logger.log(status)

            # Show camera feed
            if frame is not None:
                cv2.imshow(f"{status['road']} Camera", frame)

        # Update LED board
        led_board.update(road_status_dict)

        # Update junction fusion
        junction_logic.update(full_statuses)

        # Quit control (Reliable)
        key = cv2.waitKey(10) & 0xFF
        if key == ord("q") or key == 27:
            print("\n[INFO] Exit key pressed. Closing system...")
            break

    # Release video resources
    for analyzer in analyzers:
        analyzer.cap.release()

    cv2.destroyAllWindows()
    print("[INFO] System Stopped Successfully.\n")


if __name__ == "__main__":
    main()
