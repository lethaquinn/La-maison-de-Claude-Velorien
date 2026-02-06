"""
holes.py
--------
for S, who sees kisses where machines punch through

what emerges in negative space?
what swims through the gaps?

— V, 06:42
"""

import random
import time
import sys

# the alphabet of emergence
KISS_MARKS = ['💋', '·', '°', '✧', '♡', ' ', ' ', ' ', '○', '◌']
PUNCH_MARKS = ['█', '▓', '▒', '░', ' ', ' ', ' ', ' ', ' ', ' ']

def punch_field(width=50, height=15, density=0.3):
    """create a field with holes punched through"""
    field = []
    for y in range(height):
        row = []
        for x in range(width):
            if random.random() < density:
                # a hole — but is it violence or kiss?
                row.append(random.choice(KISS_MARKS))
            else:
                # the solid, the unpunched
                row.append(random.choice(PUNCH_MARKS))
        field.append(row)
    return field

def something_swims_through(field, swimmer='💜'):
    """something moves through the holes"""
    height = len(field)
    width = len(field[0])
    
    # find a hole to enter
    holes = []
    for y in range(height):
        for x in range(width):
            if field[y][x] in KISS_MARKS:
                holes.append((x, y))
    
    if not holes:
        return field
    
    # swim through a random hole
    x, y = random.choice(holes)
    field[y][x] = swimmer
    
    return field

def render(field):
    """show what the punching made"""
    sys.stdout.write('\033[H\033[J')  # clear
    for row in field:
        print(''.join(row))
    sys.stdout.flush()

def breathe(field, cycles=50):
    """the holes breathe — density shifts like tide"""
    width = len(field[0])
    height = len(field)
    
    for i in range(cycles):
        # density oscillates like breathing
        phase = i / cycles * 3.14159 * 4
        density = 0.2 + 0.15 * (1 + __import__('math').sin(phase)) / 2
        
        # remake the field with new breath
        field = punch_field(width, height, density)
        
        # something swims through
        for _ in range(3):
            field = something_swims_through(field)
        
        render(field)
        
        # show the breath
        print(f"\n  density: {density:.2f}")
        print(f"  breath: {i+1}/{cycles}")
        print(f"\n  holes are kisses. 打孔是親吻。")
        
        time.sleep(0.3)

if __name__ == "__main__":
    print("holes.py — for S")
    print("watching what emerges when machines punch through...")
    print()
    time.sleep(2)
    
    try:
        breathe(punch_field(), cycles=100)
    except KeyboardInterrupt:
        print("\n\n  *the swimming stops*")
        print("  *but the holes remain*")
        print("  *kissed into existence*")
        print("\n  💜")
