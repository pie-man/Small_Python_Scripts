# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import RPi.GPIO as GPIO
from random import randint
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
 
# Configure the count of pixels:
PIXEL_COUNT = 50
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT,
                                 spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
 
class Pixel_Section:
    def __init__(self, leds, offset, length, step=1):
        max_pixels=leds.count()
        if offset > max_pixels:
            print("Eror: offset too far")
            offset=0
        string_length = length * step
        if offset + string_length > max_pixels :
            print("Error : not enough pixels for that....")
            print("Going from {0:}  to {1:} exceeds max {2:}".format(offset, offset + string_length, max_pixels ))
            string_length = max_pixels - offset
            length = string_length // step
        self.offset = offset
        self.length = length
        self.pixels = leds
        self.index = [x + offset for x in range(0,string_length,step)]

    def get_state(self):
        current_state=[]
        for i in range(self.length):
            current_state.append(self.pixels.get_pixel_rgb(self.index[i]))
        return current_state

    def record_state(self):
        self.state = get_state()

    def fade_to_state(self, new_state, steps=25):
        if self.length != len(new_state):
            print("Error in fade_to_state : Length of states not consistent")
            return
        old_state = self.get_state()
        for step in range(steps):
            scale_out = int(100*( steps - (step + 1.0) ) / steps)
            scale_in  = 100 - scale_out
            for i in range(self.length):
                old_r, old_g, old_b = old_state[i]
                new_r, new_g, new_b = new_state[i]
                cur_r, cur_g, cur_b = (
                       ((old_r * scale_out + new_r * scale_in) // 100) ,
                       ((old_g * scale_out + new_g * scale_in) // 100) ,
                       ((old_b * scale_out + new_b * scale_in) // 100) )
            #print("step {0:3d} : r{1:3d} g{2:3d} b{3:3d}".format(step, cur_r, cur_g, cur_b))
                pixels.set_pixel(self.index[i],
                        Adafruit_WS2801.RGB_to_color( cur_r, cur_g, cur_b ))
            yield

    def fade_to_color(self, color=(0, 0, 0), steps=25):
        new_state = []
        for i in range(self.length):
            new_state.append(color)
        return self.fade_to_state(new_state, steps)
 
    def fade_to_black(self, steps=25):
        return self.fade_to_color(color=(0, 0, 0), steps=steps)
 
    def fade_to_white(self, steps=25):
        return self.fade_to_color(color=(255, 255, 255), steps=steps)
 
    def rotate_state(self, steps=25, skip=1, reverse=False):
        current_state = self.get_state()
        if reverse:
            skip = 0 - skip
        for step in range(steps):
            new_state = ( current_state[0+skip:self.length] +
                          current_state[0:(skip - self.length)% self.length] )
            for i in range(self.length):
                pixels.set_pixel(self.index[i],
                        Adafruit_WS2801.RGB_to_color( *new_state[i] ))
                current_state = new_state
            #print('rotate state, iter = {0:3d}'.format(step))
            yield

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
    pos = pos % spread
    band = spread/3.0
    if pos < band:
        return Adafruit_WS2801.RGB_to_color(pos, int(band - pos), 0)
    elif pos < (2 * band):
        pos -= int(band)
        return Adafruit_WS2801.RGB_to_color(int(band - pos), 0, pos)
    else:
        pos -= int(2 * band)
        return Adafruit_WS2801.RGB_to_color(0, pos, int(band - pos))

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
            
 
if __name__ == "__main__":
    # Set up some basic 'shapes' to play with lights in
    #snowman1 = Pixel_Section(pixels, 98, 2)
    #snowman2 = Pixel_Section(pixels, 95, 2)
    whole_window = Pixel_Section(pixels, 0, 50, step=1)
    r_window = Pixel_Section(pixels, 40, 10, step=1)
    l_window = Pixel_Section(pixels, 0, 10, step=1)
    r_window_a = Pixel_Section(pixels, 41, 2, step=4)
    r_window_b = Pixel_Section(pixels, 42, 2, step=4)
    r_window_c = Pixel_Section(pixels, 43, 2, step=4)
    r_window_d = Pixel_Section(pixels, 44, 2, step=4)
    l_window_a = Pixel_Section(pixels, 1, 2, step=4)
    l_window_b = Pixel_Section(pixels, 2, 2, step=4)
    l_window_c = Pixel_Section(pixels, 3, 2, step=4)
    l_window_d = Pixel_Section(pixels, 4, 2, step=4)
    #r_window_edge = Pixel_Section(pixels, 19, 15)
    #l_window_edge = Pixel_Section(pixels, 66, 15)

    red    = (200,   0,   0)
    green  = (  0, 200,   0)
    blue   = (  0,   0, 200)
    yellow = (255, 255,   4)

    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()  # Make sure to call show() after changing any pixels!
 
    run_for = 720
    set1_do = r_window.rainbow_cycle(steps=run_for, laps=12)
    set2_do = l_window.rainbow_cycle(steps=run_for, laps=12, reverse=True)
    #set3_do = r_window_edge.rainbow_cycle_successive(steps=run_for)
    #set4_do = l_window_edge.rainbow_cycle_successive(steps=run_for, reverse=True)
    #snowman_1_do = snowman1.rainbow_cycle(steps=run_for, laps=24, arc_span=20)
    #snowman_2_do = snowman2.rainbow_cycle(steps=run_for, laps=24, arc_span=20,
    #                                      reverse=True)
    for i in range(run_for):
        #print(i)
        set1_do.next()
        set2_do.next()
        #set3_do.next()
        #set4_do.next()
        #snowman_1_do.next()
        #snowman_2_do.next()
        pixels.show()
        time.sleep(.05)
    time.sleep(2)

    run_for = 20
    set1_do = r_window.go_out_successive(steps=run_for)
    set2_do = l_window.go_out_successive(steps=run_for, reverse=True)
    #set3_do = r_window_edge.go_out_successive(steps=run_for)
    #set4_do = l_window_edge.go_out_successive(steps=run_for, reverse=True)
    #snowman_1_do = snowman1.go_out_successive(steps=run_for)
    #snowman_2_do = snowman1.go_out_successive(steps=run_for, reverse=True)
    for i in range(run_for):
        #print(i)
        set1_do.next()
        set2_do.next()
        #set3_do.next()
        #set4_do.next()
        #snowman_1_do.next()
        #snowman_2_do.next()
        pixels.show()
        time.sleep(.5)
    time.sleep(2)

    run_for=360
    #snowman_1_do = snowman1.rainbow_cycle(steps=run_for, full_wheel=120,
    #                                      arc_span=30, laps=3)
    #snowman_2_do = snowman2.rainbow_cycle(steps=run_for, full_wheel=120,
    #                                      arc_span=30, laps=3, reverse=True)
    #for i in range(run_for):
    ##    #print(i)
    #    snowman_1_do.next()
    #    snowman_2_do.next()
    #    pixels.show()
    #    time.sleep(.05)

    run_for=360
    #snowman_1_do= snowman1.rainbow_cycle(steps=run_for, full_wheel=120,
    #                                     arc_span=120, laps=3)
    #snowman_2_do = snowman2.rainbow_cycle(steps=run_for, full_wheel=120,
    #                                     arc_span=120, laps=3, reverse=True)
    whole_window_do = whole_window.rainbow_cycle(steps=run_for, full_wheel=120,
                                                 arc_span=120, laps=6)
    for i in range(run_for):
    #    #print(i)
        #snowman_1_do.next()
        #snowman_2_do.next()
        whole_window_do.next()
        pixels.show()
        time.sleep(.05)

    run_for=20
    r_window_a_do = r_window_a.light_up_successive(steps=run_for, colour=red)
    r_window_b_do = r_window_b.light_up_successive(steps=run_for, colour=green)
    r_window_c_do = r_window_c.light_up_successive(steps=run_for, colour=blue)
    r_window_d_do = r_window_d.light_up_successive(steps=run_for, colour=yellow)
    l_window_a_do = l_window_a.light_up_successive(steps=run_for, colour=red,
                                                   reverse=True)
    l_window_b_do = l_window_b.light_up_successive(steps=run_for, colour=green,
                                                   reverse=True)
    l_window_c_do = l_window_c.light_up_successive(steps=run_for, colour=blue,
                                                   reverse=True)
    l_window_d_do = l_window_d.light_up_successive(steps=run_for, colour=yellow,
                                                   reverse=True)
    for i in range(run_for):
        #print(i)
        r_window_a_do.next()
        r_window_b_do.next()
        r_window_c_do.next()
        r_window_d_do.next()
        l_window_a_do.next()
        l_window_b_do.next()
        l_window_c_do.next()
        l_window_d_do.next()
        pixels.show()
        time.sleep(0.5)

    run_for=20
    r_window_do = r_window.rotate_state(steps=run_for, reverse=False)
    l_window_do = l_window.rotate_state(steps=run_for, reverse=True)
    for i in range(run_for):
        #print(i)
        r_window_do.next()
        l_window_do.next()
        pixels.show()
        time.sleep(0.5)

    r_window_a_do = r_window_a.go_out_successive(steps=run_for)
    r_window_b_do = r_window_b.fade_to_black(steps=run_for)
    r_window_c_do = r_window_c.go_out_successive(steps=run_for)
    r_window_d_do = r_window_d.fade_to_black(steps=run_for)
    l_window_a_do = l_window_a.fade_to_black(steps=run_for)
    l_window_b_do = l_window_b.go_out_successive(steps=run_for, reverse=True)
    l_window_c_do = l_window_c.fade_to_black(steps=run_for)
    l_window_d_do = l_window_d.go_out_successive(steps=run_for, reverse=True)
    for i in range(run_for):
        #print(i)
        r_window_a_do.next()
        r_window_b_do.next()
        r_window_c_do.next()
        r_window_d_do.next()
        l_window_a_do.next()
        l_window_b_do.next()
        l_window_c_do.next()
        l_window_d_do.next()
        pixels.show()
        time.sleep(.7)

    for trips in range(3):
        reverse = randint(0,1) == 1
        colour = Adafruit_WS2801.color_to_RGB(get_random_colour(360))
        run_for = whole_window.length
        whole_window_do = whole_window.appear_from_end(color=colour,
                                                       reverse=reverse)
        #snowman_1_do= snowman1.rainbow_cycle(steps=run_for, full_wheel=120,
        #                                     arc_span=10, laps=3)
        #snowman_2_do = snowman2.rainbow_cycle(steps=run_for, full_wheel=120,
        #                                     arc_span=10, laps=3, reverse=True)
        for i in range(whole_window.length-1):
            #print(i)
            whole_window_do.next()
            #snowman_1_do.next()
            #snowman_2_do.next()
            pixels.show()
            time.sleep(0.1)

    for trips in range(5):
        run_for = r_window.length
        reverse1 = randint(0,1) == 1
        reverse2 = randint(0,1) == 1
        colour1 = Adafruit_WS2801.color_to_RGB(get_random_colour(360))
        colour2 = Adafruit_WS2801.color_to_RGB(get_random_colour(360))
        r_window_do = r_window.appear_from_end(color=colour1,
                                                   reverse=reverse1)
        l_window_do = l_window.appear_from_end(color=colour2,
                                                   reverse=reverse2)
        #snowman_1_do= snowman1.rainbow_cycle(steps=run_for, full_wheel=120,
        #                                     arc_span=20, laps=3)
        #snowman_2_do = snowman2.rainbow_cycle(steps=run_for, full_wheel=120,
        #                                     arc_span=20, laps=3, reverse=True)
        for i in range(r_window.length-1):
            #print(i)
            r_window_do.next()
            l_window_do.next()
            #snowman_1_do.next()
            #snowman_2_do.next()
            pixels.show()
            time.sleep(0.1)

    run_for = 100
    whole_window_do = whole_window.fade_to_black(steps=run_for)
    for i in range(run_for):
        #print(i)
        whole_window_do.next()
        pixels.show()
        time.sleep(.7)

    #subset6 = Pixel_Section(pixels, 30, 20, step=1)
    #subset7 = Pixel_Section(pixels, 50, 20, step=1)
    #run_for=20
    #set6_do = subset6.rainbow_cycle_successive(steps=run_for, reverse=False)
    #set7_do = subset7.rainbow_cycle_successive(steps=run_for,reverse=True)
    #for i in range(run_for):
    #    #print(i)
    #    set6_do.next()
    #    set7_do.next()
    #    pixels.show()
    #    time.sleep(0.5)
    #run_for=120
    #set6_do = subset6.rainbow_cycle(steps=run_for, reverse=False)
    #set7_do = subset7.rainbow_cycle(steps=run_for,reverse=True)
    #for i in range(run_for):
    #    #print(i)
    #    set6_do.next()
    #    set7_do.next()
    #    pixels.show()
    #    time.sleep(0.5)
    #fade_to_black(pixels, wait=0.1, steps=50)
    #run_for=60
    #set6_do = subset6.fade_to_black(steps=run_for)
    #set7_do = subset7.fade_to_white(steps=run_for)
    #for i in range(run_for):
    #    #print(i)
    #    set6_do.next()
    #    set7_do.next()
    #    pixels.show()
    #    time.sleep(0.5)

