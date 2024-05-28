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
        
        #Drone Stuff
        battery_text_rect = battery_text.get_rect(center=(self.sidebar_width // 2, 100))
        time_text_rect = time_text.get_rect(center=(self.sidebar_width // 2, 140))
        state_text_rect = state_text.get_rect(center=(self.sidebar_width // 2, 180))

        self.screen.blit(battery_text, battery_text_rect)
        self.screen.blit(time_text, time_text_rect)
        self.screen.blit(state_text, state_text_rect)

        #Sensors
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