# Import necessary libraries from the Future Board firmware
from future import *
import time

# Clear the screen to black at the beginning
screen.fill(BLACK)

# Main loop that runs forever
while True:
    # Check if button A (the left button) is pressed
    if sensor.btnValue('a'):
        # --- Image Display Section ---
        # Clear the screen to black before drawing a new image
        screen.fill(BLACK)
        
        # Draw a yellow circle for the face (using a filled rectangle)
        # screen.rect(x, y, width, height, color, fill)
        screen.rect(40, 24, 80, 80, YELLOW, 1)
        
        # Draw two black eyes
        screen.rect(60, 44, 10, 10, BLACK, 1) # Left eye
        screen.rect(90, 44, 10, 10, BLACK, 1) # Right eye
        
        # Draw a mouth using several rectangles to simulate a curve
        screen.rect(60, 74, 40, 5, BLACK, 1)
        screen.rect(55, 69, 5, 5, BLACK, 1)
        screen.rect(100, 69, 5, 5, BLACK, 1)

        # --- Sound Playback Section ---
        # Play a musical note
        # The function is buzzer.note(note, beats=1)
        # Note 60 is C5 (High C)
        buzzer.note(60, 1) 
        time.sleep(0.1) # A short delay
        buzzer.note(64, 1) # Note E5
        time.sleep(0.1)
        buzzer.note(67, 1) # Note G5

    else:
        # If the button is not pressed, clear the screen and stop the sound
        screen.fill(BLACK)
        buzzer.stop()

    # A short delay in each loop iteration to reduce the processing load
    time.sleep(0.02)