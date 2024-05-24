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
        start_x, start_y = self.start_position
        pygame.draw.circle(self.screen, (0, 255, 0), (start_x * self.cell_size + self.cell_size // 2, start_y * self.cell_size + self.cell_size // 2), self.cell_size // 2)
        
        far_x, far_y = self.far_point
        pygame.draw.circle(self.screen, (255, 0, 0), (far_x * self.cell_size + self.cell_size // 2, far_y * self.cell_size + self.cell_size // 2), self.cell_size // 2)
    
    def update_simulation(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.screen.fill((255, 255, 255))
            self.draw_map()
            self.draw_start_and_end_points()
            
            if self.drone.battery_level > 50:
                move = self.drone.plan_next_move()
                self.drone.move(move)
                self.drone.update_battery()
                self.drone.time_elapsed += 0.1
            else:
                if not self.drone.returning_home:
                    self.drone.start_returning_home()
                move = self.drone.return_home()
                if move is None:
                    self.running = False
                else:
                    self.drone.move(move)
            
            self.draw_drone()
            self.draw_info()
            pygame.display.flip()
            self.clock.tick(10)

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
        self.returning_home = False
        self.return_path = []
        
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
        self.returning_home = True
        self.return_path = self.path[::-1]  # Reverse the path to go back home
        print("Starting to return home, path:", self.return_path)
    
    def return_home(self):
        if not self.return_path:
            print("Reached home or no valid path")
            return None
        
        next_position = self.return_path.pop(0)
        move = (next_position[0] - self.position[0], next_position[1] - self.position[1])
        print(f"Returning home, next move: {move}")
        return move

def main():
    map_size = (200, 200)
    map_data = np.ones(map_size)

    for i in range(30, 170):
        map_data[i, 30] = 0  # Vertical wall
        map_data[i, 170] = 0  # Vertical wall

    for i in range(30, 170):
        map_data[30, i] = 0  # Horizontal wall
        map_data[170, i] = 0  # Horizontal wall

    for i in range(60, 140):
        map_data[i, 100] = 0  # Vertical wall in the middle

    for i in range(100, 160):
        map_data[140, i] = 0  # Horizontal wall in the middle

    for i in range(40, 160):
        map_data[60, i] = 0  # Horizontal wall

    for i in range(60, 140):
        map_data[i, 60] = 0  # Vertical wall

    start_position = (100, 100)
    far_point = (150, 150)

    simulator = DroneSimulator(map_data, start_position, far_point)

if __name__ == "__main__":
    main()
