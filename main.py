import numpy as np
from DroneSimulator import DroneSimulator

# Main function to run the simulator
def main():
    map_size = (150, 150)  # Scaled map size for better visibility
    map_data = np.ones(map_size)

    # Add obstacles to the map
    for i in range(20, 130):
        map_data[i, 20] = 0  # Vertical wall
        map_data[i, 130] = 0  # Vertical wall

    for i in range(20, 130):
        map_data[20, i] = 0  # Horizontal wall
        map_data[130, i] = 0  # Horizontal wall

    for i in range(40, 110):
        map_data[i, 70] = 0  # Vertical wall in the middle

    for i in range(70, 110):
        map_data[90, i] = 0  # Horizontal wall in the middle

    for i in range(30, 120):
        map_data[50, i] = 0  # Horizontal wall

    for i in range(50, 90):
        map_data[i, 50] = 0  # Vertical wall

    start_position = (75, 75)
    far_point = (120, 120)

    simulator = DroneSimulator(map_data, start_position, far_point)

if __name__ == "__main__":
    main()
