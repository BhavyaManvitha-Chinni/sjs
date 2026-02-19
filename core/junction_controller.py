class JunctionLogic:
    
    #FINAL Algorithm 2 Junction Fusion
    

    def __init__(self, blind_roads):
        self.blind_roads = blind_roads
        self.current_signal = "GREEN"
        self.active_direction = None

    def update(self, road_statuses):

        self.current_signal = "GREEN"
        self.active_direction = None
        highest_risk = 0

        for status in road_statuses:

            road = status["road"]

            if road not in self.blind_roads:
                continue

            if status["alert"]:

                # Risk Score 
                risk = (
                    status["vehicle_count"]
                    + (200 - status["min_distance"]) / 20
                    + status["speed"]
                )

                if risk > highest_risk:
                    highest_risk = risk
                    self.current_signal = "YELLOW"
                    self.active_direction = road

    def get_signal(self):
        return {
            "signal": self.current_signal,
            "direction": self.active_direction
        }
