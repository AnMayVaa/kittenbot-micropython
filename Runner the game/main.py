# --- 1. Import necessary libraries ---
from future import *
import time
import random

# --- 2. Color Definitions (RGB Tuples) ---
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_RED = (255, 0, 0)
C_GREEN = (34, 139, 34)
C_BLUE = (65, 105, 225)
C_YELLOW = (255, 255, 0)
C_GRAY = (128, 128, 128)

# --- 3. Game Constants ---
SCREEN_WIDTH = 200
SCREEN_HEIGHT = 128
GROUND_Y = SCREEN_HEIGHT - 20
PLAYER_WIDTH_RUN = 12
PLAYER_HEIGHT_RUN = 20
PLAYER_WIDTH_SLIDE = 20
PLAYER_HEIGHT_SLIDE = 10
JUMP_STRENGTH = -5.8
GRAVITY = 0.5
INITIAL_GAME_SPEED = 2.5

# --- 4. Game State Variables ---
player_x = 15 # Player's X position is fixed on the left
player_y = GROUND_Y - PLAYER_HEIGHT_RUN
player_vy = 0 # Player's vertical velocity
player_state = "run" # Can be "run", "jump", or "slide"
obstacles = []
obstacle_spawn_timer = 0
game_active = False
score = 0.0
start_time = 0
game_speed = INITIAL_GAME_SPEED
animation_frame = 0


# --- 5. Drawing Functions ---
def draw_player():
    """Draws the player character based on its current state."""
    global screen, animation_frame
    if player_state == "slide":
        y_pos = GROUND_Y - PLAYER_HEIGHT_SLIDE
        screen.rect(int(player_x), int(y_pos), PLAYER_WIDTH_SLIDE, PLAYER_HEIGHT_SLIDE, C_BLUE, 1)
    else:
        y_pos = int(player_y)
        screen.rect(int(player_x), y_pos, PLAYER_WIDTH_RUN, PLAYER_HEIGHT_RUN, C_BLUE, 1)
        # Simple two-frame running animation for the legs
        if player_state == "run":
            animation_frame += 1
            leg_height = 4
            if (animation_frame // 4) % 2 == 0:
                screen.rect(int(player_x), y_pos + PLAYER_HEIGHT_RUN, 4, leg_height, C_BLUE, 1)
            else:
                screen.rect(int(player_x + PLAYER_WIDTH_RUN - 4), y_pos + PLAYER_HEIGHT_RUN, 4, leg_height, C_BLUE, 1)

def draw_obstacles():
    """Draws all obstacles currently on the screen."""
    global screen
    for obs in obstacles:
        color = C_GREEN if obs['type'] == 'ground' else C_GRAY
        screen.rect(int(obs['x']), int(obs['y']), obs['w'], obs['h'], color, 1)

def draw_game_ui():
    """Draws the static UI elements like the ground and score."""
    global screen
    screen.line(0, GROUND_Y, SCREEN_WIDTH, GROUND_Y, C_WHITE)
    score_text = "{:.2f}".format(score)
    # The signature is: text(string, x, y, size, color)
    screen.text(score_text, SCREEN_WIDTH - 4 - len(score_text) * 18, 5, 1, C_WHITE)

# --- 6. Game Logic Update Functions ---
def update_player_state():
    """Handles player input and physics."""
    global player_y, player_vy, player_state, sensor, buzzer
    is_jumping = sensor.btnValue('a')
    is_sliding = sensor.btnValue('b')

    # Handle state transitions based on input
    if player_state != "jump" and is_jumping:
        player_state = "jump"
        player_vy = JUMP_STRENGTH
        buzzer.note(76, 0.05)
    elif player_state != "jump" and is_sliding:
        if player_state != "slide":
            buzzer.note(50, 0.1)
        player_state = "slide"
    elif player_state != "jump":
        player_state = "run"

    # Apply gravity if jumping
    if player_state == "jump":
        player_y += player_vy
        player_vy += GRAVITY
        # Check for landing on the ground
        if player_y >= GROUND_Y - PLAYER_HEIGHT_RUN:
            player_y = GROUND_Y - PLAYER_HEIGHT_RUN
            player_vy = 0
            player_state = "run"

def update_obstacles():
    """Moves, removes, and spawns new obstacles."""
    global obstacle_spawn_timer, obstacles
    # Move all obstacles to the left
    for obs in obstacles:
        obs['x'] -= game_speed
    
    # Remove obstacles that have moved off-screen
    obstacles = [obs for obs in obstacles if obs['x'] + obs['w'] > 0]

    # Decide whether to spawn a new obstacle
    obstacle_spawn_timer -= 1
    if obstacle_spawn_timer <= 0:
        if len(obstacles) < 3 and random.randint(1, 100) > 30:
            if random.randint(0, 1) == 0:
                # Ground obstacle (cactus)
                new_obs = {'x': SCREEN_WIDTH, 'w': 10, 'h': 20, 'type': 'ground', 'y': GROUND_Y - 20}
            else:
                # Air obstacle (bird), lowered to force sliding
                new_obs = {'x': SCREEN_WIDTH, 'w': 18, 'h': 8, 'type': 'air', 'y': GROUND_Y - PLAYER_HEIGHT_RUN - 5}
            obstacles.append(new_obs)
        # Reset spawn timer (spawns faster as game speed increases)
        # Adjusted range for more consistent obstacles
        obstacle_spawn_timer = random.randint(30, 40) / (game_speed / INITIAL_GAME_SPEED)

def check_collision():
    """Checks for collision between the player and any obstacle."""
    # Define player's hitbox based on current state
    if player_state == "slide":
        player_rect = {'x': player_x, 'y': GROUND_Y - PLAYER_HEIGHT_SLIDE, 'w': PLAYER_WIDTH_SLIDE, 'h': PLAYER_HEIGHT_SLIDE}
    else:
        player_rect = {'x': player_x, 'y': player_y, 'w': PLAYER_WIDTH_RUN, 'h': PLAYER_HEIGHT_RUN}
    
    # Standard AABB collision detection
    for obs in obstacles:
        if (player_rect['x'] < obs['x'] + obs['w'] and
            player_rect['x'] + player_rect['w'] > obs['x'] and
            player_rect['y'] < obs['y'] + obs['h'] and
            player_rect['y'] + player_rect['h'] > obs['y']):
            return True # Collision!
    return False

def reset_game():
    """Resets all game variables to their initial state."""
    global player_y, player_vy, player_state, obstacles, score, game_speed, game_active, start_time
    player_y = GROUND_Y - PLAYER_HEIGHT_RUN
    player_vy = 0
    player_state = "run"
    obstacles.clear()
    
    # Pre-spawn the first obstacle to make the start less empty
    first_obstacle = {'x': SCREEN_WIDTH, 'w': 10, 'h': 20, 'type': 'ground', 'y': GROUND_Y - 20}
    obstacles.append(first_obstacle)

    score = 0.0
    game_speed = INITIAL_GAME_SPEED
    game_active = True
    start_time = time.ticks_ms()

# --- 7. Game State Screens ---
def show_start_screen():
    """Displays the initial start screen and waits for input."""
    global screen, sensor
    screen.fill(C_BLACK)
    screen.text("Future Runner", 20, 40, 1, C_WHITE)
    screen.text("Press A to Start", 8, 70, 1, C_YELLOW)
    # Wait for button A to be pressed
    while not sensor.btnValue('a'):
        time.sleep(0.05)
    # Wait for button A to be released to prevent an immediate jump
    while sensor.btnValue('a'):
        time.sleep(0.05)

def show_game_over_screen():
    """Displays the static game over screen and waits for restart."""
    global screen, sensor
    screen.fill(C_BLACK)
    screen.text("GAME OVER", 32, 40, 1, C_RED)
    final_score_text = "Score: {:.2f}".format(score)
    screen.text(final_score_text, 20, 60, 1, C_WHITE)
    screen.text("Press A to Retry", 4, 90, 1, C_YELLOW)
    
    # Wait in a loop without redrawing to prevent flickering
    time.sleep(0.5) # Short delay to prevent accidental restart
    while not sensor.btnValue('a'):
        time.sleep(0.05)
    while sensor.btnValue('a'):
        time.sleep(0.05)
    reset_game()

# --- 8. Main Game Loop ---
show_start_screen()
reset_game()

while True:
    if game_active:
        # --- LOGIC UPDATES ---
        score = (time.ticks_ms() - start_time) / 1000.0
        update_player_state()
        update_obstacles()

        # --- COLLISION CHECK ---
        if check_collision():
            game_active = False
            buzzer.note(30, 0.2)
            time.sleep(0.05)
            buzzer.note(25, 0.4)
            continue # Skip to the next loop iteration to enter the 'else' block

        # --- SPEED UP ---
        # Every 10 seconds, increase the game speed
        if int(score) > 0 and int(score) % 10 == 0 and time.ticks_ms() % 1000 < 20:
             game_speed += 0.2
        
        # --- DRAWING ---
        screen.fill(C_BLACK)
        draw_game_ui()
        draw_player()
        draw_obstacles()
    else:
        # --- GAME OVER STATE ---
        show_game_over_screen()
    
    # By removing time.sleep(), the loop runs as fast as possible,
    # resulting in a higher and smoother frame rate.