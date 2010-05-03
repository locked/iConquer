import re, jsonpickle, random, urllib
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, loader, TemplateDoesNotExist
from django.utils import html, translation, simplejson
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from django.core import serializers

#from django.db.models.loading import get_models
#loaded_models = get_models()
from rts.models import *
from astarfromjs import AStarJS

GRD_GRD = 0
GRD_WALL_H = 2
GRD_WALL_V = 3
GRD_WALL_HR = 4
GRD_WALL_HL = 5
GRD_WALL_VT = 6
GRD_WALL_VB = 7
GRD_WALL_CTL = 8
GRD_WALL_CTR = 9
GRD_WALL_CBL = 10
GRD_WALL_CBR = 11

GRD_SPICE = 20

MAP_WIDTH = 90
MAP_HEIGHT = 40

RTS_TICK = 0.04
CHECKPOINT = 360

TILE_SIZE = 24

SPICE_MAX_LEVEL = 10000


def find_path(startpoint, endpoint, ground, method='astar'):
	import AStar
	
	path = []
	if method=='astar':
		astar = AStarJS( ground )
		path = astar.findPath(startpoint,endpoint)
		"""
		astar = AStar.AStar(AStar.SQ_MapHandler(grid,len(ground[0]),len(ground)))
		start = AStar.SQ_Location(startpoint[0],startpoint[1])
		end = AStar.SQ_Location(endpoint[0],endpoint[1])
		# Find path
		p = astar.findPath(start,end)
		for n in p.nodes:
			path.append( [n.location.x, n.location.y] )
		"""
	return path


def load_shadow( gs, ground ):
	from rts.models import Shadow
	alls = Shadow.objects.filter( gamestatus=gs )
	shadow = {}
	print "LOAD SHADOW ", gs.player.id
	for y, xs in ground.items():
		for x, v in xs.items():
			if y not in shadow:
				shadow[y] = {}
			fs = None
			for s in alls:
				if s.x==x and s.y==y:
					fs = s
					break
			if not fs:
				fs = Shadow( gamestatus=gs, x=x, y=y, v=1 )
				#fs.save()
			shadow[y][x] = fs
	return shadow
	

def load_ground( g ):
	from rts.models import GroundData
	grd = GroundData.objects.filter( ground=g.ground )
	ground = {}
	for g in grd:
		if g.y not in ground:
			ground[g.y] = {}
		ground[g.y][g.x] = [g.v,0,1]
	return ground

"""
def load_grid( ground ):
	grid = []
	for y,xs in ground.items():
		#l = []
		for x,v in xs.items():
			#if v[0:4]=="wall":
			if v[0]>=2 and v[0]<=11:
				grid.append( -1 )
			else:
				grid.append( 0 )
		#grid.append( l )
	return grid
"""

