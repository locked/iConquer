# -*- coding: utf-8 -*-

import re, jsonpickle, random

from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, loader, TemplateDoesNotExist
from django.utils import html, translation, simplejson
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required

from django.core import serializers

from rts.models import *

from librts import *

from astarfromjs import AStarJS


def load_game( game_id ):
	game = Game.objects.get( id=int(game_id) )
	return game


#
# Django requests
#
def get_all_obj_tiles(request):
	alltiles = []
	for tc in Team.type_choices:
		for color in Team.color_choices:
			for ot in ObjType.objects.all():
				alltiles.append( "/static/graphics/"+tc[0]+"/"+color[0]+"/"+ot.objclass+".png" )
	return HttpResponse( simplejson.dumps( alltiles ) )


def get_ground(request, gameid):
	g = load_game( gameid )
	p = request.user.get_profile()
	gs = GameStatus.objects.get( game=g, player=p )
	ground = load_ground( g )
	resp = { 'ground':ground };
	resp['gs'] = { 'viewx':gs.viewx, "viewy":gs.viewy, "team_id":gs.team_id };
	return HttpResponse( simplejson.dumps( resp ) )



@login_required
def game(request, gameid):
	template = "game.html"
	p = request.user.get_profile()
	g = load_game( gameid )
	p.game = g
	p.save()
	gs = GameStatus.objects.get( game=g, player=p )
	
	context = {}
	context['map_tiles_x'] = MAP_WIDTH
	context['map_tiles_y'] = MAP_HEIGHT
	context['map_width'] = context['map_tiles_x'] * 24
	context['map_height'] = context['map_tiles_y'] * 24
	
	context['game'] = g
	context['objtypes'] = serializers.serialize('json', ObjType.objects.all())
	context['players'] = serializers.serialize('json', Player.objects.all())
	context['teams'] = serializers.serialize('json', Team.objects.all())
	return render_to_response(template, context, RequestContext(request))


@login_required
def menu(request):
	from django.contrib.auth.models import User
	template = "menu.html"
	context = {}
	p = request.user.get_profile()
	context['player'] = p
	context['games'] = []
	for gs in p.gamestatus_set.all():
		context['games'].append( gs.game )
	context['agames'] = []
	for g in Game.objects.all():
		if g not in context['games']:
			context['agames'].append( g );
	return render_to_response(template, context, RequestContext(request))
	
