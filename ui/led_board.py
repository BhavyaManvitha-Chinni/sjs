import cv2
import numpy as np


class LedBoard:
    def __init__(self, junction_type="FOUR_WAY"):

        self.width = 900
        self.height = 650

        
        # JUNCTION CONFIG RULES
        
        self.junction_type = junction_type

        if junction_type == "FOUR_WAY":
            self.rules = {
                "NORTH TO SOUTH": ["EAST", "WEST"],
                "SOUTH TO NORTH": ["EAST", "WEST"],
                "EAST TO WEST": ["NORTH", "SOUTH"],
                "WEST TO EAST": ["NORTH", "SOUTH"]
            }

        elif junction_type == "T_JUNCTION":
            self.rules = {
                "NORTH TO SOUTH": ["EAST", "WEST"],
                "EAST TO WEST": ["NORTH"],
                "WEST TO EAST": ["NORTH"]
            }

        elif junction_type == "Y_JUNCTION":
            self.rules = {
                "LEFT BRANCH": ["RIGHT"],
                "RIGHT BRANCH": ["LEFT"],
                "MAIN ROAD": ["LEFT", "RIGHT"]
            }

        
        # PANEL POSITIONS (2×2 GRID)
        
        self.positions = {
            "NORTH TO SOUTH": (50, 80),
            "SOUTH TO NORTH": (480, 80),
            "EAST TO WEST": (50, 360),
            "WEST TO EAST": (480, 360),

            # Extra names for Y junction
            "LEFT BRANCH": (50, 80),
            "RIGHT BRANCH": (480, 80),
            "MAIN ROAD": (50, 360)
        }

        # Threat direction display
        self.arrow_text = {
            "EAST": "RIGHT",
            "WEST": "LEFT",
            "NORTH": "UP",
            "SOUTH": "DOWN",
            "LEFT": "LEFT",
            "RIGHT": "RIGHT"
        }

    
    def update(self, road_status_dict):
        
        road_statuses = []

        for road, alert in road_status_dict.items():
            road_statuses.append({
                "road": road,
                "alert": alert
            })

        self.render(road_statuses)

    
    def render(self, road_statuses):

        # Convert list → dict
        status_dict = {s["road"]: s["alert"] for s in road_statuses}

        # Background window
        board = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        
        cv2.putText(
            board,
            f"SMART JUNCTION LED WARNING SYSTEM ({self.junction_type})",
            (90, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )


        for movement, threats in self.rules.items():

            px, py = self.positions[movement]

            # Find active threats
            active_threats = [t for t in threats if status_dict.get(t, False)]

            # Panel border
            cv2.rectangle(board, (px, py), (px + 360, py + 250),
                          (200, 200, 200), 2)

            # Movement label
            cv2.putText(
                board,
                movement,
                (px + 60, py + 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2
            )

            if active_threats:
                light_color = (0, 255, 255)  # Yellow
                status_text = "WARNING"
            else:
                light_color = (0, 255, 0)    # Green
                status_text = "SAFE"

            # Traffic Light Circle
            cv2.circle(board, (px + 70, py + 120), 40, light_color, -1)

            # Status Text
            cv2.putText(
                board,
                status_text,
                (px + 140, py + 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                light_color,
                3
            )

            if active_threats:
                arrow_text = " ".join([self.arrow_text[t] for t in active_threats])
            else:
                arrow_text = "-"

            cv2.putText(
                board,
                f"Threat: {arrow_text}",
                (px + 80, py + 210),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (255, 255, 255),
                2
            )

        # Show dashboard
        cv2.imshow("JUNCTION LED DASHBOARD", board)
        cv2.waitKey(1)
