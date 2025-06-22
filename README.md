# Arduino Rover Communication : For the Arc Jr Project 2025 : Team FireFlies

This project implements the Arc Jr project's ground station control system, enabling both controller and keyboard-based control of the rover using nRF24L01+ radio module.

## Hardware Requirements

- Arduino Uno
- nRF24L01+ radio module
- Connecting wires
- Optional: Game Controller (for enhanced control)

## Pin Connections

nRF24L01+ to Arduino Uno:
- CE -> Pin 9
- CSN -> Pin 10
- MOSI -> Pin 11 (SPI)
- MISO -> Pin 12 (SPI)
- SCK -> Pin 13 (SPI)
- VCC -> 3.3V
- GND -> GND

## Software Requirements

1. Arduino IDE (2.x or later)
2. Required Libraries:
   - RF24 library
   - SPI library (included with Arduino IDE)
3. Python 3.x (for ground station control interface)
4. Required Python packages:
   - pyserial
   - keyboard
   - pygame (for controller support)

## Installation ::

1. Install the RF24 library in Arduino IDE:
   - Tools > Manage Libraries
   - Search for "RF24"
   - Install the library by TMRh20

2. Connect the Arduino Uno to your computer

3. Upload the ground station code:
   - Open `arduino/ground_station_control/ground_station_control.ino`
   - Select board: Tools > Board > Arduino AVR Boards > Arduino Uno
   - Select port: Tools > Port > (your Arduino port)
   - Click Upload

4. Install Python requirements:
```bash
pip install pyserial keyboard pygame
```

## Usage

### Ground Station Control

1. Run the Python control interface:
```bash
python Controller/controller.py
```

2. Control Methods:

   **Game Controller:**
   - **Left Stick**: Movement control (forward/backward/left/right)
   - **Right Stick**: Camera/rotation control
   - **A Button**: Emergency STOP
   - **B Button**: Toggle between manual/autonomous mode
   - **X Button**: Tilt camera up
   - **Y Button**: Tilt camera down
   - **Left Bumper (LB)**: Low speed mode
   - **Right Bumper (RB)**: High speed mode
   - **Left Trigger (LT)**: Raise arm (if applicable)
   - **Right Trigger (RT)**: Lower arm (if applicable)
   - **Start Button**: Calibration mode
   - **Back Button**: Reset rover
   - Automatically falls back to keyboard if controller disconnects

   **Keyboard (Fallback):**
   - **W/S**: Forward/Backward
   - **A/D**: Left/Right
   - **Shift + WASD**: Right stick emulation (camera control)
   - **Space**: Emergency STOP (A button equivalent)
   - **Tab**: Toggle mode (B button equivalent)
   - **Q**: Camera up (X button equivalent)
   - **E**: Camera down (Y button equivalent)
   - **Ctrl+C**: Quit program

### Sensitivity and Deadzone Controls

The controller supports real-time adjustment of stick sensitivity and deadzone settings:

**Left Stick Controls:**
- **Sensitivity**: Keys 1-0 (0.1 to 1.0)
- **Deadzone**: Keys Q/W/E/R (0.0 to 0.3)

**Right Stick Controls:**
- **Sensitivity**: Keys F/G/H/J/K/L (0.1 to 0.6)
- **Deadzone**: Keys Z/X/C/V (0.0 to 0.3)

**Settings Explained:**
- **Sensitivity**: Controls how responsive the stick is (0.1 = very slow, 1.0 = normal, 2.0 = very fast)
- **Deadzone**: Prevents drift by ignoring small movements (0.0 = no deadzone, 0.5 = 50% deadzone)
- **Exponential**: Adjusts the response curve (1.0 = linear, higher = more sensitive at edges)

### Button Mapping Reference

| Controller Button | Action | Keyboard Equivalent |
|------------------|--------|-------------------|
| A | Emergency STOP | Space |
| B | Toggle Mode | Tab |
| X | Camera Up | Q |
| Y | Camera Down | E |
| LB | Low Speed | - |
| RB | High Speed | - |
| LT | Arm Up | - |
| RT | Arm Down | - |
| START | Calibrate | - |
| BACK | Reset | - |

### Command Format
The ground station sends these commands to the rover:
- **Movement**: FORWARD, BACKWARD, LEFT, RIGHT, STOP
- **Special Actions**: TOGGLE_MODE, CAMERA_UP, CAMERA_DOWN, SPEED_LOW, SPEED_HIGH, ARM_UP, ARM_DOWN, CALIBRATE, RESET

## Project Structure

```
.
├── arduino/
│   ├── rover_communication/           # Original telemetry code
│   │   └── rover_communication.ino
│   └── ground_station_control/        # New keyboard control code
│       └── ground_station_control.ino
├── Controller/
│   └── controller.py                  # Python control interface with button mapping
└── .vscode/                          # VS Code configuration
    ├── arduino.json                  # Arduino settings
    └── c_cpp_properties.json         # C++ configuration
```

## Features

### Core Functionality
- **Dual Input Support**: Seamless switching between controller and keyboard
- **Button Mapping**: Comprehensive mapping of all controller buttons to rover actions
- **Automatic Fallback**: Keyboard controls activate when controller disconnects
- **Real-time Feedback**: Console output showing current input values and button presses
- **Sensitivity Control**: Adjustable stick sensitivity for fine-tuned control
- **Deadzone Management**: Configurable deadzones to prevent stick drift
- **Exponential Response**: Customizable response curves for precise control

### Button Actions
- **Emergency Stop**: Immediate halt of all rover movement
- **Mode Toggle**: Switch between manual and autonomous control modes
- **Camera Control**: Independent camera tilt controls
- **Speed Control**: Variable speed modes for different terrains
- **Arm Control**: Robotic arm manipulation (if hardware supports it)
- **System Functions**: Calibration and reset capabilities

## Current Tasks

1. Ground Station Control (Completed)
   - [x] Arduino code for receiving and transmitting commands
   - [x] Python interface for keyboard control
   - [x] Controller support with automatic fallback
   - [x] Button mapping for all controller inputs
   - [ ] Testing and debugging

2. Rover Control
   - [ ] Implement command processing on rover
   - [ ] Motor control implementation
   - [ ] Testing and debugging

## Troubleshooting

1. **Radio Not Responding:**
   - Check nRF24L01+ connections
   - Verify 3.3V power supply
   - Reset Arduino

2. **No Serial Communication:**
   - Verify correct port selection
   - Check baud rate (115200)
   - Reset Arduino

3. **Command Not Received:**
   - Verify radio channel settings match (76)
   - Check data rate settings (250KBPS)
   - Ensure both radios are powered

4. **Controller Issues:**
   - Ensure pygame is installed
   - Check controller connection
   - Verify controller is recognized by system
   - If controller disconnects, keyboard controls will activate automatically

5. **Button Not Responding:**
   - Check button mapping in console output
   - Verify controller button layout matches expected mapping
   - Test with keyboard equivalents

6. **Stick Too Sensitive/Not Responsive:**
   - Adjust sensitivity using keyboard controls (1-0 for left stick, F-L for right stick)
   - Increase deadzone if experiencing drift (Q-R for left stick, Z-V for right stick)
   - Check exponential settings in the code if needed
   - Verify controller calibration in system settings

## Development Notes

### Button Mapping Implementation
The button mapping system uses Pygame's event system to detect button presses and releases. Each button is mapped to a specific rover action, and the system prevents continuous triggering by tracking button states.

### Controller Layout
The code assumes a standard controller layout (Xbox-style). If using a different controller, button mappings may need adjustment in the `PYGAME_BUTTONS` dictionary.

### Extensibility
New button actions can be easily added by:
1. Adding the action to the `button_actions` dictionary
2. Implementing the corresponding rover command
3. Updating the Arduino code to handle the new command

### Sensitivity System
The sensitivity and deadzone system provides three levels of control:
1. **Deadzone**: Filters out small movements to prevent drift
2. **Sensitivity**: Scales the response magnitude
3. **Exponential**: Adjusts the response curve for fine control

The system processes raw stick input through these stages:
1. Apply deadzone filtering
2. Normalize remaining range
3. Apply sensitivity scaling
4. Apply exponential curve
5. Clamp to valid range (-1.0 to 1.0)

### Real-time Adjustment
Sensitivity and deadzone can be adjusted in real-time using keyboard controls, making it easy to fine-tune the control feel without restarting the program.

feat: add Y-axis inversion toggle for both sticks

- Add invert_y setting to control configuration
- Implement toggle_y_inversion() function
- Add keyboard controls: I (left stick), O (right stick)
- Update process_stick_input() to apply inversion
- Add help text for new controls

This allows users to flip the Y-axis direction for more intuitive control. 