# Arduino Rover Communication

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

## Installation

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
   - Left Stick: Movement control
   - Right Stick: Camera/rotation control
   - Automatically falls back to keyboard if controller disconnects

   **Keyboard (Fallback):**
   - W: Forward
   - S: Backward
   - A: Left
   - D: Right
   - Hold Shift + WASD: Right stick emulation (camera control)
   - Ctrl+C: Quit program

### Command Format
The ground station sends these commands to the rover:
- FORWARD
- BACKWARD
- LEFT
- RIGHT
- STOP

## Project Structure

```
.
├── arduino/
│   ├── rover_communication/           # Original telemetry code
│   │   └── rover_communication.ino
│   └── ground_station_control/        # New keyboard control code
│       └── ground_station_control.ino
├── Controller/
│   └── controller.py                  # Python control interface
└── .vscode/                          # VS Code configuration
    ├── arduino.json                  # Arduino settings
    └── c_cpp_properties.json         # C++ configuration
```

## Current Tasks

1. Ground Station Control (In Progress)
   - [x] Arduino code for receiving and transmitting commands
   - [x] Python interface for keyboard control
   - [x] Controller support with automatic fallback
   - [ ] Testing and debugging

2. Rover Control
   - [ ] Implement command processing on rover
   - [ ] Motor control implementation
   - [ ] Testing and debugging

## Troubleshooting

1. Radio Not Responding:
   - Check nRF24L01+ connections
   - Verify 3.3V power supply
   - Reset Arduino

2. No Serial Communication:
   - Verify correct port selection
   - Check baud rate (115200)
   - Reset Arduino

3. Command Not Received:
   - Verify radio channel settings match (76)
   - Check data rate settings (250KBPS)
   - Ensure both radios are powered

4. Controller Issues:
   - Ensure pygame is installed
   - Check controller connection
   - Verify controller is recognized by system
   - If controller disconnects, keyboard controls will activate automatically 