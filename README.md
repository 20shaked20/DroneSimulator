# Drone Simulator :money_with_wings:
## Created By:
* :space_invader: [Shaked Levi](https://github.com/20shaked20)
* :octocat: [Dana Zorohov](https://github.com/danaZo)
* :trollface: [Yuval Bubnovsky](https://github.com/YuvalBubnovsky)

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
python main.py
```

- Simulation Controls:
  - The simulation starts automatically, with the drone beginning its navigation from the start position.
  - The drone will autonomously navigate the environment, avoiding obstacles and trying to cover as much terrain as possible.
  - When the battery level reaches 50%, the drone will start returning to the start position.

</br></br>

## Code Structure :page_with_curl:
- ```main.py:``` The main script that initializes and runs the simulation.
- ```DroneSimulator Class:``` Manages the Pygame window, updates the simulation, and handles user inputs.
- ```Drone Class:``` Contains the drone's logic, including sensor data processing, movement, battery management, and pathfinding.

</br></br>

## Implementation Details :hammer:

### Part One: Platform Search and Interface Definition :mag:
- The simulator uses a 2D grid to model the environment. The grid cells represent 2.5 cm x 2.5 cm areas.
- The drone has multiple sensors, an IMU for orientation, a barometer for atmospheric pressure, altitude, and a battery sensor. Sensor data is updated at 10 Hz (ticks).
- The interface for calculating distances is implemented in the ```get_sensor_data``` method, which uses the ```_distance_to_obstacle``` helper function to calculate distances to the nearest obstacles.

### Part Two: Control System :wrench:
- The drone navigates autonomously using a simple control algorithm. It tries to explore unvisited adjacent cells and avoids obstacles.
- The ```plan_next_move``` method determines the drone's next move based on sensor data and battery level.
- When the battery level reaches 50%, the drone uses Dijkstra's algorithm to find the shortest path back to the starting point (```return_home``` method).

</br></br>

## Visualization
### Start Flying

<p align="center">
<img src="https://github.com/20shaked20/DroneSimulator/assets/93203695/6e23da71-7691-4229-93b4-9def28691efb">
</p>

- Drone is "Taking Off".
- Battery is 100%.
- Flight Time: 0 seconds.
- State: "Taking Off".
</br>

### Flying

<p align="center">
<img src="https://github.com/20shaked20/DroneSimulator/assets/93203695/1b1fdca9-4e8d-43f6-94b9-6d6b1ba76694">
</p>

- Drone is "Flying".
- Battery is 98.25% (drone has started flying --> battery went down)
- Flight Time: 8.40 seconds.
- State: "Flying".
</br>

### Returning Home

<p align="center">
<img src="https://github.com/20shaked20/DroneSimulator/assets/93203695/b8ef3f37-5206-4e32-8ea3-d04cab155c07">
</p>

- Drone is "Flying".
- Battery is 49.60% (when battery level is 50% --> drone flying back to home)
- Flight Time: 241.90 seconds.
- State: "Returning Home".
</br>

### Landing

<p align="center">
<img src="https://github.com/20shaked20/DroneSimulator/assets/93203695/2944beb1-f2f4-4b90-a216-3c5e2a2d4c1e">
</p>

- Drone is "Landed Safely".
- Battery is 39.81% (The drone took the fastest route back home --> battery not empty :) )
- Flight Time: 288.90 seconds.
- State: "Landed".
</br>


## Future Improvements :crystal_ball:
- **Enhance Control Algorithm:** Implement more advanced algorithms for navigation and obstacle avoidance.
- **3D Environment:** Extend the simulator to support 3D modeling and navigation.
- **Reinforcement Learning:** Explore reinforcement learning techniques to improve the drone's navigation strategy.
- **Real-world Integration:** Interface with real drones and sensors for testing in physical environments.
</br></br>
