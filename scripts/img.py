import os, sys
import Image, ImageDraw

fn = '/hd1/hosting/iconquer/scripts/dog/line1/dog 000.png'
im = Image.open(fn)
pal = im.getpalette()
ind = im.getpixel((10,14))
print "10, 15", ind, pal[3*ind : 3*ind+3]
ind = im.getpixel((23,14))
print "15, 15", ind, pal[3*ind : 3*ind+3]

