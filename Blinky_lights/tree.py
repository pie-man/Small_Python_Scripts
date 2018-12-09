# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import pixel_strings_fncs as q
 
# Configure the count of pixels:
PIXEL_COUNT = 46

top = [x+37 for x in range(9)]
middle = [x+22 for x in range(11)]
bottom = range(18)

pixels = q.initialise_pixels(PIXEL_COUNT)

top_state    = q.make_rainbow_state(top)
middle_state = q.make_rainbow_state(middle)
bottom_state = q.make_rainbow_state(bottom)
q.set_state(pixels, top, top_state)
q.set_state(pixels, middle, middle_state)
q.set_state(pixels, bottom, bottom_state)
pixels.show()


