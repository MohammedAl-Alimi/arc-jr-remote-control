# controller.py - Main interface for controlling the Arc Jr rover (Team FireFlies)
# Micro change for July 15th, 2025
# Importing pygame for controller support (July 14th micro-commit)
import pygame
# Importing time for delays and timing (July 13th micro-commit)
import time
# Importing sys for system-specific parameters (July 12th micro-commit)
import sys
# Importing json for configuration (July 11th micro-commit)
import json
# Importing os for file and path operations (July 10th micro-commit)
import os

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
debug_mode = False
auto_center = False
show_fps = False
vibration_enabled = False
color_theme = "default"
sound_enabled = False
fullscreen = False
border_enabled = True
cursor_visible = True
background_color = "black"
window_title = "Controller Input"
volume_level = 50
brightness = 100
contrast = 100
saturation = 100
hue = 0
gamma = 1.0
sharpness = 100

# Command recording and playback
recording = False
playing = False
recorded_commands = []
recording_start_time = 0
playback_index = 0
playback_speed = 1.0
blur = 0
noise = 0
grain = 0
vignette = 0
chromatic = 0
distortion = 0
fisheye = 0
frame_count = 0
last_fps_time = time.time()

# Command history for display
command_history = []
max_history_size = 10

# Controller battery tracking
controller_battery_level = 100.0  # Simulated battery level (0-100%)
battery_drain_rate = 0.01  # Battery drain per frame
last_battery_update = time.time()

# Sensitivity and Deadzone Settings
CONTROL_SETTINGS = {
    'left_stick': {
        'sensitivity': 1.0,    # 0.1 to 2.0 (0.1 = very slow, 2.0 = very fast)
        'deadzone': 0.1,       # 0.0 to 0.5 (0.0 = no deadzone, 0.5 = 50% deadzone)
        'exponential': 1.5,    # 1.0 to 3.0 (1.0 = linear, higher = more sensitive at edges)
        'invert_y': False      # Invert Y-axis
    },
    'right_stick': {
        'sensitivity': 1.0,
        'deadzone': 0.1,
        'exponential': 1.5,
        'invert_y': False      # Invert Y-axis
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

# Main controller class and logic (July 9th micro-commit)
def apply_deadzone(value, deadzone):
    """Apply deadzone to a stick value"""
    if abs(value) < deadzone:
        return 0.0
    # Normalize the value after deadzone
    sign = 1 if value > 0 else -1
    normalized = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * normalized

# Sensitivity adjustment logic (July 8th micro-commit)
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
    
    # Apply Y-axis inversion if enabled
    if settings['invert_y']:
        processed = -processed
    
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

def toggle_y_inversion(stick_type):
    """Toggle Y-axis inversion for a specific stick"""
    CONTROL_SETTINGS[stick_type]['invert_y'] = not CONTROL_SETTINGS[stick_type]['invert_y']
    status = "ON" if CONTROL_SETTINGS[stick_type]['invert_y'] else "OFF"
    print(f"\n🔄 {stick_type.replace('_', ' ').title()} Y-axis inversion: {status}")

def reset_all_settings():
    """Reset all sensitivity and deadzone settings to default values"""
    CONTROL_SETTINGS['left_stick'] = {
        'sensitivity': 1.0,
        'deadzone': 0.1,
        'exponential': 1.5,
        'invert_y': False
    }
    CONTROL_SETTINGS['right_stick'] = {
        'sensitivity': 1.0,
        'deadzone': 0.1,
        'exponential': 1.5,
        'invert_y': False
    }
    print("\n🔄 All settings reset to default values")
    print_control_settings()

def show_help_menu():
    """Display all controls and mappings"""
    current_time = time.strftime("%H:%M:%S")
    print("\n" + "="*50)
    print(f"🎮 CONTROLLER HELP MENU - {current_time}")
    print("="*50)
    print("\n📋 CONTROLLER BUTTONS:")
    for button, action in button_actions.items():
        print(f"   {button}: {action}")
    
    print("\n⚙️ SENSITIVITY CONTROLS:")
    print("   Left Stick Sensitivity: 1/2/3/4/5/6/7/8/9/0")
    print("   Right Stick Sensitivity: F/G/H/J/K/L")
    print("   Left Stick Deadzone: Q/W/E/R")
    print("   Right Stick Deadzone: Z/X/C/V")
    print("   Y-Axis Inversion: I (left), O (right)")
    print("   Exponential Curve: T (left), Y (right)")
    print("   Save Settings: S")
    print("   Debug Mode: D")
    print("   Quick Presets: 1 (slow), 2 (normal), 3 (fast)")
    print("   Auto-Center: C")
    print("   Show FPS: F")
    print("   Vibration: V")
    print("   Color Theme: T")
    print("   Reset All Settings: R")
    print("   Show This Help: H")
    print("\n🎙️ Recording Controls:")
    print("   F1: Start Recording | F2: Stop Recording")
    print("   F3: Start Playback | F4: Stop Playback")
    print("   F5: Clear Recording | F6/F7/F8: Speed (0.5x/1x/2x)")
    
    print("\n⌨️ KEYBOARD CONTROLS (when no controller):")
    print("   Movement: W/S/A/D")
    print("   Camera (hold Shift): Shift + W/S/A/D")
    print("   Emergency Stop: Space")
    print("   Toggle Mode: Tab")
    print("   Camera Up/Down: Q/E")
    
    print("\n🛑 QUIT: Ctrl+C")
    print("="*50)

def toggle_exponential_curve(stick_type):
    """Toggle between linear and exponential response curves"""
    current_exp = CONTROL_SETTINGS[stick_type]['exponential']
    if current_exp == 1.0:
        # Switch to exponential
        CONTROL_SETTINGS[stick_type]['exponential'] = 1.5
        print(f"\n📈 {stick_type.replace('_', ' ').title()} response: Exponential (1.5)")
    else:
        # Switch to linear
        CONTROL_SETTINGS[stick_type]['exponential'] = 1.0
        print(f"\n📈 {stick_type.replace('_', ' ').title()} response: Linear (1.0)")

def handle_button_press(button_name):
    """Handle button press and return the corresponding action"""
    if button_name in button_actions:
        action = button_actions[button_name]
        if not button_states[action]:  # Only trigger once per press
            button_states[action] = True
            print(f"\n🔘 Button {button_name} pressed: {action}")
            
            # Trigger vibration if enabled
            if vibration_enabled and controller_connected:
                try:
                    joystick.rumble(0.5, 0.5, 100)  # Left motor, right motor, duration
                except:
                    pass  # Vibration not supported on this controller
            
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

def save_current_settings():
    """Save current settings to a JSON file"""
    try:
        settings_file = "controller_settings.json"
        with open(settings_file, 'w') as f:
            json.dump(CONTROL_SETTINGS, f, indent=2)
        print(f"\n💾 Settings saved to {settings_file}")
        print("📁 File location:", os.path.abspath(settings_file))
    except Exception as e:
        print(f"\n❌ Error saving settings: {e}")

def load_saved_settings():
    """Load settings from JSON file if it exists"""
    try:
        settings_file = "controller_settings.json"
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                loaded_settings = json.load(f)
                CONTROL_SETTINGS.update(loaded_settings)
            print(f"\n📂 Settings loaded from {settings_file}")
            return True
    except Exception as e:
        print(f"\n❌ Error loading settings: {e}")
    return False

def toggle_debug_mode():
    """Toggle debug mode to show raw vs processed values"""
    global debug_mode
    debug_mode = not debug_mode
    status = "ON" if debug_mode else "OFF"
    print(f"\n🐛 Debug mode: {status}")
    if debug_mode:
        print("   Showing raw vs processed stick values")
    else:
        print("   Showing processed stick values only")

def set_sensitivity_preset(preset_name):
    """Set quick sensitivity presets for both sticks"""
    presets = {
        'slow': {'sensitivity': 0.5, 'deadzone': 0.15, 'exponential': 1.2},
        'normal': {'sensitivity': 1.0, 'deadzone': 0.1, 'exponential': 1.5},
        'fast': {'sensitivity': 1.5, 'deadzone': 0.05, 'exponential': 1.8}
    }
    
    if preset_name in presets:
        preset = presets[preset_name]
        for stick_type in ['left_stick', 'right_stick']:
            CONTROL_SETTINGS[stick_type]['sensitivity'] = preset['sensitivity']
            CONTROL_SETTINGS[stick_type]['deadzone'] = preset['deadzone']
            CONTROL_SETTINGS[stick_type]['exponential'] = preset['exponential']
        
        print(f"\n⚡ Sensitivity preset: {preset_name.upper()}")
        print(f"   Sensitivity: {preset['sensitivity']}")
        print(f"   Deadzone: {preset['deadzone']}")
        print(f"   Exponential: {preset['exponential']}")
        print_control_settings()

def toggle_auto_center():
    """Toggle auto-center mode for sticks"""
    global auto_center
    auto_center = not auto_center
    status = "ON" if auto_center else "OFF"
    print(f"\n🎯 Auto-center mode: {status}")
    if auto_center:
        print("   Sticks will automatically center when released")
    else:
        print("   Sticks will maintain position when released")

def toggle_fps_display():
    """Toggle FPS and performance display"""
    global show_fps
    show_fps = not show_fps
    status = "ON" if show_fps else "OFF"
    print(f"\n📊 FPS display: {status}")
    if show_fps:
        print("   Showing frame rate and performance metrics")
    else:
        print("   Hiding performance metrics")

def toggle_vibration():
    """Toggle controller vibration feedback"""
    global vibration_enabled
    vibration_enabled = not vibration_enabled
    status = "ON" if vibration_enabled else "OFF"
    print(f"\n📳 Vibration feedback: {status}")
    if vibration_enabled:
        print("   Controller will vibrate on button presses")
    else:
        print("   Vibration disabled")

def cycle_color_theme():
    """Cycle through different color themes"""
    global color_theme
    themes = {
        "default": "🎮",
        "space": "🚀", 
        "nature": "🌿",
        "tech": "⚡",
        "gaming": "🎯"
    }
    
    theme_list = list(themes.keys())
    current_index = theme_list.index(color_theme)
    next_index = (current_index + 1) % len(theme_list)
    color_theme = theme_list[next_index]
    
    print(f"\n🎨 Color theme: {color_theme.title()} {themes[color_theme]}")
    print(f"   Console output will use {color_theme} theme")

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    print(f"\n🔊 Sound effects: {'ON' if sound_enabled else 'OFF'}")

def toggle_fullscreen():
    global fullscreen
    fullscreen = not fullscreen
    print(f"\n🖥️ Fullscreen: {'ON' if fullscreen else 'OFF'}")

def toggle_border():
    global border_enabled
    border_enabled = not border_enabled
    print(f"\n🖼️ Border: {'ON' if border_enabled else 'OFF'}")

def toggle_cursor():
    global cursor_visible
    cursor_visible = not cursor_visible
    print(f"\n👆 Cursor: {'ON' if cursor_visible else 'OFF'}")

def toggle_background():
    global background_color
    background_color = "white" if background_color == "black" else "black"
    print(f"\n🎨 Background: {background_color}")

def toggle_title():
    global window_title
    window_title = "Arc Jr Controller" if window_title == "Controller Input" else "Controller Input"
    print(f"\n📝 Title: {window_title}")

def toggle_volume():
    global volume_level
    volume_level = 100 if volume_level == 50 else 50
    print(f"\n🔊 Volume: {volume_level}%")

def toggle_brightness():
    global brightness
    brightness = 50 if brightness == 100 else 100
    print(f"\n💡 Brightness: {brightness}%")

def toggle_contrast():
    global contrast
    contrast = 50 if contrast == 100 else 100
    print(f"\n🎨 Contrast: {contrast}%")

def toggle_saturation():
    global saturation
    saturation = 50 if saturation == 100 else 100
    print(f"\n🌈 Saturation: {saturation}%")

def toggle_hue():
    global hue
    hue = 180 if hue == 0 else 0
    print(f"\n🎨 Hue: {hue}°")

def toggle_gamma():
    global gamma
    gamma = 2.0 if gamma == 1.0 else 1.0
    print(f"\n📊 Gamma: {gamma}")

def toggle_blur():
    global blur
    blur = 5 if blur == 0 else 0
    print(f"\n🌫️ Blur: {blur}")

def toggle_noise():
    global noise
    noise = 10 if noise == 0 else 0
    print(f"\n📻 Noise: {noise}")

def toggle_grain():
    global grain
    grain = 15 if grain == 0 else 0
    print(f"\n🌾 Grain: {grain}")

def toggle_vignette():
    global vignette
    vignette = 20 if vignette == 0 else 0
    print(f"\n🖼️ Vignette: {vignette}")

def toggle_chromatic():
    global chromatic
    chromatic = 5 if chromatic == 0 else 0
    print(f"\n🌈 Chromatic: {chromatic}")

def toggle_distortion():
    global distortion
    distortion = 10 if distortion == 0 else 0
    print(f"\n🌀 Distortion: {distortion}")

def start_recording():
    """Start recording control commands"""
    global recording, recorded_commands, recording_start_time
    recording = True
    recorded_commands = []
    recording_start_time = time.time()
    print(f"\n🎙️ Recording started at {time.strftime('%H:%M:%S')}")
    print("   All stick movements and button presses will be recorded")

def stop_recording():
    """Stop recording and save commands"""
    global recording
    if recording:
        recording = False
        duration = time.time() - recording_start_time
        print(f"\n⏹️ Recording stopped - {len(recorded_commands)} commands captured")
        print(f"   Duration: {duration:.1f} seconds")
        return True
    return False

def start_playback():
    """Start playing back recorded commands"""
    global playing, playback_index
    if recorded_commands and not playing:
        playing = True
        playback_index = 0
        print(f"\n▶️ Playback started - {len(recorded_commands)} commands")
        print(f"   Speed: {playback_speed}x")

def stop_playback():
    """Stop command playback"""
    global playing
    if playing:
        playing = False
        print(f"\n⏹️ Playback stopped at command {playback_index}")

def clear_recording():
    """Clear all recorded commands"""
    global recorded_commands
    recorded_commands = []
    print(f"\n🗑️ Recording cleared")

def set_playback_speed(speed):
    """Set playback speed multiplier"""
    global playback_speed
    playback_speed = speed
    print(f"\n⚡ Playback speed: {playback_speed}x")

def record_command(command_type, values, timestamp):
    """Record a single command with timestamp"""
    if recording:
        recorded_commands.append({
            'type': command_type,
            'values': values.copy(),
            'timestamp': timestamp - recording_start_time
        })

def get_next_playback_command():
    """Get the next command for playback"""
    global playback_index
    if playing and playback_index < len(recorded_commands):
        command = recorded_commands[playback_index]
        playback_index += 1
        return command
    elif playing and playback_index >= len(recorded_commands):
        stop_playback()
        print(f"\n✅ Playback completed")
    return None

def add_to_command_history(command_type, values=None):
    """Add a command to the history for display"""
    global command_history
    timestamp = time.strftime("%H:%M:%S")
    if values:
        command_str = f"{timestamp} - {command_type}: {values}"
    else:
        command_str = f"{timestamp} - {command_type}"
    
    command_history.append(command_str)
    if len(command_history) > max_history_size:
        command_history.pop(0)

def display_command_history():
    """Display the command history"""
    if command_history:
        print("\n📜 Command History:")
        for i, cmd in enumerate(command_history[-5:], 1):  # Show last 5
            print(f"   {i}. {cmd}")
    else:
        print("\n📜 No commands in history")

def update_battery_level():
    """Update controller battery level (simulated)"""
    global controller_battery_level, last_battery_update
    current_time = time.time()
    if current_time - last_battery_update >= 1.0:  # Update every second
        controller_battery_level = max(0.0, controller_battery_level - battery_drain_rate)
        last_battery_update = current_time

def display_battery_level():
    """Display current battery level"""
    battery_icon = "🔋" if controller_battery_level > 20 else "🔴"
    print(f"\n{battery_icon} Controller Battery: {controller_battery_level:.1f}%")
    
    if controller_battery_level < 10:
        print("⚠️  Low battery warning! Consider charging controller.")
    elif controller_battery_level < 25:
        print("🔶 Battery level is getting low.")

def display_connection_status():
    """Display current controller connection status"""
    if controller_connected:
        try:
            controller_name = joystick.get_name()
        except:
            controller_name = "Unknown Controller"
        print(f"\n✅ Controller Connected: {controller_name}")
        print(f"📡 Input Mode: Controller")
        print(f"🎮 Battery: {controller_battery_level:.1f}%")
    else:
        print(f"\n❌ Controller Disconnected")
        print(f"⌨️  Input Mode: Keyboard")
        print(f"🔧 Using WASD controls")

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
        
        # Load saved settings if available
        load_saved_settings()
        
        print_control_settings()
        print("\n💡 Sensitivity Controls:")
        print("   Left Stick: 1/2/3/4/5/6/7/8/9/0 (sensitivity), Q/W/E/R (deadzone)")
        print("   Right Stick: F/G/H/J/K/L (sensitivity), Z/X/C/V (deadzone)")
        print("   Y-Axis Inversion: I (left stick), O (right stick)")
        print("   Exponential Curve: T (left), Y (right)")
        print("   Save Settings: S")
        print("   Debug Mode: D")
        print("   Quick Presets: 1 (slow), 2 (normal), 3 (fast)")
        print("   Auto-Center: C")
        print("   Show FPS: F")
        print("   Vibration: V")
        print("   Color Theme: T")
        print("   Reset All Settings: R")
        print("[MODE] Controller mode active.")
    except:
        controller_connected = False

if not controller_connected:
    print("❌ No controller detected. Falling back to WASD keyboard controls.")
    print("Usage: W/S for forward/backward, A/D for left/right")
    print("Hold Shift for right stick emulation (camera control)")
    print("[MODE] Keyboard mode active.")
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
                
                # Y-axis inversion controls
                elif event.key == pygame.K_i: toggle_y_inversion('left_stick')
                elif event.key == pygame.K_o: toggle_y_inversion('right_stick')
                
                # Exponential curve toggle controls
                elif event.key == pygame.K_t: toggle_exponential_curve('left_stick')
                elif event.key == pygame.K_y: toggle_exponential_curve('right_stick')
                
                # Save settings
                elif event.key == pygame.K_s: save_current_settings()
                
                # Debug mode toggle
                elif event.key == pygame.K_d: toggle_debug_mode()
                
                # Quick sensitivity presets
                elif event.key == pygame.K_1: set_sensitivity_preset('slow')
                elif event.key == pygame.K_2: set_sensitivity_preset('normal')
                elif event.key == pygame.K_3: set_sensitivity_preset('fast')
                
                # Auto-center toggle
                elif event.key == pygame.K_c: toggle_auto_center()
                
                # FPS display toggle
                elif event.key == pygame.K_f: toggle_fps_display()
                
                # Vibration toggle
                elif event.key == pygame.K_v: toggle_vibration()
                
                # Color theme cycling
                elif event.key == pygame.K_t: cycle_color_theme()
                
                # Sound toggle
                elif event.key == pygame.K_s: toggle_sound()
                
                # Fullscreen toggle
                elif event.key == pygame.K_g: toggle_fullscreen()
                
                # Border toggle
                elif event.key == pygame.K_b: toggle_border()
                
                # Cursor toggle
                elif event.key == pygame.K_x: toggle_cursor()
                
                # Recording and playback controls
                elif event.key == pygame.K_F1: start_recording()
                elif event.key == pygame.K_F2: stop_recording()
                elif event.key == pygame.K_F3: start_playback()
                elif event.key == pygame.K_F4: stop_playback()
                elif event.key == pygame.K_F5: clear_recording()
                elif event.key == pygame.K_F6: set_playback_speed(0.5)
                elif event.key == pygame.K_F7: set_playback_speed(1.0)
                elif event.key == pygame.K_F8: set_playback_speed(2.0)
                
                # Reset all settings
                elif event.key == pygame.K_r: reset_all_settings()
                
                # Show help menu
                elif event.key == pygame.K_h: show_help_menu()
                
                # Show command history
                elif event.key == pygame.K_p: display_command_history()
                
                # Show battery level
                elif event.key == pygame.K_m: display_battery_level()
                
                # Show connection status
                elif event.key == pygame.K_n: display_connection_status()
        
        # Reset values each frame
        lx, ly, rx, ry = 0.0, 0.0, 0.0, 0.0
        
        if controller_connected:
            # Check if controller got disconnecgited
            if pygame.joystick.get_count() == 0:
                controller_connected = False
                keyboard_active = True
                print("⚠️ Controller disconnected! Falling back to WASD keyboard controls.")
                print("[MODE] Keyboard mode active.")
            
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
                
                # Apply auto-center if enabled
                if auto_center:
                    if abs(raw_lx) < 0.05: lx = 0.0
                    if abs(raw_ly) < 0.05: ly = 0.0
                    if abs(raw_rx) < 0.05: rx = 0.0
                    if abs(raw_ry) < 0.05: ry = 0.0
        
        if keyboard_active:
            # Check if controller got reconnected
            if pygame.joystick.get_count() > 0 and not controller_connected:
                try:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    controller_connected = True
                    keyboard_active = False
                    print("🎮 Controller reconnected! Switching back to controller input.")
                    print("[MODE] Controller mode active.")
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
        if debug_mode:
            timestamp = time.strftime("%H:%M:%S")
            # Initialize raw values for keyboard mode
            raw_lx = raw_ly = raw_rx = raw_ry = 0.0
            if controller_connected:
                raw_lx = joystick.get_axis(0)
                raw_ly = joystick.get_axis(1)
                raw_rx = joystick.get_axis(2)
                raw_ry = joystick.get_axis(3)
            print(f"[{timestamp}] Frame:{frame_count} 🕹️  Left Stick: Raw(X={raw_lx:.2f} Y={raw_ly:.2f}) → Processed(X={lx:.2f} Y={ly:.2f})    |    Right Stick: Raw(X={raw_rx:.2f} Y={raw_ry:.2f}) → Processed(X={rx:.2f} Y={ry:.2f})", end='\r')
        else:
            recording_status = "🔴" if recording else "⚪"
            playback_status = "▶️" if playing else ""
            mode_indicator = "🎮" if controller_connected else "⌨️"
            battery_indicator = f"🔋{controller_battery_level:.0f}%" if controller_connected else ""
            sensitivity_info = f"L:{CONTROL_SETTINGS['left_stick']['sensitivity']:.1f} R:{CONTROL_SETTINGS['right_stick']['sensitivity']:.1f}"
            deadzone_info = f"DZ:{CONTROL_SETTINGS['left_stick']['deadzone']:.1f}"
            exp_info = f"EXP:{CONTROL_SETTINGS['left_stick']['exponential']:.1f}"
            auto_center_status = "AC" if auto_center else ""
            debug_status = "DBG" if debug_mode else ""
            vibration_status = "VB" if vibration_enabled else ""
            theme_status = f"TH:{color_theme[:3].upper()}"
            print(f"{recording_status}{playback_status}{mode_indicator}{battery_indicator} {sensitivity_info} {deadzone_info} {exp_info} {auto_center_status} {debug_status} {vibration_status} {theme_status} 🕹️  Left Stick: X={lx:.2f}  Y={ly:.2f}    |    Right Stick: X={rx:.2f}  Y={ry:.2f}", end='\r')
        
        # Record commands if recording is active
        if recording:
            current_time = time.time()
            record_command('stick', {'lx': lx, 'ly': ly, 'rx': rx, 'ry': ry}, current_time)
        
        # Playback recorded commands
        if playing:
            playback_command = get_next_playback_command()
            if playback_command and playback_command['type'] == 'stick':
                lx = playback_command['values']['lx']
                ly = playback_command['values']['ly']
                rx = playback_command['values']['rx']
                ry = playback_command['values']['ry']
                time.sleep(0.05 / playback_speed)  # Adjust timing for playback speed
        
        # Calculate and display FPS if enabled
        if show_fps:
            frame_count += 1
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:  # Update every second
                fps = frame_count / (current_time - last_fps_time)
                print(f"\n📊 FPS: {fps:.1f} | Frame: {frame_count} | Time: {current_time:.1f}s")
                frame_count = 0
                last_fps_time = current_time
        
        # Update battery level
        update_battery_level()
        
        # Small delay to prevent high CPU usage
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
    pygame.quit()
    sys.exit()