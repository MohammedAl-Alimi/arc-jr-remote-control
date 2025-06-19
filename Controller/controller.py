import pygame
import time
import sys

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Create a small window to capture keyboard input
screen = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Controller Input")

# Default control values
lx, ly, rx, ry = 0.0, 0.0, 0.0, 0.0
controller_connected = False
keyboard_active = False

# Button mapping for rover actions
button_actions = {
    'A': 'STOP',           # Emergency stop
    'B': 'TOGGLE_MODE',    # Toggle between manual/autonomous
    'X': 'CAMERA_UP',      # Tilt camera up
    'Y': 'CAMERA_DOWN',    # Tilt camera down
    'LB': 'SPEED_LOW',     # Low speed mode
    'RB': 'SPEED_HIGH',    # High speed mode
    'LT': 'ARM_UP',        # Raise arm (if applicable)
    'RT': 'ARM_DOWN',      # Lower arm (if applicable)
    'START': 'CALIBRATE',  # Calibration mode
    'BACK': 'RESET'        # Reset rover
}

# Button states (to prevent continuous triggering)
button_states = {action: False for action in button_actions.values()}

# Pygame button mappings (common controller layout)
PYGAME_BUTTONS = {
    0: 'A',      # A button
    1: 'B',      # B button
    2: 'X',      # X button
    3: 'Y',      # Y button
    4: 'LB',     # Left bumper
    5: 'RB',     # Right bumper
    6: 'BACK',   # Back/Select button
    7: 'START',  # Start button
}

# Trigger mappings
TRIGGER_AXES = {
    4: 'LT',     # Left trigger
    5: 'RT',     # Right trigger
}

def handle_button_press(button_name):
    """Handle button press and return the corresponding action"""
    if button_name in button_actions:
        action = button_actions[button_name]
        if not button_states[action]:  # Only trigger once per press
            button_states[action] = True
            print(f"\n🔘 Button {button_name} pressed: {action}")
            return action
    return None

def handle_button_release(button_name):
    """Handle button release"""
    if button_name in button_actions:
        action = button_actions[button_name]
        button_states[action] = False
        print(f"\n🔘 Button {button_name} released: {action}")

# Try to initialize controller
if pygame.joystick.get_count() > 0:
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        controller_connected = True
        print("🎮 Controller connected:", joystick.get_name())
        print("🔁 Reading both sticks (left + right)...")
        print("🔘 Button mapping enabled:")
        for button, action in button_actions.items():
            print(f"   {button}: {action}")
    except:
        controller_connected = False

if not controller_connected:
    print("❌ No controller detected. Falling back to WASD keyboard controls.")
    print("Usage: W/S for forward/backward, A/D for left/right")
    print("Hold Shift for right stick emulation (camera control)")
    keyboard_active = True

try:
    while True:
        # Process all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle button events
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in PYGAME_BUTTONS:
                    button_name = PYGAME_BUTTONS[event.button]
                    handle_button_press(button_name)
            
            elif event.type == pygame.JOYBUTTONUP:
                if event.button in PYGAME_BUTTONS:
                    button_name = PYGAME_BUTTONS[event.button]
                    handle_button_release(button_name)
            
            # Handle trigger events
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis in TRIGGER_AXES:
                    trigger_name = TRIGGER_AXES[event.axis]
                    # Triggers typically range from -1 (not pressed) to 1 (fully pressed)
                    if event.value > 0.5:  # Trigger threshold
                        handle_button_press(trigger_name)
                    elif event.value < 0.1:  # Release threshold
                        handle_button_release(trigger_name)
        
        # Reset values each frame
        lx, ly, rx, ry = 0.0, 0.0, 0.0, 0.0
        
        if controller_connected:
            # Check if controller got disconnected
            if pygame.joystick.get_count() == 0:
                controller_connected = False
                keyboard_active = True
                print("⚠️ Controller disconnected! Falling back to WASD keyboard controls.")
            
            # Read controller axes if still connected
            if controller_connected:
                lx = joystick.get_axis(0)
                ly = joystick.get_axis(1)
                rx = joystick.get_axis(2)
                ry = joystick.get_axis(3)
        
        if keyboard_active:
            # Check if controller got reconnected
            if pygame.joystick.get_count() > 0 and not controller_connected:
                try:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    controller_connected = True
                    keyboard_active = False
                    print("🎮 Controller reconnected! Switching back to controller input.")
                except:
                    pass
            
            # Read keyboard inputs if no controller
            if keyboard_active:
                keys = pygame.key.get_pressed()
                
                # Left stick emulation (movement)
                if keys[pygame.K_w]: ly = -1.0
                if keys[pygame.K_s]: ly = 1.0
                if keys[pygame.K_a]: lx = -1.0
                if keys[pygame.K_d]: lx = 1.0
                
                # Right stick emulation (hold Shift + WASD)
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    if keys[pygame.K_w]: ry = -1.0
                    if keys[pygame.K_s]: ry = 1.0
                    if keys[pygame.K_a]: rx = -1.0
                    if keys[pygame.K_d]: rx = 1.0
                
                # Keyboard button mapping (for testing without controller)
                if keys[pygame.K_SPACE]:  # Space = A button (STOP)
                    handle_button_press('A')
                if keys[pygame.K_TAB]:   # Tab = B button (TOGGLE_MODE)
                    handle_button_press('B')
                if keys[pygame.K_q]:     # Q = X button (CAMERA_UP)
                    handle_button_press('X')
                if keys[pygame.K_e]:     # E = Y button (CAMERA_DOWN)
                    handle_button_press('Y')
        
        # Print the current control values
        print(f"🕹️  Left Stick: X={lx:.2f}  Y={ly:.2f}    |    Right Stick: X={rx:.2f}  Y={ry:.2f}", end='\r')
        
        # Small delay to prevent high CPU usage
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
    pygame.quit()
    sys.exit()