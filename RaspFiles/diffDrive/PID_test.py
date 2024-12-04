import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

class MotorWithPID:
    def __init__(self, Kp=0.1, Ki=0.01, Kd=0.2):
        # Motor Parameters
        self.time_constant = 0.1  # Motor time constant
        self.K = 1.0             # Motor gain
        
        # PID Parameters
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        # PID State
        self.last_error = 0
        self.integral = 0
        self.last_time = 0
        
        # Motor State
        self.current_speed = 0
        
        # Simulate motor imperfections
        self.efficiency = np.random.uniform(0.9, 1.0)  # Random efficiency factor
        
    def update(self, target_speed, current_time, dt):
        # Calculate error
        error = target_speed - self.current_speed
        
        # PID calculations
        self.integral += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0
        
        # Calculate control signal
        control = (self.Kp * error + 
                  self.Ki * self.integral + 
                  self.Kd * derivative)
        
        # Update motor speed (simple first-order dynamics)
        speed_change = (control - self.current_speed) * dt / self.time_constant
        self.current_speed += speed_change * self.efficiency
        
        # Store values for next iteration
        self.last_error = error
        self.last_time = current_time
        
        return self.current_speed

class DifferentialDriveRobot:
    def __init__(self, use_pid=False):
        # Robot parameters
        self.wheel_radius = 0.05  # meters
        self.wheel_base = 0.2     # meters
        
        # Create motors
        self.left_motor = MotorWithPID(Kp=2.0, Ki=0.5, Kd=0.1)
        self.right_motor = MotorWithPID(Kp=2.0, Ki=0.5, Kd=0.1)
        
        self.use_pid = use_pid
        self.x = 0
        self.y = 0
        self.theta = 0
        
    def update(self, target_speed, t, dt):
        if self.use_pid:
            # With PID control
            left_speed = self.left_motor.update(target_speed, t, dt)
            right_speed = self.right_motor.update(target_speed, t, dt)
        else:
            # Without PID control - direct motor control with imperfections
            left_speed = target_speed * self.left_motor.efficiency
            right_speed = target_speed * self.right_motor.efficiency
            
        # Calculate robot motion
        v = self.wheel_radius * (left_speed + right_speed) / 2
        omega = self.wheel_radius * (right_speed - left_speed) / self.wheel_base
        
        # Update robot position
        self.theta += omega * dt
        self.x += v * np.cos(self.theta) * dt
        self.y += v * np.sin(self.theta) * dt
        
        return self.x, self.y, self.theta, left_speed, right_speed

# Simulation
def run_simulation(use_pid=False):
    # Create robot
    robot = DifferentialDriveRobot(use_pid=use_pid)
    
    # Simulation parameters
    t = np.linspace(0, 5, 500)  # 5 seconds simulation
    dt = t[1] - t[0]
    target_speed = 1.0  # target speed in rad/s
    
    # Storage for results
    x_hist = []
    y_hist = []
    left_speeds = []
    right_speeds = []
    
    # Run simulation
    for time in t:
        x, y, theta, left_speed, right_speed = robot.update(target_speed, time, dt)
        x_hist.append(x)
        y_hist.append(y)
        left_speeds.append(left_speed)
        right_speeds.append(right_speed)
    
    return np.array(x_hist), np.array(y_hist), np.array(left_speeds), np.array(right_speeds), t

# Run simulations and plot results
x_no_pid, y_no_pid, left_no_pid, right_no_pid, t = run_simulation(use_pid=False)
x_pid, y_pid, left_pid, right_pid, t = run_simulation(use_pid=True)

# Plot results
plt.figure(figsize=(15, 10))

# Plot trajectories
plt.subplot(2, 1, 1)
plt.plot(x_no_pid, y_no_pid, 'r-', label='Without PID')
#plt.plot(x_pid, y_pid, 'b-', label='With PID')
plt.title('Robot Trajectory')
plt.xlabel('X Position (m)')
plt.ylabel('Y Position (m)')
plt.grid(True)
plt.legend()
plt.axis('equal')

# Plot motor speeds
plt.subplot(2, 1, 2)
plt.plot(t, left_no_pid, 'r--', label='Left Motor (No PID)')
plt.plot(t, right_no_pid, 'r:', label='Right Motor (No PID)')
plt.plot(t, left_pid, 'b--', label='Left Motor (PID)')
plt.plot(t, right_pid, 'b:', label='Right Motor (PID)')
plt.title('Motor Speeds')
plt.xlabel('Time (s)')
plt.ylabel('Speed (rad/s)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()