def get_color(screen, coords):
    return screen[coords[1], coords[0]]

def color_eq(c1, c2, tolerance = 1):
    diff = 0
    for i in range(0, 3):
        p1 = int(c1[i])
        p2 = int(c2[i])
        diff = diff + abs(p1 - p2)
    return diff < tolerance
