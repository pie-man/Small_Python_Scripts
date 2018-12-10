#!/usr/bin/env python
# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
from flask import Flask
# To install and run flask:
# $ pip install Flask
# $ FLASK_APP=tree.py flask run
# and then point a webbrowser to the Pi's IP address, port 5000 and page
# top/colour, middle/colour, bottom/colour (i.e.
# http://aaa.bbb.ccc.ddd:5000/top/RGB). Not sure how you're expressing RGB,
# but it should be the same in the URL as in the q.make_colour_state
# function.  Dynamic DNS and a proper webserver (e.g. apache) needed for more
# than basic testing! I can help set this up.  Ideally, you'd run a browser
# locally on the pi, in which case you can use http://localhost:5000/top/RGB.
# We should probably show something in the browser too.

import pixel_strings_fncs as q


app = Flask(__name__)
# Configure the count of pixels:
PIXEL_COUNT = 46
TOP = range(37, 46)
MIDDLE = range(22, 33)
BOTTOM = range(18)


def set_tree():
    '''Insert docstring here'''
    pixels = q.initialise_pixels(PIXEL_COUNT)
    top_state = q.make_rainbow_state(TOP)
    middle_state = q.make_rainbow_state(MIDDLE)
    bottom_state = q.make_rainbow_state(BOTTOM)
    q.set_state(pixels, TOP, top_state)
    q.set_state(pixels, MIDDLE, middle_state)
    q.set_state(pixels, BOTTOM, bottom_state)
    pixels.show()


@app.route('/top/<colour>')
def set_top(colour):
    pixels = q.initialise_pixels(PIXEL_COUNT)
    q.set_state_rgb(pixels, TOP, q.make_colour_state(TOP, colour))
    pixels.show()


@app.route('/middle/<colour>')
def set_middle(colour):
    pixels = q.initialise_pixels(PIXEL_COUNT)
    q.set_state_rgb(pixels, MIDDLE, q.make_colour_state(MIDDLE, colour))
    pixels.show()


@app.route('/bottom/<colour>')
def set_bottom(colour):
    pixels = q.initialise_pixels(PIXEL_COUNT)
    q.set_state_rgb(pixels, BOTTOM, q.make_colour_state(BOTTOM, colour))
    pixels.show()


if __name__ == '__main__':
    set_tree()
