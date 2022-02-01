import numpy as np
from PIL import ImageGrab
import cv2
from directKeys import click, queryMousePosition, PressKey, ReleaseKey, SPACE
import time
import math

# only start the program after the mouse is in the top left corner
print("move the mouse to the upper left corner to start")
while True:
    mouse_pos = queryMousePosition()
    if mouse_pos.x <= 0 and mouse_pos.y <= 0:
        break
    
print("here we go")
