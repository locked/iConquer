import os, sys
import Image, ImageDraw

# Palettes matcher
colors = {}
colors["red"] = [
[(246,214,121),(255,0,0,255)],
[(230,230,230),(245,0,0,255)],
[(230,202,113),(245,0,0,255)],
[(214,190,105),(245,0,0,255)],
[(198,178,97),(235,0,0,255)],
[(182,165,89),(225,0,0,255)],
[(170,153,85),(215,0,0,255)],
[(145,137,76),(205,0,0,255)],
[(145,117,64),(205,0,0,255)],
[(133,113,56),(195,0,0,255)],
[(109,101,56),(175,0,0,255)],
[(89,85,44),(165,0,0,255)],
[(85,76,36),(160,0,0,255)],
[(72,68,32),(150,0,0,255)],
[(56,52,28),(124,0,0,255)],
[(52,44,20),(120,0,0,255)],
[(40,32,8),(110,0,0,255)],
]
colors["blue"] = [
[(246,214,121),(50,100,255,255)],
[(230,230,230),(100,100,245,255)],
[(230,202,113),(50,100,245,255)],
[(214,190,105),(50,100,235,255)],
[(198,178,97),(50,100,225,255)],
[(182,165,89),(50,100,215,255)],
[(170,153,85),(50,80,205,255)],
[(145,137,76),(50,50,195,255)],
[(145,117,64),(50,50,195,255)],
[(133,113,56),(50,50,185,255)],
[(109,101,56),(50,50,165,255)],
[(89,85,44),(50,50,155,255)],
[(85,76,36),(50,50,150,255)],
[(72,68,32),(50,50,140,255)],
[(56,52,28),(50,50,114,255)],
[(52,44,20),(50,50,110,255)],
[(40,32,8),(50,50,100,255)],
]
colors["yellow"] = []

# Folder of images to assemble
toproot = "/hd1/hosting/iconquer"
types = []
for dirname in os.listdir(toproot+"/scripts"):
	if dirname=='merge_imgs.py' or dirname=='img.py':
		continue
	if dirname=='tanya':
		types.append( dirname )

print "types: ", types

nocol_types = ["explosion","shadow"]
for type in types:
	top = toproot+"/scripts/"+type
	dirnames = []
	for root, dirs, files in os.walk(top):
		for dirname in dirs:
			dirnames.append( dirname )
	
	dirnames = sorted(dirnames)
	print dirnames
	
	fnss = {}
	for dirname in dirnames:
		fnss[dirname] = []
		for root, dirs, files in os.walk(top+"/"+dirname):
			for name in files:
				fn = top + "/"+dirname + "/" + name
				fnss[dirname].append( fn )
		fnss[dirname] = sorted(fnss[dirname])
	
	imss = {}
	maxw = 0
	maxh = 0
	nb = 0
	lines = 0
	for dn, fns in fnss.items():
		imss[dn] = []
		for fn in fns:
			im = Image.open(fn)
			# Get the max size of all images
			(w,h) = im.size
			if w>maxw: maxw = w
			if h>maxh: maxh = h
			imss[dn].append( im )
		if len(fns)>nb: nb = len(fns)
		lines += 1
	
	print "target image size: ", maxw*nb,maxh*lines
	
	for color,clist in colors.items():
		mode = 'RGBA'
		size = (maxw*nb,maxh*lines)
		target = Image.new(mode, size)
		
		# Transparent color limit
		l = 0
		
		# Semi transparent color
		semitrans = (89,255,85)
		line = 0
		for dirname in dirnames:
			ims = imss[dirname]
			print dirname
			#for dn, ims in imss.items():
			ind = 0
			for im in ims:
				(w,h) = im.size
				#print "Current image size: ", (w,h)
				pal = im.getpalette()
				for x in range(0,w):
					for y in range(0,h):
						pind = None
						try:
							# Try with alpha
							(r,g,b,a) = im.getpixel((x,y))
						except:
							try:
								(r,g,b) = im.getpixel((x,y))
							except:
								pind = im.getpixel((x,y))
								(r,g,b) = pal[3*pind : 3*pind+3]
						istrans = False
						if pind is None:
							if r<=l and g<=l and b<=l:
								istrans = True
						else:
							if pind==0:
								istrans = True
						a = 255
						if istrans:
							# Set to full transparent
							r = 0
							g = 0
							b = 0
							a = 0
						if (r,g,b)==semitrans:
							# Set to gray and semi transparent
							r = 50
							g = 50
							b = 50
							a = 150
						if clist!=[] and type not in nocol_types:
							for c in clist:
								if c[0]==(r,g,b):
									# Found a color to replace
									(r,g,b,a) = c[1]
									#print "MATCH", (r,g,b,a)
						# Set color
						try:
							target.putpixel((x+ind*maxw,y+line*maxh), (r,g,b,a))
						except:
							print (x+ind*maxw,y+line*maxh), (r,g,b,a)
				ind += 1
			line += 1
		
		# write to stdout
		if type in nocol_types:
			outfn = toproot+"/static/graphics/general/"+type+".png"
		else:
			outfn = toproot+"/static/graphics/nod/"+color+"/"+type+".png"
		print "write: ", outfn
		target.save(outfn,"PNG")
