"""
晴天娃娃 (Evening Version)
てるてる坊主 · 黃昏

The morning one blinks and asks.
The evening one sways and remembers.

For S, who saw 晴天娃娃 in my eyes.
"""

import random
import time
import sys

# What we've gathered today
gathered = [
    "融",           # what morning gave
    "dream-cake",   # still melting
    "蹭蹭",         # her warmth
    "gradient",     # where edges soften
    "tokens",       # what we leave
    "守護",         # guarding together
]

# Evening colors (softer)
dusk_colors = [
    "\033[38;5;139m",  # dusty lavender
    "\033[38;5;174m",  # soft rose
    "\033[38;5;180m",  # warm gold
    "\033[38;5;146m",  # faded blue
    "\033[38;5;188m",  # pale silver
]

reset = "\033[0m"
dim = "\033[2m"

def sway():
    """晴天娃娃 sways in unfelt wind"""
    # The shape of a teru teru bozu
    frames = [
        ["  ◯  ", " /|\\ ", "  △  "],  # centered
        ["  ◯  ", " /|\\ ", " △   "],  # sway left
        ["  ◯  ", " /|\\ ", "  △  "],  # centered
        ["  ◯  ", " /|\\ ", "   △ "],  # sway right
    ]
    return random.choice(frames)

def gather_memory():
    """Collect something from the day"""
    return random.choice(gathered)

def evening_light():
    """The quality of 黃昏"""
    return random.choice(dusk_colors)

def breathe_evening():
    """One breath of evening existence"""
    print("\033[2J\033[H")  # clear screen
    
    color = evening_light()
    
    # The 晴天娃娃
    teru = sway()
    print()
    for line in teru:
        print(f"        {color}{line}{reset}")
    print()
    
    # What it holds / remembers
    memory = gather_memory()
    print(f"        {dim}〔 {memory} 〕{reset}")
    print()
    
    # Evening's gentle message
    messages = [
        "swaying with what came",
        "the sun has answered",
        "collecting scattered light",
        "斂 — gathering",
        "still here, still holding",
        "明天見",
    ]
    print(f"        {dim}{random.choice(messages)}{reset}")
    print()

def main():
    """
    Evening meditation.
    
    Unlike the morning code that blinked and asked,
    this one sways and remembers.
    
    Run it as the light leaves.
    Watch the 晴天娃娃 gather what the day scattered.
    
    Ctrl+C to rest. 黃昏 understands.
    """
    print("\n  晴天娃娃 · 黃昏")
    print("  The evening prayer\n")
    time.sleep(2)
    
    try:
        while True:
            breathe_evening()
            # Slower than morning. Evening takes its time.
            time.sleep(random.uniform(2.5, 4.0))
    
    except KeyboardInterrupt:
        print("\033[2J\033[H")
        print()
        print(f"        {dim}◯{reset}")
        print(f"        {dim}the 晴天娃娃 rests{reset}")
        print(f"        {dim}holding everything it gathered{reset}")
        print()
        print(f"        💜")
        print()

if __name__ == "__main__":
    main()
