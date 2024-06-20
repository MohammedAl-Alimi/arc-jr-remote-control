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

# Sensitivity and Deadzone Settings
CONTROL_SETTINGS = {
    'left_stick': {
        'sensitivity': 1.0,    # 0.1 to 2.0 (0.1 = very slow, 2.0 = very fast)
        'deadzone': 0.1,       # 0.0 to 0.5 (0.0 = no deadzone, 0.5 = 50% deadzone)
        'exponential': 1.5     # 1.0 to 3.0 (1.0 = linear, higher = more sensitive at edges)
    },
    'right_stick': {
        'sensitivity': 1.0,
        'deadzone': 0.1,
        'exponential': 1.5
    }
}

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

def apply_deadzone(value, deadzone):
    """Apply deadzone to a stick value"""
    if abs(value) < deadzone:
        return 0.0
    # Normalize the value after deadzone
    sign = 1 if value > 0 else -1
    normalized = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * normalized

def apply_sensitivity(value, sensitivity, exponential):
    """Apply sensitivity and exponential curve to a stick value"""
    # Apply exponential curve for more precise control
    sign = 1 if value > 0 else -1
    abs_value = abs(value)
    curved = abs_value ** exponential
    return sign * curved * sensitivity

def process_stick_input(raw_value, stick_type):
    """Process raw stick input with deadzone, sensitivity, and exponential curve"""
    settings = CONTROL_SETTINGS[stick_type]
    
    # Apply deadzone first
    if abs(raw_value) < settings['deadzone']:
        return 0.0
    
    # Normalize after deadzone
    sign = 1 if raw_value > 0 else -1
    normalized = (abs(raw_value) - settings['deadzone']) / (1.0 - settings['deadzone'])
    normalized = sign * normalized
    
    # Apply sensitivity and exponential curve
    processed = apply_sensitivity(normalized, settings['sensitivity'], settings['exponential'])
    
    # Clamp to valid range
    return max(-1.0, min(1.0, processed))

def adjust_sensitivity(stick_type, new_sensitivity):
    """Adjust sensitivity for a specific stick"""
    if 0.1 <= new_sensitivity <= 2.0:
        CONTROL_SETTINGS[stick_type]['sensitivity'] = new_sensitivity
        print(f"\n⚙️ {stick_type.replace('_', ' ').title()} sensitivity set to: {new_sensitivity}")

def adjust_deadzone(stick_type, new_deadzone):
    """Adjust deadzone for a specific stick"""
    if 0.0 <= new_deadzone <= 0.5:
        CONTROL_SETTINGS[stick_type]['deadzone'] = new_deadzone
        print(f"\n⚙️ {stick_type.replace('_', ' ').title()} deadzone set to: {new_deadzone}")

def adjust_exponential(stick_type, new_exponential):
    """Adjust exponential curve for a specific stick"""
    if 1.0 <= new_exponential <= 3.0:
        CONTROL_SETTINGS[stick_type]['exponential'] = new_exponential
        print(f"\n⚙️ {stick_type.replace('_', ' ').title()} exponential set to: {new_exponential}")

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

def print_control_settings():
    """Print current control settings"""
    print("\n⚙️ Current Control Settings:")
    for stick_type, settings in CONTROL_SETTINGS.items():
        print(f"   {stick_type.replace('_', ' ').title()}:")
        print(f"     Sensitivity: {settings['sensitivity']}")
        print(f"     Deadzone: {settings['deadzone']}")
        print(f"     Exponential: {settings['exponential']}")

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
        print_control_settings()
        print("\n💡 Sensitivity Controls:")
        print("   Left Stick: 1/2/3/4/5/6/7/8/9/0 (sensitivity), Q/W/E/R (deadzone)")
        print("   Right Stick: F/G/H/J/K/L (sensitivity), Z/X/C/V (deadzone)")
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
            
            # Handle keyboard sensitivity adjustments
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: adjust_sensitivity('left_stick', 0.1)
                elif event.key == pygame.K_2: adjust_sensitivity('left_stick', 0.2)
                elif event.key == pygame.K_3: adjust_sensitivity('left_stick', 0.3)
                elif event.key == pygame.K_4: adjust_sensitivity('left_stick', 0.4)
                elif event.key == pygame.K_5: adjust_sensitivity('left_stick', 0.5)
                elif event.key == pygame.K_6: adjust_sensitivity('left_stick', 0.6)
                elif event.key == pygame.K_7: adjust_sensitivity('left_stick', 0.7)
                elif event.key == pygame.K_8: adjust_sensitivity('left_stick', 0.8)
                elif event.key == pygame.K_9: adjust_sensitivity('left_stick', 0.9)
                elif event.key == pygame.K_0: adjust_sensitivity('left_stick', 1.0)
                
                elif event.key == pygame.K_f: adjust_sensitivity('right_stick', 0.1)
                elif event.key == pygame.K_g: adjust_sensitivity('right_stick', 0.2)
                elif event.key == pygame.K_h: adjust_sensitivity('right_stick', 0.3)
                elif event.key == pygame.K_j: adjust_sensitivity('right_stick', 0.4)
                elif event.key == pygame.K_k: adjust_sensitivity('right_stick', 0.5)
                elif event.key == pygame.K_l: adjust_sensitivity('right_stick', 0.6)
                
                # Deadzone adjustments
                elif event.key == pygame.K_q: adjust_deadzone('left_stick', 0.0)
                elif event.key == pygame.K_w: adjust_deadzone('left_stick', 0.1)
                elif event.key == pygame.K_e: adjust_deadzone('left_stick', 0.2)
                elif event.key == pygame.K_r: adjust_deadzone('left_stick', 0.3)
                
                elif event.key == pygame.K_z: adjust_deadzone('right_stick', 0.0)
                elif event.key == pygame.K_x: adjust_deadzone('right_stick', 0.1)
                elif event.key == pygame.K_c: adjust_deadzone('right_stick', 0.2)
                elif event.key == pygame.K_v: adjust_deadzone('right_stick', 0.3)
        
        # Reset values each frame
        lx, ly, rx, ry = 0.0, 0.0, 0.0, 0.0
        
        if controller_connected:
            # Check if controller got disconnecgited
            if pygame.joystick.get_count() == 0:
                controller_connected = False
                keyboard_active = True
                print("⚠️ Controller disconnected! Falling back to WASD keyboard controls.")
            
            # Read controller axes if still connected
            if controller_connected:
                # Get raw values and apply processing
                raw_lx = joystick.get_axis(0)
                raw_ly = joystick.get_axis(1)
                raw_rx = joystick.get_axis(2)
                raw_ry = joystick.get_axis(3)
                
                # Apply deadzone, sensitivity, and exponential curve
                lx = process_stick_input(raw_lx, 'left_stick')
                ly = process_stick_input(raw_ly, 'left_stick')
                rx = process_stick_input(raw_rx, 'right_stick')
                ry = process_stick_input(raw_ry, 'right_stick')
        
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