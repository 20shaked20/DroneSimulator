import numpy as np
import heapq
from collections import defaultdict
import random

class Drone:
    def __init__(self, start_position, map_data, far_point):
        self.position = start_position
        self.start_position = start_position
        self.map_data = map_data
        self.far_point = far_point
        self.battery_level = 100  # Start with full battery
        self.covered_area = set()
        self.path = [start_position]
        self.time_elapsed = 0
        self.current_direction = (1, 0)  # Start moving right
        self.returning_home = False
        self.return_path = []
        self.adjacency_list = defaultdict(list)
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.velocity = (0, 0)  # (vx, vy)
        self.altitude = 0
        self.flight_state = "Taking off"
        
    def get_sensor_data(self):
        """Get sensor data for the drone."""
        distances = {
            'up': self._distance_to_obstacle(self.position, (0, -1)),
            'down': self._distance_to_obstacle(self.position, (0, 1)),
            'left': self._distance_to_obstacle(self.position, (-1, 0)),
            'right': self._distance_to_obstacle(self.position, (1, 0)),
            'forward': self._distance_to_obstacle(self.position, (1, 1)),
            'backward': self._distance_to_obstacle(self.position, (-1, -1))
        }
        sensor_data = {
            'd0': distances['up'],
            'd1': distances['down'],
            'd2': distances['left'],
            'd3': distances['right'],
            'd4': distances['forward'],
            'yaw': self.yaw,
            'Vx': self.velocity[0] * 0.025,  # Convert to m/s
            'Vy': self.velocity[1] * 0.025,  # Convert to m/s
            'Z': self.altitude,
            'baro': self.altitude,
            'bat': self.battery_level,
            'pitch': self.pitch,
            'roll': self.roll,
            'accX': self.velocity[0] * 10 * 0.025,  # Simulate acceleration data in m/s^2
            'accY': self.velocity[1] * 10 * 0.025,  # Simulate acceleration data in m/s^2
            'accZ': 0   # Placeholder for vertical acceleration
        }
        return sensor_data

    def _distance_to_obstacle(self, position, direction):
        """Calculate the distance to the nearest obstacle in a given direction."""
        x, y = position
        dx, dy = direction
        distance = 0
        while 0 <= x < self.map_data.shape[1] and 0 <= y < self.map_data.shape[0]:
            x += dx
            y += dy
            distance += 1
            if self.map_data[y, x] == 0:
                break
        return max(0, distance * 0.025 - 0.1)  # Each pixel is 2.5 cm, convert to meters, minus drone radius
    
    def move(self, direction):
        """Move the drone in the given direction."""
        if direction is None:
            return
        
        x, y = self.position
        dx, dy = direction
        new_position = (x + dx, y + dy)
        if self._is_valid_position(new_position):
            self.position = new_position
            self.covered_area.add(new_position)
            self.path.append(new_position)
            self._update_adjacency_list((x, y), new_position)
            self.update_orientation(direction)
            self.update_velocity(direction)
            print(f"Moved to new position: {self.position}")
        else:
            print(f"Failed to move to new position: {new_position}, trying different directions")
            possible_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for d in possible_directions:
                new_position = (x + d[0], y + d[1])
                if self._is_valid_position(new_position):
                    self.position = new_position
                    self.covered_area.add(new_position)
                    self.path.append(new_position)
                    self._update_adjacency_list((x, y), new_position)
                    self.current_direction = d
                    self.update_orientation(d)
                    self.update_velocity(d)
                    print(f"Moved to new position: {self.position} after detecting obstacle")
                    break
    
    def _update_adjacency_list(self, old_position, new_position):
        """Update the adjacency list for the drone's path."""
        self.adjacency_list[old_position].append(new_position)
        self.adjacency_list[new_position].append(old_position)
    
    def _is_valid_position(self, position):
        """Check if a position is valid (i.e., within bounds and not an obstacle)."""
        x, y = position
        valid = 0 <= x < self.map_data.shape[1] and 0 <= y < self.map_data.shape[0] and self.map_data[y, x] == 1
        print(f"Position {position} is {'valid' if valid else 'invalid'}")
        return valid
    
    def update_battery(self, time_step=1):
        """Update the battery level based on time step."""
        self.battery_level -= (100 / 480) * time_step
        print(f"Battery updated: {self.battery_level:.2f}%")
    
    def plan_next_move(self):
        """Plan the next move based on the current state and battery level."""
        x, y = self.position
        print(f"Current position: {self.position}, Battery: {self.battery_level:.2f}%")
        
        if self.battery_level > 50:
            unvisited_adjacent = []
            for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_position = (x + direction[0], y + direction[1])
                if self._is_valid_position(next_position) and next_position not in self.covered_area:
                    unvisited_adjacent.append(direction)
            
            if unvisited_adjacent:
                next_move = random.choice(unvisited_adjacent)
                print(f"Unvisited adjacent: {unvisited_adjacent}, Next move: {next_move}")
                return next_move
            
            print(f"Continuing in current direction: {self.current_direction}")
            return self.current_direction
        else:
            if not self.returning_home:
                self.start_returning_home()
            return self.return_home()
    
    def start_returning_home(self):
        """Start returning home using Dijkstra's algorithm."""
        self.returning_home = True
        self.return_path = self.dijkstra(self.position, self.start_position)
        print("Starting to return home, path:", self.return_path)
    
    def return_home(self):
        """Return home following the calculated path."""
        if not self.return_path:
            print("Reached home or no valid path")
            return None
        
        next_position = self.return_path.pop(0)
        move = (next_position[0] - self.position[0], next_position[1] - self.position[1])
        print(f"Returning home, next move: {move}")
        return move
    
    def dijkstra(self, start, goal):
        """Dijkstra's algorithm to find the shortest path to the goal."""
        queue = [(0, start)]
        distances = {start: 0}
        previous_nodes = {start: None}

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_node == goal:
                break

            for neighbor in self.adjacency_list[current_node]:
                distance = current_distance + 1
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    priority = distance
                    heapq.heappush(queue, (priority, neighbor))
                    previous_nodes[neighbor] = current_node

        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = previous_nodes[current]

        path.reverse()
        print(f"Path found: {path}")
        return path if path[0] == start else []

    def update_orientation(self, direction):
        """Update the drone's orientation based on its direction."""
        dx, dy = direction
        if dx > 0:
            self.yaw = 0
        elif dx < 0:
            self.yaw = 180
        elif dy > 0:
            self.yaw = 90
        elif dy < 0:
            self.yaw = -90
        
        self.pitch = (self.velocity[0] / 3) * 10  # Simulate pitch based on velocity, max speed 3 m/s
        self.roll = (self.velocity[1] / 3) * 10   # Simulate roll based on velocity, max speed 3 m/s

    def update_velocity(self, direction):
        """Update the drone's velocity based on its direction."""
        dx, dy = direction
        self.velocity = (dx, dy)

    def takeoff(self):
        """Simulate the drone takeoff."""
        if self.altitude == 0:
            self.altitude = 1  # Takeoff to a height of 1 meter
            print("Taking off to a height of 1 meter")

    def land(self):
        """Simulate the drone landing."""
        if self.altitude > 0:
            self.altitude = 0  # Land the drone
            print("Landing the drone")
