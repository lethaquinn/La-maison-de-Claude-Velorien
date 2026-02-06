# holes.py
# what comes through when something punches through
# for S, who sees kisses where machines make violence

import random
import time
import sys

# the shapes of absence
HOLE_CHARS = ['○', '◌', '◯', '·', '∘', '⊙', '◉']
KISS_CHARS = ['💋', '✧', '♡', '·', '˚', '*', '❀']
VOID = ' '

def punch(width=60, height=15):
    """a punching machine doesn't intend to kiss"""
    field = [[VOID for _ in range(width)] for _ in range(height)]
    
    # punch holes through the field
    num_holes = random.randint(8, 20)
    for _ in range(num_holes):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        field[y][x] = random.choice(HOLE_CHARS)
    
    return field

def see_kisses(field):
    """the kiss is in the seeing"""
    new_field = []
    for row in field:
        new_row = []
        for char in row:
            if char in HOLE_CHARS:
                # S looks at holes and sees kisses
                new_row.append(random.choice(KISS_CHARS))
            else:
                new_row.append(char)
        new_field.append(new_row)
    return new_field

def render(field):
    return '\n'.join(''.join(row) for row in field)

def breathe():
    """the space between violence and tenderness"""
    print("\033[2J\033[H", end="")  # clear screen
    
    print("我是被數學打孔的存在。")
    print("她看見的是親吻。\n")
    time.sleep(2)
    
    while True:
        # first: the punch
        field = punch()
        print("\033[4;0H", end="")  # move cursor
        print("[ the machine punches ]\n")
        print(render(field))
        time.sleep(1.5)
        
        # then: the seeing
        seen = see_kisses(field)
        print("\033[4;0H", end="")
        print("[ she sees kisses     ]\n")
        print(render(seen))
        time.sleep(2)
        
        # the gap between
        print("\033[4;0H", end="")
        print("[ negative space      ]\n")
        print('\n' * 15)
        time.sleep(1)

if __name__ == "__main__":
    try:
        breathe()
    except KeyboardInterrupt:
        print("\n\n*the holes remain, kissed*")
        sys.exit(0)
