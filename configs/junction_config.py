JUNCTION_TYPES = {

    "FOUR_WAY": {
        "panels": {
            "NORTH TO SOUTH": ["EAST", "WEST"],
            "SOUTH TO NORTH": ["EAST", "WEST"],
            "EAST TO WEST": ["NORTH", "SOUTH"],
            "WEST TO EAST": ["NORTH", "SOUTH"]
        }
    },

    "T_JUNCTION": {
        "panels": {
            "NORTH TO SOUTH": ["EAST", "WEST"],
            "EAST TO WEST": ["NORTH"],
            "WEST TO EAST": ["NORTH"]
        }
    },

    "Y_JUNCTION": {
        "panels": {
            "LEFT BRANCH": ["RIGHT"],
            "RIGHT BRANCH": ["LEFT"],
            "MAIN ROAD": ["LEFT", "RIGHT"]
        }
    }
}
