# Drone Simulator :money_with_wings:
## Created By:
* :space_invader: [Shaked Levi](https://github.com/20shaked20)
* :octocat: [Dana Zorohov](https://github.com/danaZo)
* :trollface: [Yuval Bubnovsky](https://github.com/YuvalBubnovsky)
</br>
## Overview :pushpin:
The Drone Simulator is a Python-based simulation of an autonomous drone navigating a 2D environment. This simulator models a drone equipped with multiple sensors to detect its surroundings and autonomously plan its path to explore as much terrain as possible. The drone will return to its starting point when the battery level drops to 50%. The simulator uses Pygame for visual representation and basic control algorithms for navigation.
</br></br>

## Features :desktop_computer:
- **2D Map Representation:** The environment is represented as a 2D grid where each cell can be either an obstacle or a free space.
- **Drone Sensors:** Simulated sensors include distance meters in six directions, a speed sensor, an orientation sensor (IMU), a barometer, and a battery sensor.
- **Autonomous Navigation:** The drone uses a simple control algorithm to navigate and avoid obstacles, attempting to cover as much area as possible.
- **Battery Management:** The drone monitors its battery level and returns to the starting point when the battery level reaches 50%.
- **Pathfinding:** Uses Dijkstra's algorithm for efficient pathfinding during the return to the home position.
- **Visualization:** Uses Pygame to visualize the drone's movement, the explored area, obstacles, and other key information.
</br></br>

## Installation :arrow_down:
1. Clone the Repository: </br>

```
git clone https://github.com/your-repo/drone-simulator.git

```

```
cd drone-simulator
```

3. Install Dependencies: </br>

```
pip install pygame numpy
```
</br></br>

## Usage :joystick:
- Run the Simulator:

```
python drone_simulator.py
```

- Simulation Controls:
  - The simulation starts automatically, with the drone beginning its navigation from the start position.
  - The drone will autonomously navigate the environment, avoiding obstacles and trying to cover as much terrain as possible.
  - When the battery level reaches 50%, the drone will start returning to the start position.

</br></br>

## Code Structure :page_with_curl:
- ```drone_simulator.py:``` The main script that initializes and runs the simulation.
- ```DroneSimulator Class:``` Manages the Pygame window, updates the simulation, and handles user inputs.
- ```Drone Class:``` Contains the drone's logic, including sensor data processing, movement, battery management, and pathfinding.

</br></br>

## Implementation Details :hammer:

### Part One: Platform Search and Interface Definition :mag:
- The simulator uses a 2D grid to model the environment. The grid cells represent 2.5 cm x 2.5 cm areas.
- The drone has six distance sensors, an IMU for orientation, a barometer for altitude, and a battery sensor. Sensor data is updated at 10 Hz.
- The interface for calculating distances is implemented in the ```get_sensor_data``` method, which uses the ```_distance_to_obstacle``` helper function to calculate distances to the nearest obstacles.

### Part Two: Control System :wrench:
- The drone navigates autonomously using a simple control algorithm. It tries to explore unvisited adjacent cells and avoids obstacles.
- The ```plan_next_move``` method determines the drone's next move based on sensor data and battery level.
- When the battery level reaches 50%, the drone uses Dijkstra's algorithm to find the shortest path back to the starting point (```return_home``` method).

</br></br>

## Future Improvements :crystal_ball:
- **Enhance Control Algorithm:** Implement more advanced algorithms for navigation and obstacle avoidance.
- **3D Environment:** Extend the simulator to support 3D modeling and navigation.
- **Reinforcement Learning:** Explore reinforcement learning techniques to improve the drone's navigation strategy.
- **Real-world Integration:** Interface with real drones and sensors for testing in physical environments.
</br></br>
