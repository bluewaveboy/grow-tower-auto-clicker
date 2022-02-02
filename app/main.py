import numpy as np
from PIL import ImageGrab
import cv2
from directKeys import click, move_mouse_to, query_mouse_position, press_key, release_key, query_key_state, move_window, KEY_Q, KEY_CONTROL
import time
import math

game_coords = [0, 0, 1460, 840]
screen = None

def get_color(x, y):
    return screen[y, x]

def check_color(x, y, color):
    return np.array_equal(get_color(x, y), color)

# only start the program after the mouse is in the top left corner
print("move the mouse to the upper left corner to start")
while True:
    mouse_pos = query_mouse_position()
    if mouse_pos.x <= 0 and mouse_pos.y <= 0:
        break
    
print("here we go")
move_window(u'Qt5154QWindowOwnDCIcon', None, 0, 0, 1453, 832)
while not query_key_state(KEY_CONTROL):
    print("checking (hold CTRL to exit)")
    screen = np.array(ImageGrab.grab(bbox=game_coords))
    
    # dismiss "Daily Event"
    if check_color(1100, 153, [35, 33, 30]):
        print("dismiss 'Daily Event'")
        click(1100, 153)
        time.sleep(1)

    # click "Battle"
    if check_color(1318, 771, [191, 185, 172]):
        print("click 'Battle'")
        click(1318, 771)
        time.sleep(1)
    
    # get the color of a pixel
    # print(get_color(1318, 771))

    time.sleep(1)
    move_mouse_to(100, 100)
    time.sleep(1)
    move_mouse_to(200, 200)

print("done")
