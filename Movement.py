import pygame
import numpy as np
import heapq
from collections import defaultdict
import time
import random

class DroneSimulator:
    def __init__(self, map_data, start_position, far_point):
        pygame.init()
        self.map_data = map_data
        self.start_position = start_position
        self.far_point = far_point
        self.drone = Drone(start_position, map_data, far_point)
        self.cell_size = 8  # Size of each cell in the grid for better visibility
        self.sidebar_width = 300  # Width of the sidebar for data display
        self.screen_size = (map_data.shape[1] * self.cell_size + self.sidebar_width, map_data.shape[0] * self.cell_size)
        
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Drone Simulator")
        
        self.font = pygame.font.SysFont(None, 24)
        self.exit_button = pygame.Rect(self.sidebar_width - 40, 10, 30, 30)
        
        self.running = True
        self.clock = pygame.time.Clock()
        self.fullscreen = False
        
        self.update_simulation()
    
    def draw_map(self):
        for y in range(self.map_data.shape[0]):
            for x in range(self.map_data.shape[1]):
                color = (255, 255, 255) if self.map_data[y, x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, pygame.Rect(x * self.cell_size + self.sidebar_width, y * self.cell_size, self.cell_size, self.cell_size))
    
    def draw_start_and_end_points(self):
        start_x, start_y = self.start_position
        pygame.draw.circle(self.screen, (0, 255, 0), (start_x * self.cell_size + self.cell_size // 2 + self.sidebar_width, start_y * self.cell_size + self.cell_size // 2), self.cell_size)
        
        far_x, far_y = self.far_point
        pygame.draw.circle(self.screen, (255, 0, 0), (far_x * self.cell_size + self.cell_size // 2 + self.sidebar_width, far_y * self.cell_size + self.cell_size // 2), self.cell_size)
    
    def update_simulation(self):
        takeoff_displayed = False
        landing_displayed = False

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.exit_button.collidepoint(event.pos):
                        self.running = False
            
            self.screen.fill((255, 255, 255))
            self.draw_map()
            self.draw_start_and_end_points()
            
            if self.drone.flight_state == "Taking off" and not takeoff_displayed:
                self.draw_drone()
                self.draw_info()
                pygame.display.flip()
                time.sleep(2)
                takeoff_displayed = True
                self.drone.takeoff()
                self.drone.flight_state = "Flying"
            elif self.drone.battery_level > 50 and self.drone.flight_state == "Flying":
                move = self.drone.plan_next_move()
                self.drone.move(move)
                self.drone.update_battery()
                self.drone.time_elapsed += 0.1
            elif self.drone.battery_level <= 50 and self.drone.flight_state == "Flying":
                self.drone.start_returning_home()
                self.drone.flight_state = "Returning home"
            elif self.drone.flight_state == "Returning home":
                move = self.drone.return_home()
                if move is None:
                    self.drone.flight_state = "Landing"
                else:
                    self.drone.move(move)
                    self.drone.update_battery()
                    self.drone.time_elapsed += 0.1
            elif self.drone.flight_state == "Landing" and not landing_displayed:
                self.draw_drone()
                self.draw_info()
                pygame.display.flip()
                time.sleep(2)
                landing_displayed = True
                self.drone.land()
                self.drone.flight_state = "Landed"
            
            self.draw_drone()
            self.draw_info()
            pygame.display.flip()
            self.clock.tick(10)
    
    def draw_info(self):
        pygame.draw.rect(self.screen, (200, 200, 200), pygame.Rect(0, 0, self.sidebar_width, self.screen.get_height()))
        
        battery_text = self.font.render(f"Battery: {self.drone.battery_level:.2f}%", True, (0, 0, 0))
        time_text = self.font.render(f"Flight Time: {self.drone.time_elapsed:.2f} sec", True, (0, 0, 0))
        
        sensors = self.drone.get_sensor_data()
        tof_text = self.font.render(
            f"ToF Ranger:"
            f"d0={sensors['d0']:.2f}"
            f"d1={sensors['d1']:.2f}"
            f"d2={sensors['d2']:.2f}"
            f"d3={sensors['d3']:.2f}"
            f"d4={sensors['d4']:.2f}", True, (0, 0, 0))
        baro_text = self.font.render(f"Barometer: baro={sensors['baro']:.2f}", True, (0, 0, 0))
        imu_gyro_text = self.font.render(f"IMU (gyro): yaw={sensors['yaw']:.2f}", True, (0, 0, 0))
        imu_acc_text = self.font.render(f"IMU (acc): pitch={sensors['pitch']:.2f} roll={sensors['roll']:.2f} accX={sensors['accX']:.2f} accY={sensors['accY']:.2f} accZ={sensors['accZ']:.2f}", True, (0, 0, 0))
        optical_flow_text = self.font.render(f"Optical Flow: Vx={sensors['Vx']:.2f} Vy={sensors['Vy']:.2f}", True, (0, 0, 0))
        
        state_text = self.font.render(f"State: {self.drone.flight_state}", True, (0, 0, 0))
        
        # Drone Info
        battery_text_rect = battery_text.get_rect(center=(self.sidebar_width // 2, 100))
        time_text_rect = time_text.get_rect(center=(self.sidebar_width // 2, 140))
        state_text_rect = state_text.get_rect(center=(self.sidebar_width // 2, 180))

        self.screen.blit(battery_text, battery_text_rect)
        self.screen.blit(time_text, time_text_rect)
        self.screen.blit(state_text, state_text_rect)

        # Sensors Info
        tof_text_rect = tof_text.get_rect(topleft=(10, 260))
        baro_text_rect = baro_text.get_rect(topleft=(10, 300))
        imu_gyro_text_rect = imu_gyro_text.get_rect(topleft=(10, 340))
        imu_acc_text_rect = imu_acc_text.get_rect(topleft=(10, 380))
        optical_flow_text_rect = optical_flow_text.get_rect(topleft=(10, 420))

        self.screen.blit(tof_text, tof_text_rect)
        self.screen.blit(baro_text, baro_text_rect)
        self.screen.blit(imu_gyro_text, imu_gyro_text_rect)
        self.screen.blit(imu_acc_text, imu_acc_text_rect)
        self.screen.blit(optical_flow_text, optical_flow_text_rect)
    
    def draw_drone(self):
        x, y = self.drone.position
        pygame.draw.circle(self.screen, (0, 0, 255), (x * self.cell_size + self.cell_size // 2 + self.sidebar_width, y * self.cell_size + self.cell_size // 2), self.cell_size)
        
        for (tx, ty) in self.drone.path:
            pygame.draw.circle(self.screen, (255, 0, 0), (tx * self.cell_size + self.cell_size // 2 + self.sidebar_width, ty * self.cell_size + self.cell_size // 2), self.cell_size // 2)
        
        if self.drone.flight_state == "Taking off":
            takeoff_text = self.font.render("Taking Off", True, (0, 255, 0))
            self.screen.blit(takeoff_text, (x * self.cell_size + self.cell_size // 2 + self.sidebar_width - 20, y * self.cell_size + self.cell_size // 2 - 20))
        elif self.drone.flight_state == "Flying" or self.drone.flight_state == "Returning home":
            flying_text = self.font.render("Flying", True, (0, 0, 255))
            self.screen.blit(flying_text, (x * self.cell_size + self.cell_size // 2 + self.sidebar_width - 20, y * self.cell_size + self.cell_size // 2 - 20))
        elif self.drone.flight_state == "Landing":
            landing_text = self.font.render("Landing", True, (255, 0, 0))
            self.screen.blit(landing_text, (x * self.cell_size + self.cell_size // 2 + self.sidebar_width - 20, y * self.cell_size + self.cell_size // 2 - 20))
        elif self.drone.flight_state == "Landed":
            landed_text = self.font.render("Landed Safely", True, (0, 255, 0))
            self.screen.blit(landed_text, (x * self.cell_size + self.cell_size // 2 + self.sidebar_width - 40, y * self.cell_size + self.cell_size // 2 - 20))

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
        self.adjacency_list[old_position].append(new_position)
        self.adjacency_list[new_position].append(old_position)
    
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
        self.return_path = self.dijkstra(self.position, self.start_position)
        print("Starting to return home, path:", self.return_path)
    
    def return_home(self):
        if not self.return_path:
            print("Reached home or no valid path")
            return None
        
        next_position = self.return_path.pop(0)
        move = (next_position[0] - self.position[0], next_position[1] - self.position[1])
        print(f"Returning home, next move: {move}")
        return move
    
    def dijkstra(self, start, goal):
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
        dx, dy = direction
        self.velocity = (dx, dy)

    def takeoff(self):
        if self.altitude == 0:
            self.altitude = 1  # Takeoff to a height of 1 meter
            print("Taking off to a height of 1 meter")

    def land(self):
        if self.altitude > 0:
            self.altitude = 0  # Land the drone
            print("Landing the drone")

def main():
    map_size = (150, 150)  # Scaled map size for better visibility
    map_data = np.ones(map_size)

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
