# Drone Simulator :money_with_wings:
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

