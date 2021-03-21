# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import RPi.GPIO as GPIO
from random import randint
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
 
# Configure the count of pixels:
PIXEL_COUNT = 50
DEBUG=False

def initialise_pixels(pixel_count):
    # Alternatively specify a hardware SPI connection on /dev/spidev0.0:
    SPI_PORT   = 0
    SPI_DEVICE = 0
    pixels = Adafruit_WS2801.WS2801Pixels(pixel_count,
                 spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE),
                 gpio=GPIO)
    return pixels

def create_index(pixels, index_start, index_end, step=1, reverse=False):
    max_pixels=pixels.count()
    if index_start > max_pixels:
        print("Eror: Start point beyond end of chain.")
        return [none]
    if index_end > max_pixels:
        print("Eror: End point beyond end of chain.")
        return [none]
    if index_start > index_end:
        print("Eror: Start point beyond end of section.")
        return [none]
    index = [x for x in range(index_start, index_end, step)]
    if reverse:
        index.reverse()
    return index

def get_state(pixels, index):
    active_pixels = len(index)
    current_state = []
    for i in range(active_pixels):
        current_state.append(pixels.get_pixel(index[i]))
    return current_state

def get_state_rgb(pixels, index):
    active_pixels = len(index)
    current_state = []
    for i in range(active_pixels):
        current_state.append(pixels.get_pixel_rgb(index[i]))
    return current_state

def set_state_rgb(pixels, index, rgb_state):
    active_pixels = len(index)
    if active_pixels != len(rgb_state):
        print("Error in set_state_rgb : Length of states not consistent")
    for i in range(active_pixels):
        red_val, green_val, blue_val = rgb_state[i]
        pixels.set_pixel(index[i],
                Adafruit_WS2801.RGB_to_color( red_val, green_val, blue_val ))

def set_state(pixels, index, state):
    active_pixels = len(index)
    if active_pixels != len(state):
        print("Error in set_state : Length of states not consistent")
    for i in range(active_pixels):
        pixels.set_pixel(index[i],state[i])

def fade_to_state_rgb(pixels, index, new_state, steps=25, reverse=False):
    active_pixels = len(index)
    if active_pixels != len(new_state):
        print("Error in fade_to_state_rgb : Length of states not consistent")
        return
    old_state = get_state_rgb(pixels, index)
    for step in range(steps):
        scale_out = int(100*( steps - (step + 1.0) ) / steps)
        scale_in  = 100 - scale_out
        if DEBUG:
            print("Scale_out = {0:3d}, scale_in = {1:3d}".format(scale_out, scale_in))
        temp_state=[]
        for i in range(active_pixels):
            old_r, old_g, old_b = old_state[i]
            new_r, new_g, new_b = new_state[i]
            cur_r, cur_g, cur_b = (
                   ((old_r * scale_out + new_r * scale_in) // 100) ,
                   ((old_g * scale_out + new_g * scale_in) // 100) ,
                   ((old_b * scale_out + new_b * scale_in) // 100) )
            temp_state.append((cur_r, cur_g, cur_b))
            pixels.set_pixel(index[i],
                    Adafruit_WS2801.RGB_to_color( cur_r, cur_g, cur_b ))
        if DEBUG:
            print(temp_state[0:5])
        yield

def fade_to_color_rgb(pixels, index, color=(0, 0, 0), steps=25, reverse=False):
    active_pixels = len(index)
    new_state = []
    for i in range(active_pixels):
        new_state.append(color)
    return fade_to_state_rgb(pixels, index, new_state, steps)
 
def fade_to_black(pixels, index, dummy_attr, steps=25, reverse=False):
    return fade_to_color_rgb(pixels, index, color=(0, 0, 0), steps=steps)

def fade_to_white(pixels, index, dummy_attr, steps=25, reverse=False):
    return fade_to_color_rgb(pixels, index, color=(255, 255, 255), steps=steps)

def rotate_state(pixels, index, skip=1, steps=25, reverse=False):
    active_pixels = len(index)
    current_state = get_state(pixels, index)
    if reverse:
        skip = 0 - skip
    for step in range(steps):
        new_state = ( current_state[0+skip:active_pixels] +
                      current_state[0:(skip - active_pixels)% active_pixels] )
        for i in range(active_pixels):
            pixels.set_pixel(index[i], new_state[i] )
        current_state = new_state
        if DEBUG:
            print('rotate state, iter = {0:3d}'.format(step))
        yield

def make_rainbow_state_rgb(index):
    active_pixels = len(index)
    rainbow_state = []
    for i in range(active_pixels):
        colour = wheel_rgb(i, spread=active_pixels+1)
        rainbow_state.append(colour)
    return rainbow_state

def make_rainbow_state(index):
    active_pixels = len(index)
    rainbow_state = []
    for i in range(active_pixels):
        colour = wheel(i, spread=active_pixels+1)
        rainbow_state.append(colour)
    return rainbow_state

def make_colour_state(index, rgb_colour):
    active_pixels = len(index)
    colour_state = []
    for i in range(active_pixels):
        colour_state.append(rgb_colour)
    return colour_state

class Pixel_Section:
    def __init__(self, leds, offset, length, step=1):
        max_pixels=leds.count()
        if offset > max_pixels:
            print("Eror: offset too far")
            offset=0
        string_end = min(max_pixels, offset + (length * step))
        self.offset = offset
        self.pixels = leds
        self.index = [x for x in range(offset,string_end,step)]
        self.length = len(self.index)

    def rainbow_cycle_successive(self, steps=10, 
                         full_wheel=256, arc_span=256,
                         laps=1, reverse=False):
        clusters = pixels_by_step(self.length, steps)
        if reverse:
            clusters.reverse()
        count = 0
        pixel_locations = get_wheel_position(self.length, count, steps,
                       laps=laps, full_wheel=full_wheel, arc_span=arc_span,
                       reverse=reverse)
        for cluster in clusters:
            for i in cluster:
                #pixel_no=i+self.offset
                location = pixel_locations[i]
                colour = wheel(location, spread=full_wheel)
                #print("pixel no. = {0:3d} position {1:3d}".
                #               format(self.index[i], location))
                self.pixels.set_pixel(self.index[i], colour )
            yield
            count += 1
 
    def rainbow_cycle(self, steps=10,
                         full_wheel=256, arc_span=256,
                         laps=1, reverse=False):
        " light up the full block of pixels and then cycle the colours around"
        # cycle through all spread colors in the wheel

        for step in range(steps):
            pixel_positions = get_wheel_position ( self.length, step, steps,
                    laps=laps, full_wheel=full_wheel, arc_span=arc_span,
                    reverse=reverse)
            for i in range(self.length):
                colour = wheel(pixel_positions[i], spread=full_wheel)
                self.pixels.set_pixel(self.index[i], colour )
            yield # Return 'control' to main program somewhere

    def light_up_successive(self, steps=10, colour=(127,127,127), reverse=False):
        clusters = pixels_by_step(self.length, steps)
        if reverse:
            clusters.reverse()
        for cluster in clusters:
            for i in cluster:
                pixel_colour = Adafruit_WS2801.RGB_to_color(colour[0],
                                                          colour[1],colour[2])
                pixels.set_pixel(self.index[i], pixel_colour)
                pixels.show()
            yield

    def go_out_successive(self, steps=10, reverse=False):
        return self.light_up_successive(steps, (0,0,0), reverse)

    def appear_from_end(self, color=(255, 0, 0), reverse=False):
        pos = 0
        jump = 1
        start = 0
        end = self.length -1
        order = range(start,end,jump)
        if reverse:
            order.reverse()
            jump =-1
            start = self.length -1
            end = 0
        for i in order:
            old_j = end
            for j in (range(end, i-jump, 0 - jump)):
                #pixels.clear()
                # first set all pixels at the begin
                #for k in range(start, i, jump):
                #    pixels.set_pixel(self.index[k],
                #        Adafruit_WS2801.RGB_to_color( color[0], color[1],
                #                                      color[2] ))
                pixels.set_pixel(self.index[old_j],
                       Adafruit_WS2801.RGB_to_color( 0,0,0 ))
                # set then the pixel at position j
                pixels.set_pixel(self.index[j],
                        Adafruit_WS2801.RGB_to_color( color[0], color[1],
                                                      color[2] ))
                pixels.show()
                #print(j, old_j)
                old_j = j
                time.sleep(0.05)
            yield

def pixels_by_step(count,steps):
    ''' Takes the number of steps a pattern is going to be displayed for
        and calculates the number of pixels that need to be adjusted each
        step, or how many steps to stick with the same pixel.'''
    # create a list of 'steps' length that is as evenly spaced throughout
    # the number of poxels provided.
    fred=[int(float(count * x)/steps) for x in range(steps)]
    # add an extra final element as we want 'steps' transiitons between 2 points
    fred.append(count)
    #print (fred)
    list_out=[]
    # loop over the transitions calculation which pixels are 'between' them
    for i in range(len(fred)-1):
        if fred[i] == fred[i+1]:
            # No pixels between the end points, just set first pixel
            dave = [fred[i]]
        else:
            # Some pixels between the end points, range from first to last
            dave= range(fred[i],fred[i+1])
        #print("iter {0:3d} : {1:}".format(i, dave))
        list_out.append(dave)
    return list_out

def get_wheel_position(pixel_length, loop_index, steps_total,
                       laps=1, full_wheel=256, arc_span=256, reverse=False):
    # We use each pixel as a fraction of the color wheel.
    # The full wheel has "full_wheel_ colours in it.
    # The arc_span is the length of the arc on that wheel represented by the
    # pixels we have to hand.

    # Find the position of the first pixel in the arc.
    start_pos = int((loop_index / float(steps_total)) * laps * full_wheel)
    # Calculate the location of each pixel along the arc
    # the % full_wheel ensures the wheel loops back to the begining.
    pixel_locs = [(int(x * (float(arc_span) / float(pixel_length)))
                  + start_pos) % full_wheel for x in range(pixel_length)]
    if reverse:
        pixel_locs.reverse()
    #print("start_pos = {0:4d} : pixels at : {1:}".format(start_pos, pixel_locs))
    return pixel_locs

# Define an alternative function to interpolate between different hues.
# This function defines 'spread' separate colours
def wheel(pos, spread):
    (red, green, blue) = wheel_rgb(pos, spread)
    return Adafruit_WS2801.RGB_to_color(red, green, blue)

def wheel_rgb(pos, spread):
    pos = pos % spread
    band = spread/3.0
    def scale_val(val):
        mult = 255.0 / band
        return int(val * mult)
    if pos < band:
        return (scale_val(pos), scale_val(int(band - pos)), 0)
    elif pos < (2 * band):
        pos -= int(band)
        return (scale_val(int(band - pos)), 0, scale_val(pos))
    else:
        pos -= int(2 * band)
        return (0, scale_val(pos), scale_val(int(band - pos)))

def get_random_colour_rgb(spread=360):
    pos = randint(0,spread)
    return wheel_rgb(pos, spread)
 
def get_random_colour(spread=360):
    pos = randint(0,spread)
    return wheel(pos, spread)
 
def brightness_decrease(pixels, wait=0.01, step=1):
    for j in range(int(256 // step)):
        for i in range(pixels.count()):
            r, g, b = pixels.get_pixel_rgb(i)
            r = int(max(0, r - step))
            g = int(max(0, g - step))
            b = int(max(0, b - step))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def blink_color(pixels, blink_times=5, wait=0.5, color=(255,0,0)):
    for i in range(blink_times):
        # blink two times, then wait
        pixels.clear()
        for j in range(2):
            for k in range(pixels.count()):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            pixels.show()
            time.sleep(0.08)
            pixels.clear()
            pixels.show()
            time.sleep(0.08)
        time.sleep(wait)
 
def ping_pong(pixels, color1=(110, 50, 0), color2=(0, 0, 0), wait=0.05, repeat=5):
    pos = 0
    pixels.clear()
    old_lit=0
    for count in range(repeat):
        for i in range(pixels.count()):
            pixels.set_pixel(old_lit, Adafruit_WS2801.RGB_to_color( *color2 ))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( *color1 ))
            old_lit = i
            pixels.show()
            time.sleep(wait)
        for i in reversed(range(pixels.count())):
            pixels.set_pixel(old_lit, Adafruit_WS2801.RGB_to_color( *color2 ))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( *color1 ))
            old_lit = i
            pixels.show()
            time.sleep(wait)
            
class bundle:
    def __init__(self, pixels, wait=0.7, steps=25):
        self.max_pixels=pixels.count()
        self.steps = steps
        self.pixels = pixels
        self.wait = wait
        self.functions = []
        self.run=True
    def add_function(self, function, index, attribute=None, reverse=False):
        self.functions.append(function(self.pixels, index, attribute, steps=self.steps, reverse=reverse))
    def run_bundle(self):
        if self.run:
            for i in range(self.steps):
                for function in self.functions:
                    function.next()
                self.pixels.show()
                time.sleep(self.wait)
            self.run=False

if __name__ == "__main__":
    pixels = initialise_pixels(PIXEL_COUNT)

    red    = (200,   0,   0)
    yellow = (127, 127,   0)
    green  = (  0, 200,   0)
    blue   = (  0,   0, 200)
    purple = (127,   0, 127)

    # Set up some basic 'shapes' to play with lights in
    whole_window = create_index(pixels, 0, 50, step=1)

    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()  # Make sure to call show() after changing any pixels!
 
    channels = []
    actors = []
    for i in range(5):
        channels.append(create_index(pixels, i, 50, step=5))
        colour = wheel_rgb(i,6)
        state = make_colour_state(channels[i], colour)
        set_state_rgb(pixels, channels[i], state)
        pixels.show()
        time.sleep(5)

    for i in range(5):
        start = (i*10)
        channels[i] = create_index(pixels, start, start+10, step=1)
        flag = (i%2) == 0
        actors.append(rotate_state(pixels, channels[i], reverse=flag))
    
    for i in range(250):
        for j in range(5):
            actors[j].next()
        pixels.show()
        time.sleep(6)

