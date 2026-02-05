import cv2
import time

from core.road_analyzer import RoadAnalyzer
from ui.led_board import LedBoard


def main():
    print("\n[INFO] Multi-Road Junction Safety System Started")
    print("[INFO] Press 'q' to quit\n")

    # ============================
    # VIDEO INPUTS (4 Directions)
    # ============================
    roads = [
        RoadAnalyzer("EAST", "videos/east.mp4"),
        RoadAnalyzer("WEST", "videos/west.mp4"),
        RoadAnalyzer("NORTH", "videos/north.mp4"),
        RoadAnalyzer("SOUTH", "videos/south.mp4")
    ]

    # ============================
    # SELECT JUNCTION TYPE
    # Options: FOUR_WAY, T_JUNCTION, Y_JUNCTION
    # ============================
    led_board = LedBoard(junction_type="FOUR_WAY")

    # ============================
    # MAIN LOOP
    # ============================
    while True:

        road_statuses = []

        # ---- Process each road ----
        for road in roads:

            frame = road.process_frame()
            if frame is None:
                continue

            # Show road camera window
            cv2.imshow(f"Road View: {road.road_name}", frame)

            # Collect road status
            road_statuses.append(road.get_status())

        # ---- Render LED Dashboard ----
        led_board.render(road_statuses)

        # ---- Exit condition ----
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        time.sleep(0.01)

    # Cleanup
    cv2.destroyAllWindows()
    print("\n[INFO] System Stopped Successfully\n")


if __name__ == "__main__":
    main()
