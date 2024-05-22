import pygame
import numpy as np
import random
import heapq
import math

class DroneSimulator:
    def __init__(self, map_data, start_position, far_point):
        pygame.init()
        self.map_data = map_data
        self.start_position = start_position
        self.far_point = far_point
        self.drone = Drone(start_position, map_data, far_point)
        self.cell_size = 5  # Size of each cell in the grid
        self.screen_size = (map_data.shape[1] * self.cell_size, map_data.shape[0] * self.cell_size + 50)
        
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Drone Simulator")
        
        self.font = pygame.font.SysFont(None, 24)
        
        self.running = True
        self.clock = pygame.time.Clock()
        
        self.update_simulation()
    
    def draw_map(self):
        for y in range(self.map_data.shape[0]):
            for x in range(self.map_data.shape[1]):
                color = (255, 255, 255) if self.map_data[y, x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
    
    def draw_start_and_end_points(self):
        # Draw starting point circle
        start_x, start_y = self.start_position
        pygame.draw.circle(self.screen, (0, 255, 0), (start_x * self.cell_size + self.cell_size // 2, start_y * self.cell_size + self.cell_size // 2), self.cell_size // 2)
        
        # Draw far point circle
        far_x, far_y = self.far_point
        pygame.draw.circle(self.screen, (255, 0, 0), (far_x * self.cell_size + self.cell_size // 2, far_y * self.cell_size + self.cell_size // 2), self.cell_size // 2)
    
    def update_simulation(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.screen.fill((255, 255, 255))
            self.draw_map()
            self.draw_start_and_end_points()  # Draw starting and ending points
            
            if self.drone.battery_level > 50:
                move = self.drone.plan_next_move()
                self.drone.move(move)
                self.drone.update_battery()
                self.drone.time_elapsed += 0.1
            else:
                path_to_home = self.drone.return_to_point(self.start_position)
                if path_to_home:
                    next_step = path_to_home[0]
                    move = (next_step[0] - self.drone.position[0], next_step[1] - self.drone.position[1])
                    self.drone.move(move)
                else:
                    # Reached home or couldn't find a path back
                    self.running = False  # End simulation
            
            self.draw_drone()
            self.draw_info()
            pygame.display.flip()
            self.clock.tick(10)

        # Keep the pygame window open
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        
    def draw_info(self):
        battery_text = self.font.render(f"Battery: {self.drone.battery_level:.2f}%", True, (0, 0, 0))
        time_text = self.font.render(f"Flight Time: {self.drone.time_elapsed:.2f} sec", True, (0, 0, 0))
        self.screen.blit(battery_text, (10, self.map_data.shape[0] * self.cell_size + 10))
        self.screen.blit(time_text, (200, self.map_data.shape[0] * self.cell_size + 10))
    
    def draw_drone(self):
        x, y = self.drone.position
        pygame.draw.circle(self.screen, (0, 0, 255), (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2), self.cell_size // 2)
        
        # Draw the trail
        for (tx, ty) in self.drone.path:
            pygame.draw.circle(self.screen, (255, 0, 0), (tx * self.cell_size + self.cell_size // 2, ty * self.cell_size + self.cell_size // 2), self.cell_size // 4)


class Drone:
    def __init__(self, start_position, map_data, far_point):
        self.position = start_position
        self.map_data = map_data
        self.far_point = far_point
        self.battery_level = 100  # Start with full battery
        self.covered_area = set()
        self.path = [start_position]
        self.time_elapsed = 0
        self.current_direction = (1, 0)  # Start moving right
        
    def get_sensor_data(self):
        distances = {
            'up': self._distance_to_obstacle(self.position, (0, -1)),
            'down': self._distance_to_obstacle(self.position, (0, 1)),
            'left': self._distance_to_obstacle(self.position, (-1, 0)),
            'right': self._distance_to_obstacle(self.position, (1, 0)),
            'forward': self._distance_to_obstacle(self.position, (1, 1)),
            'backward': self._distance_to_obstacle(self.position, (-1, -1))
        }
        return distances
    
    def _distance_to_obstacle(self, position, direction):
        x, y = position
        dx, dy = direction
        distance = 0
        while 0 <= x < self.map_data.shape[1] and 0 <= y < self.map_data.shape[0]:
            x += dx
            y += dy
            distance += 1
            if self.map_data[y, x] == 0:
                break
        return distance * 2.5  # Each pixel is 2.5 cm
    
    def move(self, direction):
        x, y = self.position
        dx, dy = direction
        new_position = (x + dx, y + dy)
        if self._is_valid_position(new_position):
            self.position = new_position
            self.covered_area.add(new_position)
            self.path.append(new_position)
            print(f"Moved to new position: {self.position}")
        else:
            print(f"Failed to move to new position: {new_position}, trying different directions")
            # Drone detects an obstacle, try different directions
            possible_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            random.shuffle(possible_directions)
            for d in possible_directions:
                new_position = (x + d[0], y + d[1])
                if self._is_valid_position(new_position):
                    self.position = new_position
                    self.covered_area.add(new_position)
                    self.path.append(new_position)
                    self.current_direction = d
                    print(f"Moved to new position: {self.position} after detecting obstacle")
                    break
    
    def _is_valid_position(self, position):
        x, y = position
        valid = 0 <= x < self.map_data.shape[1] and 0 <= y < self.map_data.shape[0] and self.map_data[y, x] == 1
        print(f"Position {position} is {'valid' if valid else 'invalid'}")
        return valid
    
    def update_battery(self, time_step=1):
        self.battery_level -= (100 / 480) * time_step
        print(f"Battery updated: {self.battery_level:.2f}%")
    
    def plan_next_move(self):
        x, y = self.position
        print(f"Current position: {self.position}, Battery: {self.battery_level:.2f}%")
        
        if self.battery_level > 50:
            # Check if there are unvisited adjacent positions
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
            # Use A* pathfinding to the starting point
            print(f"Battery low, attempting to return to start point: {self.start_position}")
            path_to_start = self.return_to_point(self.start_position)
            if path_to_start:
                next_step = path_to_start[0]
                move = (next_step[0] - self.position[0], next_step[1] - self.position[1])
                print(f"Path to start point: {path_to_start}, Next move: {move}")
                return move
            else:
                print("No valid path found, continuing in current direction")
                return self.current_direction
    
    def return_to_point(self, destination):
        def heuristic(a, b):
            return abs(b[0] - a[0]) + abs(b[1] - a[1])

        start = self.position
        goal = destination
        queue = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        while queue:
            _, current = heapq.heappop(queue)

            if current == goal:
                break

            for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_position = (current[0] + direction[0], current[1] + direction[1])
                if not self._is_valid_position(next_position):
                    continue
                new_cost = cost_so_far[current] + 1
                if next_position not in cost_so_far or new_cost < cost_so_far[next_position]:
                    cost_so_far[next_position] = new_cost
                    priority = new_cost + heuristic(goal, next_position)
                    heapq.heappush(queue, (priority, next_position))
                    came_from[next_position] = current

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                print("Failed to find a valid path")
                return []  # Return an empty path if no valid path is found

        path.append(start)
        path.reverse()

        print(f"Path found: {path}")
        return path

# Define the main function
def main():
    # Create the map and start the simulation
    map_size = (200, 200)
    map_data = np.ones(map_size)

    # Add complex obstacles
    for i in range(30, 170):
        map_data[i, 30] = 0  # Vertical wall
        map_data[i, 170] = 0  # Vertical wall

    for i in range(30, 170):
        map_data[30, i] = 0  # Horizontal wall
        map_data[170, i] = 0  # Horizontal wall

    # Additional complex obstacles
    for i in range(60, 140):
        map_data[i, 100] = 0  # Vertical wall in the middle

    for i in range(100, 160):
        map_data[140, i] = 0  # Horizontal wall in the middle

    for i in range(40, 160):
        map_data[60, i] = 0  # Horizontal wall

    for i in range(60, 140):
        map_data[i, 60] = 0  # Vertical wall

    start_position = (100, 100)
    far_point = (150, 150)  # Define the far point

    # Initialize the simulator with the far point
    simulator = DroneSimulator(map_data, start_position, far_point)

if __name__ == "__main__":
    main()
