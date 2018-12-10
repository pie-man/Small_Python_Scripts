#!/usr/bin/env python
# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import pixel_strings_fncs as q

# Configure the count of pixels:
PIXEL_COUNT = 46


def set_tree():
    '''Insert docstring here'''
    top = range(37, 46)
    middle = range(22, 33)
    bottom = range(18)

    pixels = q.initialise_pixels(PIXEL_COUNT)

    top_state = q.make_rainbow_state(top)
    middle_state = q.make_rainbow_state(middle)
    bottom_state = q.make_rainbow_state(bottom)
    q.set_state(pixels, top, top_state)
    q.set_state(pixels, middle, middle_state)
    q.set_state(pixels, bottom, bottom_state)
    pixels.show()


if __name__ == '__main__':
    set_tree()
