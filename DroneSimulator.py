import pygame
import time
from Drone import Drone

class DroneSimulator:
    def __init__(self, map_data, start_position, far_point):
        pygame.init()
        self.map_data = map_data
        self.start_position = start_position
        self.far_point = far_point
        self.drone = Drone(start_position, map_data, far_point)
        self.sidebar_width = 500  # Width of the sidebar for data display
        self.screen_info = pygame.display.Info()
        self.screen_width = self.screen_info.current_w
        self.screen_height = self.screen_info.current_h

        # Calculate initial cell size
        self.cell_size = min(self.screen_height // self.map_data.shape[0], self.screen_width // (self.map_data.shape[1] + self.sidebar_width // 10))
        self.screen_size = (self.screen_width, self.screen_height)
        
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Drone Simulator")
        
        self.font = pygame.font.SysFont(None, 24)
        self.exit_button = pygame.Rect(self.sidebar_width - 40, 10, 30, 30)
        
        self.running = True
        self.clock = pygame.time.Clock()
        self.fullscreen = False

        # Load the drone image
        self.drone_image = pygame.image.load("drone_2646511.png").convert_alpha()
        self.drone_image = pygame.transform.scale(self.drone_image, (self.cell_size * 4, self.cell_size * 4))
        
        self.update_simulation()
    
    def draw_map(self):
        """Draw the map."""
        for y in range(self.map_data.shape[0]):
            for x in range(self.map_data.shape[1]):
                color = (255, 255, 255) if self.map_data[y, x] == 1 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, pygame.Rect(x * self.cell_size + self.sidebar_width, y * self.cell_size, self.cell_size, self.cell_size))
    
    def draw_start_and_end_points(self):
        """Draw the start and end points."""
        start_x, start_y = self.start_position
        pygame.draw.circle(self.screen, (0, 255, 0), (start_x * self.cell_size + self.cell_size // 2 + self.sidebar_width, start_y * self.cell_size + self.cell_size // 2), self.cell_size)
        
        far_x, far_y = self.far_point
        pygame.draw.circle(self.screen, (255, 0, 0), (far_x * self.cell_size + self.cell_size // 2 + self.sidebar_width, far_y * self.cell_size + self.cell_size // 2), self.cell_size)
    
    def update_simulation(self):
        """Update the simulation."""
        takeoff_displayed = False
        landing_displayed = False

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_width, self.screen_height = event.size
                    self.cell_size = min(self.screen_height // self.map_data.shape[0], self.screen_width // (self.map_data.shape[1] + self.sidebar_width // 10))
                    self.screen_size = (self.screen_width, self.screen_height)
                    self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
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
        """Draw the sidebar information."""
        pygame.draw.rect(self.screen, (204, 255, 255), pygame.Rect(0, 0, self.sidebar_width, self.screen.get_height()))
        
        battery_text = self.font.render(f"Battery: {self.drone.battery_level:.2f}%", True, (0, 0, 0))
        time_text = self.font.render(f"Flight Time: {self.drone.time_elapsed:.2f} sec", True, (0, 0, 0))

        sensors_header = self.font.render(f"Sensors Information", True, (0, 0, 204))

        sensors = self.drone.get_sensor_data()
        tof_text = self.font.render(
            f"ToF Ranger: "
            f"d0={sensors['d0']:.2f} "
            f"d1={sensors['d1']:.2f} "
            f"d2={sensors['d2']:.2f} "
            f"d3={sensors['d3']:.2f} "
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
        sensors_header_rect = sensors_header.get_rect(center=(self.sidebar_width // 2, 260))
        tof_text_rect = tof_text.get_rect(center=(self.sidebar_width // 2, 300))
        baro_text_rect = baro_text.get_rect(center=(self.sidebar_width // 2, 340))
        imu_gyro_text_rect = imu_gyro_text.get_rect(center=(self.sidebar_width // 2, 380))
        imu_acc_text_rect = imu_acc_text.get_rect(center=(self.sidebar_width // 2, 420))
        optical_flow_text_rect = optical_flow_text.get_rect(center=(self.sidebar_width // 2, 460))

        self.screen.blit(sensors_header, sensors_header_rect)
        self.screen.blit(tof_text, tof_text_rect)
        self.screen.blit(baro_text, baro_text_rect)
        self.screen.blit(imu_gyro_text, imu_gyro_text_rect)
        self.screen.blit(imu_acc_text, imu_acc_text_rect)
        self.screen.blit(optical_flow_text, optical_flow_text_rect)
    
    def draw_drone(self):
        """Draw the drone and its path."""
        x, y = self.drone.position

        # Draw the path first
        for (tx, ty) in self.drone.path:
            pygame.draw.circle(self.screen, (255, 0, 0), (tx * self.cell_size + self.cell_size // 2 + self.sidebar_width, ty * self.cell_size + self.cell_size // 2),
                               self.cell_size // 2)

        # Calculate the position to center the image on the cell
        drone_rect = self.drone_image.get_rect(center=(x * self.cell_size + self.sidebar_width + self.cell_size // 2, y * self.cell_size + self.cell_size // 2))
        self.screen.blit(self.drone_image, drone_rect)

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
