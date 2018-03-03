# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
 
# Configure the count of pixels:
PIXEL_COUNT = 100
 
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
            string_length = max_pixels - offset
            length = string_length // step
        self.offset = offset
        self.length = length
        self.pixels = leds
        self.index = [x + offset for x in range(0,string_length,step)]

    def rainbow_cycle_successive(self, steps=10, 
                         full_wheel=256, arc_span=256,
                         laps=1, reverse=False):
        clusters = pixels_by_step(self.length, steps)
        if reverse:
            clusters.reverse()
        count = 0
        for cluster in clusters:
            # tricky math!
            # we use each pixel as a fraction of the full full_wheel-color wheel
            # (thats the i * full_wheel / slef.length part)
            # Then add in cluster which makes the colors go around per pixel
            # the % full_wheel is to make the wheel cycle around
            pixel_locations = get_wheel_position(self.length, count, steps,
                       laps=laps, full_wheel=full_wheel, arc_span=arc_span,
                       reverse=reverse)
            for i in cluster:
                #pixel_no=i+self.offset
                location = pixel_locations[i]
                colour = wheel2(location, spread=full_wheel)
                print("pixel no. = {0:3d} position {1:3d}".format(self.index[i], location))
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
                colour = wheel2(pixel_positions[i], spread=full_wheel)
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
        self.light_up_successive(steps, (0,0,0), reverse)

def pixels_by_step(count,steps):
    fred=[int(float(count * x)/steps) for x in range(steps)]
    fred.append(count)
    print (fred)
    list_out=[]
    for i in range(len(fred)-1):
        if fred[i] == fred[i+1]:
            dave = [fred[i]]
        else:
            dave= range(fred[i],fred[i+1])
        print("iter {0:3d} : {1:}".format(i, dave))
        list_out.append(dave)
    return list_out

def get_wheel_position(pixel_length, loop_index, steps_total,
                       laps=1, full_wheel=256, arc_span=256, reverse=False):
    start_pos = int((loop_index / float(steps_total)) * laps * full_wheel)
    pixel_locs = [(int(x * (float(arc_span) / float(pixel_length)))
                  + start_pos) % full_wheel for x in range(pixel_length)]
    if reverse:
        pixel_locs.reverse()
    print("start_pos = {0:4d} : pixels at : {1:}".format(start_pos, pixel_locs))
    return pixel_locs

# Define the wheel function to interpolate between different hues.
# This function defines 255 separate colours
def wheel(pos):
    pos = pos % 255
    if pos < 85:
        return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)
 
# Define an alternative function to interpolate between different hues.
# This function defines 'spread' separate colours
def wheel2(pos, spread):
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
 
# Define rainbow cycle function to do a cycle of all hues.
def rainbow_cycle_successive(pixels, wait=0.1, reverse=False):
    order = range(pixels.count())
    if reverse:
        order.reverse()
    for i in order:
        # tricky math! we use each pixel as a fraction of the full 256-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 256 is to make the wheel cycle around
        pixels.set_pixel(i, wheel(((i * 256 // pixels.count())) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def go_out_successive(pixels, wait=0.1, reverse=False):
    order = range(pixels.count())
    if reverse:
        order.reverse()
    for i in order:
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(0, 0, 0) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)

def rainbow_cycle(pixels, wait=0.005):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((i * 256 // pixels.count()) + j) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def mirror_rainbow_cycle(pixels, wait=0.005):
    for j in range(1024): # two cycles of all 256 colors in the wheel
        len_pixels = pixels.count()
        for i in range(len_pixels/2):
            pixels.set_pixel(i, wheel(((i * 256 // (len_pixels//2)) + j) % 256) )
            pixels.set_pixel((len_pixels-(i+1)), wheel(((i * 256 // (len_pixels//2)) + j) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_colors(pixels, wait=0.05):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((256 // pixels.count() + j)) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
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
 
def fade_to_color(pixels, color=(0, 0, 0), wait=0.01, steps=25):
    new_state = []
    for i in range(pixels.count()):
        new_state.append(color)
    fade_to_state(pixels, new_state, wait, steps)
 
def fade_to_black(pixels, wait=0.01, steps=25):
    fade_to_color(pixels, color=(0, 0, 0), wait=wait, steps=steps)
 
def burn_out(pixels, wait=0.01, steps=25):
    new_state = []
    for i in range(pixels.count()):
        new_state.append((255, 255, 255))
    fade_to_state(pixels, new_state, wait, steps)

def fade_to_state(pixels, new_state, wait=0.01, steps=25):
    old_state = []
    len_old = pixels.count()
    #len_old = pixels
    len_new = len(new_state)
    if len_old != len_new:
        print("Error in fade_to_state : Length of states not consistent")
        return
    for i in range(len_old):
        old_state.append(pixels.get_pixel_rgb(i))
        #old_state.append(wheel(int((255//10.0)* i)))
        new_state.append((0, 0, 0))
    for step in range(steps):
        scale_out = int(100*( steps - (step + 1.0) ) / steps)
        scale_in  = 100 - scale_out
        for i in range(len_old):
            old_r, old_g, old_b = old_state[i]
            new_r, new_g, new_b = new_state[i]
            cur_r, cur_g, cur_b = (
                   ((old_r * scale_out + new_r * scale_in) // 100) ,
                   ((old_g * scale_out + new_g * scale_in) // 100) ,
                   ((old_b * scale_out + new_b * scale_in) // 100) )
        #print("step {0:3d} : r{1:3d} g{2:3d} b{3:3d}".format(step, cur_r, cur_g, cur_b))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(
                                                cur_r, cur_g, cur_b ))
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
 
def appear_from_back(pixels, color=(255, 0, 0)):
    pos = 0
    for i in range(pixels.count()):
        for j in reversed(range(i, pixels.count())):
            pixels.clear()
            # first set all pixels at the begin
            for k in range(i):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            # set then the pixel at position j
            pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            pixels.show()
            time.sleep(0.02)
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
    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()  # Make sure to call show() after changing any pixels!
 
    #rainbow_cycle_successive(pixels, wait=0.1)
    #rainbow_cycle(pixels, wait=0.01)
 
    #brightness_decrease(pixels)
    #
    #rainbow_cycle_successive(pixels, wait=0.1)
    #rainbow_cycle(pixels, wait=0.01)
 
    #go_out_successive(pixels)
    #
    #rainbow_cycle_successive(pixels, wait=0.1)
    #rainbow_cycle(pixels, wait=0.01)
 
    #go_out_successive(pixels, reverse=True)
    
    #mirror_rainbow_cycle(pixels, wait=0.01)
    ##appear_from_back(pixels, color=(100,0,125))

    ##for i in range(3):
    ##    blink_color(pixels, blink_times = 1, color=(100, 0, 0))
    ##    blink_color(pixels, blink_times = 1, color=(0, 100, 0))
    ##    blink_color(pixels, blink_times = 1, color=(0, 0, 100))

    ##rainbow_colors(pixels)

    ##brightness_decrease(pixels)
    #set_A=[]
    ##for i in range(0,pixels.count(),4):
    ##    print("looking at counter {0:d}".format(i))
    ##    set_A.append(i)
    ##ping_pong(pixels)
    ##ping_pong(pixels, color1=(110,0,110), color2=(100,50,0))
    #rainbow_cycle_successive(pixels, wait=0.1)
    #rainbow_cycle(pixels, wait=0.1)
    #fade_to_black(pixels, wait=0.1, steps=75)
    #time.sleep(2)
    #rainbow_cycle(pixels, wait=0.01)
    #burn_out(pixels, wait=0.1, steps=25)
    #time.sleep(3)
    #fade_to_black(pixels, wait=0.1, steps=25)
    #subset1 = Pixel_Section(pixels, 0, 20)
    #subset2 = Pixel_Section(pixels, 20, 20)
    #subset3 = Pixel_Section(pixels, 40, 20)
    #subset4 = Pixel_Section(pixels, 60, 20)
    #subset5 = Pixel_Section(pixels, 80, 20)
    #run_for = 360
    #set1_do = subset3.rainbow_cycle(steps=run_for)
    #set2_do = subset1.rainbow_cycle_successive(steps=run_for)
    #set3_do = subset5.rainbow_cycle_successive(steps=run_for, reverse=True)
    #for i in range(run_for):
    #    print(i)
    #    set1_do.next()
    #    set3_do.next()
    #    set2_do.next()
    #    pixels.show()
    #    time.sleep(.05)
    #time.sleep(5)
    #fade_to_black(pixels, wait=0.1, steps=50)
    #run_for = 360
    #set1_do = subset2.rainbow_cycle(steps=run_for)
    #set2_do = subset4.rainbow_cycle(steps=run_for, reverse=True)
    #for i in range(run_for):
    #    print(i)
    #    set1_do.next()
    #    set2_do.next()
    #    pixels.show()
    #    time.sleep(.05)
    #run_for = 360
    #set1_do = subset4.go_out_successive(steps=run_for, reverse=True)
    #set2_do = subset2.go_out_successive(steps=run_for)
    #for i in range(run_for):
    #    print(i)
    #    set1_do.next()
    #    set2_do.next()
    #    pixels.show()
    #    time.sleep(.05)
    #run_for=360
    #set1_do = subset1.light_up_successive(steps=run_for, colour=(200,0,200), reverse=True)
    #set2_do = subset2.light_up_successive(steps=run_for, colour=(200,0,200), reverse=False)
    #set3_do = subset3.rainbow_cycle(steps=run_for, reverse=True)
    #set4_do = subset4.light_up_successive(steps=run_for, colour=(200,0,200), reverse=True)
    #set5_do = subset5.light_up_successive(steps=run_for, colour=(200,0,200), reverse=False)
    #for i in range(run_for):
    #    print(i)
    #    set1_do.next()
    #    set2_do.next()
    #    set3_do.next()
    #    set4_do.next()
    #    set5_do.next()
    #    pixels.show()
    #    time.sleep(.05)

    run_for=360
    #fade_to_black(pixels, wait=0.1, steps=125)
    subset6 = Pixel_Section(pixels, 98, 2)
    subset7 = Pixel_Section(pixels, 95, 2)
    subset8 = Pixel_Section(pixels, 30, 20)
    subset9 = Pixel_Section(pixels, 50, 20)
    set6_do = subset6.rainbow_cycle(steps=run_for, full_wheel=120, arc_span=30, laps=3)
    set7_do = subset7.rainbow_cycle(steps=run_for, full_wheel=120, arc_span=30, laps=3, reverse=True)
    for i in range(run_for):
        print(i)
        set6_do.next()
        set7_do.next()
        pixels.show()
        time.sleep(.05)
    run_for=360
    set6_do = subset6.rainbow_cycle(steps=run_for, full_wheel=120, arc_span=120, laps=3)
    set7_do = subset7.rainbow_cycle(steps=run_for, full_wheel=120, arc_span=120, laps=3, reverse=True)
    set8_do = subset8.rainbow_cycle(steps=run_for, full_wheel=120, arc_span=120, laps=6)
    set9_do = subset9.rainbow_cycle(steps=run_for, full_wheel=120, arc_span=120, laps=6, reverse=True)
    for i in range(run_for):
        print(i)
        set6_do.next()
        set7_do.next()
        set8_do.next()
        set9_do.next()
        pixels.show()
        time.sleep(.075)
    run_for=15
    set8_do = subset8.light_up_successive(steps=run_for )
    set9_do = subset9.light_up_successive(steps=run_for, reverse=True)
    for i in range(run_for):
        print(i)
        set8_do.next()
        set9_do.next()
        pixels.show()
        time.sleep(1)
    run_for=21
    subset6 = Pixel_Section(pixels, 30, 10, step=2)
    subset7 = Pixel_Section(pixels, 50, 10, step=2)
    subset8 = Pixel_Section(pixels, 31, 10, step=2)
    subset9 = Pixel_Section(pixels, 51, 10, step=2)
    set6_do = subset6.light_up_successive(steps=run_for, colour=(0,0,200))
    set7_do = subset7.light_up_successive(steps=run_for, colour=(0,0,200), reverse=True)
    set8_do = subset8.light_up_successive(steps=run_for, colour=(200,0,0))
    set9_do = subset9.light_up_successive(steps=run_for, colour=(200,0,0), reverse=True)
    for i in range(run_for):
        print(i)
        set6_do.next()
        set7_do.next()
        set8_do.next()
        set9_do.next()
        pixels.show()
        time.sleep(2)
    #set6_do = subset6.go_out_successive(steps=run_for)
    #set7_do = subset7.go_out_successive(steps=run_for, reverse=True)
    #set8_do = subset8.go_out_successive(steps=run_for)
    #set9_do = subset9.go_out_successive(steps=run_for, reverse=True)
    #for i in range(run_for):
    #    print(i)
    #    set6_do.next()
    #    set7_do.next()
    #    set8_do.next()
    #    set9_do.next()
    #    pixels.show()
    #    time.sleep(.7)
    run_for=50
    set6_do = subset6.rainbow_cycle_successive(steps=run_for,reverse=False)
    set7_do = subset7.rainbow_cycle_successive(steps=run_for,reverse=True)
    set8_do = subset8.rainbow_cycle_successive(steps=run_for,reverse=False)
    set9_do = subset9.rainbow_cycle_successive(steps=run_for,reverse=True)
    for i in range(run_for):
        print(i)
        set6_do.next()
        set7_do.next()
        set8_do.next()
        set9_do.next()
        pixels.show()
        time.sleep(0.5)
