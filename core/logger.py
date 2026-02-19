import csv
import os
import time


class CSVLogger:
    """
    Final CSV Logger (Paper Results Support)

    Logs:
    - Road name
    - Alert state
    - Vehicle count
    - Minimum distance
    - Speed trend score
    """

    def __init__(self, filename="logs/run_log.csv"):

        os.makedirs("logs", exist_ok=True)
        self.filename = filename

        # Write header once
        with open(self.filename, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "road",
                "alert",
                "vehicle_count",
                "min_distance",
                "speed_score"
            ])

    def log(self, status):

        with open(self.filename, mode="a", newline="") as f:
            writer = csv.writer(f)

            writer.writerow([
                time.time(),
                status["road"],
                status["alert"],
                status["vehicle_count"],
                status["min_distance"],
                status["speed"]
            ])
