#!/usr/bin/env python
# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import pixel_strings_fncs as q

# Configure the count of pixels:
PIXEL_COUNT = 46

# Define the 'index' of the three rings of pixels to be ued globally
TOP    = range(37, 46)
MIDDLE = range(22, 33)
BOTTOM = range(18)

def set_tree():
    '''Set the three rings of the tree to display a static
       loop of rainbow colours'''

    top_state = q.make_rainbow_state(TOP)
    middle_state = q.make_rainbow_state(MIDDLE)
    bottom_state = q.make_rainbow_state(BOTTOM)
    q.set_state(pixels, TOP, top_state)
    q.set_state(pixels, MIDDLE, middle_state)
    q.set_state(pixels, BOTTOM, bottom_state)
    pixels.show()

def say_something():
    print("hello")

if __name__ == '__main__':
    pixels = q.initialise_pixels(PIXEL_COUNT)
    set_tree()
    function_list = [
            set_tree,
            say_something
            ]
    for function in function_list:
        function()
        time.sleep(10)
    pixels.clear()
    pixels.show()
