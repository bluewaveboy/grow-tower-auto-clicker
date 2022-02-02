import numpy as np
from PIL import ImageGrab
import cv2
from directKeys import click, move_mouse_to, query_mouse_position, press_key, release_key, query_key_state, KEY_Q
import time
import math

# only start the program after the mouse is in the top left corner
print("move the mouse to the upper left corner to start")
while True:
    mouse_pos = query_mouse_position()
    if mouse_pos.x <= 0 and mouse_pos.y <= 0:
        break
    
print("here we go")
while not query_key_state(KEY_Q):
    time.sleep(1)
    move_mouse_to(100, 100)
    click(100, 100)
    time.sleep(1)
    move_mouse_to(200, 200)
