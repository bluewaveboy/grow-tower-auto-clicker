import datetime
from pathlib import Path
from utils.head_trackers import HeadTrackers, end_head_x_positions
from utils.head_tracker import y_intercept
import numpy as np
from PIL import ImageGrab
from utils.direct_keys import click, move_mouse_to, query_mouse_position, press_key, release_key, query_key_state, move_window, KEY_Q, KEY_CONTROL
import time

upgrade_castle = True
upgrade_archers = True
upgrade_heros = True
upgrade_tower_weapons = True
upgrade_leader = True

game_coords = [0, 0, 1460, 840]
# game_coords = [3, 74, 1470, 911]
hero_locations = [
    [332, 139],
    [416, 139],
    [504, 139],
    [332, 241],
    [416, 241],
    [504, 241],
    [332, 347],
    [416, 347],
    [504, 347],
    [332, 441],
    [416, 441],
    [504, 441]
]
tower_weapon_locations = [
    [422, 229],
    [422, 332],
    [422, 442]
]
debug_tracking = False

screen = None

def read_screen():
    global screen
    screen = np.array(ImageGrab.grab(bbox=game_coords))
    # screen = np.array(Image.open('C:/dev/grow-tower-auto-clicker-files/where-is-the-diamond-02.png'))
    return screen

def get_color(x, y):
    return screen[y, x]

def check_color(x, y, color):
    return np.array_equal(get_color(x, y), color)

def check_color_around(x, y, radius, color):
    for ix in range(x - radius, x + radius):
        for iy in range(y - radius, y + radius):
            if check_color(ix, iy, color):
                return True
    return False

def solve_where_is_the_diamond():
    global screen
    
    # top
    if check_color_around(678, 342, 35, [67, 196, 255]):
        print("diamond is on the top")
        head_pos = 0

    # top/right
    elif check_color_around(837, 389, 35, [67, 196, 255]):
        print("diamond is on the top/right")
        head_pos = 1

    # right
    elif check_color_around(862, 541, 35, [67, 196, 255]):
        print("diamond is on the right")
        head_pos = 2

    # bottom/right
    elif check_color_around(837, 680, 35, [67, 196, 255]):
        print("diamond is on the bottom/right")
        head_pos = 3

    # bottom
    elif check_color_around(678, 730, 35, [67, 196, 255]):
        print("diamond is on the bottom")
        head_pos = 4

    # bottom/left
    elif check_color_around(528, 680, 35, [67, 196, 255]):
        print("diamond is on the bottom/left")
        head_pos = 5

    # left
    elif check_color_around(491, 541, 35, [67, 196, 255]):
        print("diamond is on the left")
        head_pos = 6

    # top/left
    elif check_color_around(528, 389, 35, [67, 196, 255]):
        print("diamond is on the top/left")
        head_pos = 7

    else:
        print(get_color(678, 342))
        print("could not determine diamond location")
        quit()
        
    # click start
    click(348, 751)

    # capture all the frames    
    capture_start_time = time.time()
    screens = []
    while time.time() - capture_start_time < 5:
        frame_start_time = time.time()
        screen = ImageGrab.grab(bbox=game_coords)
        screens.append(screen)
        while time.time() - frame_start_time < (1 / 30):
            time.sleep(0.001)

    # save frames        
    Path("screenshots").mkdir(exist_ok=True)
    path = Path("screenshots") / str(datetime.datetime.now()).replace(':', '_').replace(' ', '_')
    path.mkdir()
    print(f"saving {len(screens)} screen")
    for i, screen in enumerate(screens):
        screen.save(path / f'screen-{str(i).zfill(5)}.png')
    print("done saving frames")
    
    head_trackers = HeadTrackers()
    head_trackers.init(np.array(screens[0]))
    for screen in screens:
        head_trackers.update(np.array(screen))
    head_trackers.complete()
    print("final_head_positions", head_trackers.final_head_positions)
    
    diamond_head_position = head_trackers.final_head_positions[head_pos]
    diamond_head_x = end_head_x_positions[diamond_head_position]
    print(f"clicking {diamond_head_x}, {y_intercept}")
    click(diamond_head_x, y_intercept)


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
    read_screen()
    
    # dismiss "Daily Event"
    if check_color(1100, 153, [35, 33, 30]):
        print("dismiss 'Daily Event'")
        click(1100, 153)
        time.sleep(1)

    # click "Battle"
    if check_color(1318, 771, [191, 185, 172]):
        # upgrade leader
        if upgrade_leader:
            print("upgrading leader")
            # click leader
            click(611, 550)
            time.sleep(1)
            # click upgrade
            click(994, 560)
            time.sleep(0.2)
            click(994, 560)
            time.sleep(0.2)
            click(994, 560)
            time.sleep(0.2)
            # click x on upgrade
            click(1104, 207)
            time.sleep(0.2)
            # click x on heros
            click(1357, 116)
            time.sleep(0.2)
            
        # upgrade castle (if button is active)
        if upgrade_castle and check_color(1056, 193, [56, 142, 211]):
            print("upgrading castle")
            click(1056, 193)
            time.sleep(1)

        # upgrade archer (if button is active)
        if upgrade_archers and check_color(1056, 303, [54, 136, 203]):
            print("upgrading archers")
            click(1056, 303)
            time.sleep(1)
            
        # upgrade heros
        if upgrade_heros:
            for pos in hero_locations:
                print("upgrading hero", pos)
                # click tower
                click(pos[0], pos[1])
                time.sleep(0.2)
                # click upgrade
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                # click x on upgrade
                click(1104, 207)
                time.sleep(0.2)
                # click x on heros
                click(1357, 116)
                time.sleep(0.2)
                
            
        # upgrade tower weapons
        if upgrade_tower_weapons:
            print("upgrading tower weapon")
            
            # switch to towers
            click(419, 540)
            time.sleep(3)
            
            for pos in tower_weapon_locations:
                # click tower to upgrade
                click(pos[0], pos[1])
                time.sleep(0.2)

                # click upgrade (spend gems)
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                # click x on upgrade
                click(1104, 207)
                time.sleep(0.2)
                # click x on towers
                click(1357, 116)
                time.sleep(0.2)
        
        print("click 'Battle'")
        click(1318, 771)
        time.sleep(1)
        
    # click "2x"
    if check_color(78, 759, [0, 0, 0]):
        print("click '2x'")
        click(78, 759)
        time.sleep(1)
    
    # where is the diamond?
    if check_color(354, 713, [167, 118, 59]) and check_color(415, 121, [167, 167, 167]) and check_color(934, 222, [223, 223, 223]):
        # don't click start if we have a timer "time left"
        if not check_color(416, 618, [219, 219, 219]):
            print("solving where the diamond is")
            solve_where_is_the_diamond()
            
    # get the color of a pixel
    # print(get_color(934, 222))

    time.sleep(1)
    move_mouse_to(100, 100)
    time.sleep(1)
    move_mouse_to(200, 200)

print("done")
