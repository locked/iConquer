#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 * iConquer - Online C&C-like game
 * Copyright (C) 2009-2010 Adam Etienne <etienne.adam@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * $Id$
'''

import re, os, sys, getopt, time, datetime, random
from django.core.management import execute_manager, setup_environ
from django.utils import simplejson
from django.core import serializers
import settings # Assumed to be in the same directory.

import MySQLdb
import httplib,urllib
from astarfromjs import AStarJS

from librts import *

from twisted.internet import reactor
from twisted.web import server, resource


from twisted.application import internet, service
from twisted.web import server, resource, static
from twisted.internet import defer, task
import slosh



def clear():
	print("\x1B[2J")

class Server:
	def __init__(self):
		self.games = []
		self.maps = []
		self.grs = {}
		self.db()
		self.verbose = 0
		self.psloshes = {}
	
	def db(self):
		self.db = MySQLdb.connect(user="rts",passwd="rts",db="rts")
	
	def gen_map( self, name ):
		c = self.db.cursor()
		map = {}
		map_w = MAP_WIDTH
		map_h = MAP_HEIGHT
		for y in range(0,map_h):
			for x in range(0,map_w):
		#rnd = random.randint(1, 3);
				if y not in map:
					map[y] = {}
		map[y][x] = GRD_GRD;
		for y in range(4,14):
			map[y][4] = GRD_WALL_H;
			map[4][y] = GRD_WALL_V;
		map[4][4] = GRD_WALL_CTL;
		map[y][4] = GRD_WALL_VB;
		map[4][y] = GRD_WALL_HR;
		#print map
		c.execute("""INSERT INTO rts_map (name,status) VALUES ('"""+str(name)+"""',1)""")
		map_id = 1
		for y, ys in map.items():
			for x, v in ys.items():
				#print "NAME:"+str(name)+" x:"+str(x)+" y:"+str(y)+" v:"+str(v)
				c.execute("""INSERT INTO rts_mapdata (map_id,x,y,v) VALUES ('"""+str(map_id)+"""',"""+str(x)+""","""+str(y)+""","""+str(v)+""")""")
		return 0
	
	def new_game( self, name, map_id ):
		c = self.db.cursor()
		ground_id = map_id
		c.execute("""INSERT INTO rts_ground (map_id) VALUES ("""+str(map_id)+""")""")
		c.execute("""INSERT INTO rts_grounddata (ground_id, x, y, v) SELECT """+str(ground_id)+""", x, y, v FROM rts_mapdata WHERE map_id="""+str(map_id))
		c.execute("""INSERT INTO rts_game (name,ground_id,status) VALUES ('"""+str(name)+"""',"""+str(ground_id)+""",1)""")
		return 0
	
	def start_game( self, gid ):
		c = self.db.cursor()
		c.execute("""UPDATE rts_game SET status=1 WHERE id="""+gid)
		return 0
	
	def get_maps(self):
		if self.maps==[]:
			c = self.db.cursor()
			c.execute("""SELECT * FROM rts_map WHERE status=1""")
			for m in c:
				self.maps.append( m )
		return self.maps
	
	def get_games(self):
		c = self.db.cursor()
		c.execute("""SELECT * FROM rts_game WHERE status=1""")
		self.games = []
		for g in c:
			self.games.append( Game( g ) )
		return self.games

	def run(self):
		print "MAPS:"
		print srv.get_maps()
		self.games = Game.objects.all()
		print "RUNNING GAMES ("+str(len(self.games))+"):"
		self.grs = {}
		for g in self.games:
			gr = GameReactor(self,g)
			gr.rnd = -1
			# Launch the gamereactor here
			reactor.callLater(RTS_TICK, gr.run)
			self.grs[g.id] = gr
		# Create webserver for all gamereactor
                site = server.Site(Simple(self.grs,self))
		# Listen on 8081, a proxy will do the mapping
                reactor.listenTCP(8081, site)
		
		
		
		# Basic configuration
		#PORT=8080
		ROOT='example'
		
		#application = service.Application('slosh')
		#serviceCollection = service.IServiceCollection(application)
		
		# Keep really short sessions.
		server.Session.sessionTimeout=64000
		
		root = static.File(ROOT)
		#root.putChild('push', slosh.Topics())
		#for i in range( 1, 10 ):
		#	root.putChild('objs_%d' % i, slosh.Topics())
		for p in Player.objects.all():
			pid = p.id
			self.psloshes[pid] = slosh.Topics()
			self.psloshes[pid].pid = pid
			print 'add slosh: objs_%d' % pid
			root.putChild('objs_%d' % pid, self.psloshes[pid])
		
		site_push = server.Site(root)
		site_push.sessionCheckTime = 64000
		#internet.TCPServer(PORT, site).setServiceParent(serviceCollection)
		reactor.listenTCP(8080, site_push)





		# Go
		reactor.addSystemEventTrigger("before", "shutdown", self.cleanupFunction)
		reactor.run()
	
	def cleanupFunction(self):
		print "saving objs...",
		for k,gr in self.grs.items():
			gr.save_objs()
		print "ok"
		print "shutdown"



class Simple(resource.Resource):
	def __init__(self, grs, srv):
		self.grs = grs
		self.srv = srv
    
	isLeaf = True
	def render_GET(self, request):
		p = request.path.strip("/")
		#print p
		m = re.match( r"([0-9]+)/([0-9]+)/([a-z_]+)[?&a-z0-9=-]*", p )
		#print str(len(m.groups()))
		game_id = int(m.group(1))
		gamereactor = self.grs[game_id]
		player_id = int(m.group(2))
		player = Player.objects.get( id=player_id )
		cmd = str(m.group(3))
		args = request.args
		if cmd=='ask_push':
			#path = str(args['path'][0])
			#gamereactor.push( 'path', {} )
			return ""
		
		if cmd=='get_objs':
			objs = []
			for k in gamereactor.objs:
				objs.append( gamereactor.objs[ k ] );
			return serializers.serialize('json', Obj.objects.all(), use_natural_keys=True)
		
		if cmd=='get_obj':
			objid = int(args['objid'][0])
			if objid in gamereactor.objs:
				o = gamereactor.objs[objid]
				vs = o.serialize()
			else:
				vs = { 'status':'notfound' }
			return simplejson.dumps( vs )
		
		# Sell obj
		if cmd=='sell_obj':
			try:
				id = int(args['id'][0])
				o = gamereactor.objs[id]
				gs = gamereactor.game_status[player.id]
				gs.money_level += o.type.cost
				gs.energy_consumption -= o.type.energy_consumption;
				gs.energy_production -= o.type.energy_production;
				print "MONEY LEVEL UP:", gs.money_level, o.type.cost
				vs = {'status':'ok', 'event_type':'sellobj', 'obj':o.serialize()}
				gamereactor.push( 'objs', vs, exclude=o.player.id )
				del gamereactor.objs[id]
				o.unmarkGround()
				o.delete()
			except:
				vs = {'status':'error'}
			return simplejson.dumps( vs )
		
		# Add obj
		if cmd=='add_obj':
			type_id = int(args['type_id'][0])
			x = int(args['x'][0])
			y = int(args['y'][0])
			gs = gamereactor.game_status[player.id]
			type = ObjType.objects.get( id=type_id )
			error = False
			tilexy = type.surface.split("x")
			tilex = int(tilexy[0])
			tiley = int(tilexy[1])
			for kx in range( x, x+tilex ):
				for ky in range( y, y+tiley ):
					if gamereactor.ground[ky][kx][1]>0 or gamereactor.ground[ky][kx][0]>0:
						error = True
						break
			if not error:
				o = Obj( player=player, game=gamereactor.game, team=gs.team, x=x, y=y, type=type )
				gs.money_level -= type.cost
				o.life_level = type.life_capacity
				o.gamereactor = gamereactor
				gs.energy_consumption += type.energy_consumption
				gs.energy_production += type.energy_production
				o.save()
				o.markGround()
				gamereactor.objs[o.id] = o
				vs = {'status':'ok', 'event_type':'addobj', 'obj':o.serialize()}
				gamereactor.push( 'objs', vs, exclude=o.player.id )
			else:
				vs = {'status':'error'}
			return simplejson.dumps( vs )
		
		
		if cmd=='attack':
			objid = int(args['objid'][0])
			target_objid = int(args['target_objid'][0])
			o = gamereactor.objs[objid]
			target_o = gamereactor.objs[target_objid]
			if o and target_o:
				o.attack_target = target_o
				o.setMetaState( 'attack' )
				dist = o.distance( o.attack_target )
				if dist<=o.type.attack_distance:
					o.setState( 'attack' )
					rotate = o.get_rotate( [target_o.x,target_o.y] )
					path = [[rotate,0,1]]
				else:
					path = o.findAttackPosition( gamereactor )
					print "PATH TO ATTACK POS:",path
					if path:
						#t = [dest.x,dest.y]
						#path = find_path([int(o.x),int(o.y)], t, gamereactor.ground)
						path = o.anim_new_path( path, exclude=o.player.id )
						o.setState( 'move' )
				if path:
					vs = { 'status':'ok', 'objid':objid, 'path':path, 'state':o.state, 'meta_state':o.meta_state }
				else:
					vs = { 'status':'error', 'objid':0 }
			else:
				vs = { 'status':'error', 'objid':0 }
			return simplejson.dumps( vs )
		
		
		if cmd=='move':
			objid = int(args['objid'][0])
			o = gamereactor.objs[objid]
			t = [int(args['destx'][0]),int(args['desty'][0])]
			path = find_path([int(o.x),int(o.y)], [int(t[0]),int(t[1])], gamereactor.ground)
			if len(path)>0:
				path = o.anim_new_path( path, exclude=o.player.id )
				o.setMetaState( '' )
				o.setState( 'move' )
				#o.save()
				a = { 'objid':objid, 'tile':[o.x,o.y], 'path':path, 'state':o.state, 'meta_state':o.meta_state }
			else:
				a = { 'objid':objid, 'state':o.state, 'meta_state':o.meta_state }
			return simplejson.dumps( a )
		
		
		if cmd=='join':
			try:
				# Try to join
				gs = GameStatus.objects.get( game=gamereactor.game, player=player )
			except:
				# Create game status and first Obj
				team = Team.objects.get( type='nod', color='blue' )
				gs = GameStatus( game=gamereactor.game, player=player, team=team )
				# All start positions
				startpos = [[30,4],[70,35],[20,35],[70,5],[40,20]]
				players = Player.objects.filter( game=gamereactor.game )
				allgamestatus = GameStatus.objects.filter( game=gamereactor.game )
				i = len( allgamestatus )
				x = startpos[i][0]
				y = startpos[i][1]
				print "New position/x/y: ", i, x, y
				gs.viewx = x-2
				gs.viewy = y-2
				viewport_width = 20
				viewport_height = 8
				if gs.viewx>MAP_WIDTH-viewport_width:
					gs.viewx = MAP_WIDTH-viewport_width
				if gs.viewy>MAP_HEIGHT-viewport_height:
					gs.viewy = MAP_HEIGHT-viewport_height
				gs.save()
				basetype = ObjType.objects.get( objclass='base' )
				base = Obj( game=gamereactor.game, player=player, type=basetype, team=team, x=x, y=y )
				base.life_level = basetype.life_capacity;
				base.save()
				print "New base: ", base.id, base.x
				gamereactor.reload_obj()
				gamereactor.load_game_status()
			# Redirect to the game
			request.redirect( "/game/"+str(gamereactor.game.id) )
			return 'done'
		
		if cmd=='get_ground':
			gs = gamereactor.game_status[player.id]
			resp = { 'ground':gamereactor.ground, 'shadow':gamereactor.shadows[player.id] };
			resp['gs'] = { 'viewx':gs.viewx, "viewy":gs.viewy, "team_id":gs.team_id };
			return simplejson.dumps( resp, cls=ShadowEncoder )
			#return simplejson.dumps( gamereactor.shadows[player.id], cls=ShadowEncoder )
		
		if cmd=='get_anims':
			vss = []
			"""
			try:
				objid = int(args['objid'][0])
				o = gamereactor.objs[objid]
				anims = o.animationstep_set.all().order_by('id')
				vs = { 'objid':o.id }
				vs['path'] = []
				for s in anims:
					vs['path'].append( [s.x,s.y] )
				vss.append( vs )
			except:
			"""
			for k,o in gamereactor.objs.items():
				vs = { 'objid':o.id }
				anims = o.animationsteps #_set.all().order_by('id')
				vs['path'] = []
				for s in anims:
					vs['path'].append( [s.x,s.y] )
				vss.append( vs )
			return simplejson.dumps( vss )
		
		
		if cmd=='get_gamestatus':
			#g = load_game( gameid )
			game = gamereactor.game
			ground = gamereactor.ground
			#p = request.user.get_profile()
			gs = gamereactor.game_status[player.id]
			try:
				#gs = GameStatus.objects.get( game=g, player=p )
				gs.viewx = int(args['viewx'][0]) #request.GET.get('viewx', ''))
				gs.viewy = int(args['viewy'][0]) #request.GET.get('viewy', ''))
				gs.save()
			except:
				pass
			#gss = list(GameStatus.objects.filter( game=game, player=player ))
			json = {}
			#json['gs'] = serializers.serialize('json', gss)
			json['gs'] = gs.serialize()
			vss = []
			for k,o in gamereactor.objs.items():
				vss.append( o.serialize() )
			json['objs'] = vss
			return simplejson.dumps( json )



import mem
class GameReactor:
	def __init__(self, srv, game):
		self.game = game
		self.srv = srv
		adminplayer = Player.objects.get( id=1 )
		try:
			gs = GameStatus.objects.get( game=self.game, player=adminplayer )
		except:
			gs = GameStatus( game=self.game, player=adminplayer )
			gs.save()
		
		# Load ground
		self.ground = load_ground( self.game )
		
		# Load gamestatus and shadow
		self.load_game_status()
		
		self.verbose = 0
		self.round = 0
		self.objs = {}
		self.anims = {}
		self.animsteps = {}
		self.reload_obj()
		self.fps_frame = 0
		self.frame = 0
		self.lasttime = time.time()
		self.frame_chkpoint = round(0.5/0.04);
	
	
	def push(self, type, params, player_ids=None, exclude=None):
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		#headers = {"Content-type": "application/json", "Accept": "text/plain"}
		#params = urllib.urlencode( params )
		#params = simplejson.dumps( params )
		#params = urllib.quote_plus( params )
	
		if player_ids is None:
			player_ids = []
			for k, gs in self.game_status.items():
				player_ids.append( gs.player.id )
		for player_id in player_ids:
			if player_id<>exclude:
				#print "PLAYER ID", player_id
				if player_id not in self.srv.psloshes:
					print "UNABLE TO PUSH TO", player_id
					continue
				if str(player_id)+"-"+type in self.srv.psloshes[player_id].alltopics:
					sl = self.srv.psloshes[player_id].alltopics[str(player_id)+"-"+type]
					print 'send to slosh -- id:%s type:%s' % (sl.id,type)
					#print params
					sl.deliver_msg( params )
				"""
				uri = "/objs_%d/%s.json" % (player_id,type)
				#print "URI: ", uri, params, headers
				conn = httplib.HTTPConnection("192.168.0.10", 8080, timeout=1)
				if self.verbose>1:
					print "[INFO] push request httplib ready"
				conn.request("POST", uri, params, headers)
				if self.verbose>1:
					print "[INFO] push request done"
				r1 = conn.getresponse()
				if self.verbose>0:
					print "[INFO] status:%s reason:%s" % (r1.status, r1.reason)
				"""
		return True #r1.status==200
	
	def load_game_status(self):
		self.game_status = {}
		self.shadows = {}
		for gs in GameStatus.objects.filter( game=self.game ):
			self.game_status[gs.player.id] = gs
			self.shadows[gs.player.id] = load_shadow( gs, self.ground )
	
	def load_objs(self):
		#from rts.models import Obj
		objects = Obj.objects.filter( game=self.game )
		#if use_list:
		#	objs = list(objects)
		#else:
		objs = {}
		for k,gs in self.game_status.items():
			gs.energy_production = 0
			gs.energy_consumption = 0
		for o in objects:
			o.gamereactor = self
			self.game_status[o.player.id].energy_production += o.type.energy_production
			self.game_status[o.player.id].energy_consumption += o.type.energy_consumption
			objs[o.id] = o
			o.markGround()
			"""
			x = o.x
			y = o.y
			s = o.type.surface.split("x")
			w = int(s[0])
			h = int(s[1])
			for k in range( y, y+h ):
				for j in range( x, x+w ):
					self.ground[k][j][1] = o.id
					#ground[k][j][0] = 1
					#xy = k*MAP_WIDTH + j
					#print o.id, x, y, k, j, xy
			"""
		return objs
	
	
	def save_objs(self):
		if self.shadows:
			print "SAVE SHADOWS"
			for kss,sss in self.shadows.items():
				for ky,ss in sss.items():
					for kx,s in ss.items():
						s.save()
		if self.game_status:
			print "SAVE GAMESTATUS"
			for k,gs in self.game_status.items():
				gs.save()
		if self.objs:
			print "SAVE OBJS"
			for k,o in self.objs.items():
				o.save()
	
	def reload_obj(self):
		self.objs = self.load_objs()
	
	
	def run(self):
		reactor.callLater(RTS_TICK, self.run)
		
		self.round += 1
		self.refresh = False
		self.fps_frame += 1
		if self.round==CHECKPOINT:
			self.round = 0
			self.refresh = True
			#self.reload_obj()
		
			sec = time.time() - self.lasttime
			self.lasttime = time.time()
			fps = round( float(self.fps_frame)/float(sec), 3 )
			self.fps_frame = 0
			print "== CHECKPOINT:" + datetime.datetime.now().ctime(), 
			print "-- FRAMETIME:"+str(round(float(sec)/float(CHECKPOINT),4))+" ("+str(fps)+" FPS)",
			print "-- MEMORY:"+str(mem.rss())+"/"+str(mem.rsz())+" (virtual:"+str(mem.vsz())+")"
			if mem.vsz()>300000:
				print "MEMORY AUTO KILL"
				reactor.stop()
		
		# Loop through objs
		self.loopObjs()
		
		return 0
	
	def loopObjs(self):
		#print "---- OBJECTS:"+("|".join([str(o.type) for k,o in self.objs.items()]))
		self.frame += 1
		for k,o in self.objs.items():
			if self.frame%self.frame_chkpoint==0:
				self.frame = 0
				#if o.x==15 and o.y==13:
				#	print o.meta_state
				if o.meta_state=='dying':
					# Really kill this obj
					vs = {'status':'ok', 'event_type':'destroyobj', 'obj':o.serialize()}
					self.push( 'objs', vs )
					del self.objs[o.id]
					o.unmarkGround()
					o.delete()
					continue
				if o.state=='attack':
					o.attack()
				if o.meta_state=='':
					#if self.verbose>1: print "[INFO] meta_state==null"
					if 'harvest' in o.type.capabilities.split(","):
						#if self.verbose>1: print "[INFO] has harvest capabilities", o.y, o.x, self.ground[o.y][o.x][0]
						if self.ground[o.y][o.x][0]==GRD_SPICE:
							#if self.verbose>1: print "[INFO] set harvest meta_state"
							o.setMetaState( 'harvest' )
				if o.meta_state=='harvest':
					#if not self.ground[o.y][o.x][0]==GRD_SPICE:
					#	print "HARVEST[%d:%d]=%d" % (o.y, o.x, self.ground[o.y][o.x][0])
					if self.ground[o.y][o.x][0]==GRD_SPICE:
						# In harvest mode, on a spice field
						if o.spice_level<o.type.spice_capacity:
							if self.verbose>2: print "[INFO] Spice up"
							# Not fully loaded yet
							o.spice_level += 100
							#print "level:"+str(o.spice_level)
						else:
							if not o.hasAnim():
								# Full of spice, go back home:
								if self.verbose>1: print "[INFO] Search refinery"
								refinery = o.findNearest( 'obj:refinery', self.ground, self.objs )
								if refinery is not None:
									if self.verbose>1: print "[INFO] Refinery found"
									path = find_path([int(o.x),int(o.y)], [int(refinery[0]),int(refinery[1])], self.ground)
									o.anim_new_path( path )
									o.setMetaState( 'deliver' )
								else:
									if self.verbose>1: print "[INFO] Refinery _not_ found"
									# Spice not found
									o.meta_state = 'norefinery'
					else:
						if not o.hasAnim():
							# In harvest mode but not in a spice field and no animation
							if self.verbose>1: print "[INFO] Search spice"
							spice = o.findNearest( 'grd:spice', self.ground, self.objs )
							if spice is not None:
								if self.verbose>1: print "[INFO] Spice found: [X:"+str(spice[0])+" Y:"+str(spice[1])+"]"
								path = find_path([int(o.x),int(o.y)], [int(spice[0]),int(spice[1])], self.ground)
								o.anim_new_path( path )
							else:
								if self.verbose>1: print "[INFO] Spice _not_ found"
								# Spice not found
								#o.state = 'nospice'
				if o.meta_state=='guard':
					if o.type.name=='soldier':
						if self.ground[o.y][o.x][0]==GRD_SPICE:
							o.meta_state = 'harvest'
						if o.spice_level>100:	# Need to define threshold
							o.meta_state = 'harvest'
				if o.meta_state=='deliver':
					found = False
					for kt,ot in self.objs.items():
						if ot.team_id==o.team_id and 'collect' in ot.type.capabilities.split(","):
							if self.verbose>1: print "[INFO] Delivery target reached"
							#print "grd:"+str(self.ground[o.y-1][o.x-1])
							if self.ground[o.y-1][o.x-1][1]==ot.id or\
							self.ground[o.y-1][o.x][1]==ot.id or\
							self.ground[o.y-1][o.x+1][1]==ot.id or\
							self.ground[o.y][o.x-1][1]==ot.id or\
							self.ground[o.y][o.x+1][1]==ot.id or\
							self.ground[o.y+1][o.x-1][1]==ot.id or\
							self.ground[o.y+1][o.x][1]==ot.id or\
							self.ground[o.y+1][o.x+1][1]==ot.id:
								ot.spice_level += o.spice_level
								# Update player money for this game
								gs = self.game_status[ot.player.id]
								gs.money_level += int(float(o.spice_level)/100)
								#gs.save()
								# Save target object
								#ot.save()
								# Change subject object
								o.meta_state = 'harvest'
								o.spice_level = 0
								found = True
					if not found:
						# Check if there is still an animation going on for this obj:
						if not o.hasAnim():
							# Lost its way, research refinery:
							if self.verbose>1: print "[INFO] RE-Search refinery"
							refinery = o.findNearest( 'obj:refinery', self.ground, self.objs )
							if refinery is not None:
								if self.verbose>1: print "[INFO] Refinery found"
								path = find_path([int(o.x),int(o.y)], [int(refinery[0]),int(refinery[1])], self.ground)
								o.anim_new_path( path )
								o.meta_state = 'deliver'
							else:
								if self.verbose>1: print "[INFO] Refinery _not_ found"
								# Spice not found
								o.meta_state = 'norefinery'
			o.doAnims( self.ground, self.refresh )
	"""
	def loopAnims(self):
		animations = []
		for k,a in self.anims.items():
			steps = a.steps
			#try:
			#	steps = list(AnimationStep.objects.filter( animation=a ).order_by('id'))
			#except:
			#	steps = []
			if len(steps)==0:
				# Arrived, check if need to do some actions
				a.delete()
				continue
			step = steps[0]
			#print step
			aimx = step.x
			aimy = step.y
			
			curx = self.objs[a.obj_id].x
			cury = self.objs[a.obj_id].y
			curposx = self.objs[a.obj_id].posx
			curposy = self.objs[a.obj_id].posy
			#print "ANIMATION: OBJID:"+str(self.objs[a.obj_id].id)+" :"+str(aimx)+"/"+str(aimy)+" CURX:"+str(curx)+"/"+str(cury)+" POSCURX:"+str(curposx)+"/"+str(curposy)
			if aimy*TILE_SIZE<curposy:
				curposy -= 2
				#print "-- MOVE -- POSCURY:"+str(curposy)
				if aimy*24>=curposy:
					curposy = aimy*24
					step.delete()
				self.objs[a.obj_id].posy = curposy
			if aimy*24>curposy:
				curposy += 2
				#print "-- MOVE ++ POSCURY:"+str(curposy)
				if aimy*24<=curposy:
					curposy = aimy*24
					step.delete()
				self.objs[a.obj_id].posy = curposy
			if aimx*24<curposx:
				curposx -= 2;
				#print "-- MOVE -- POSCURX:"+str(curposx)
				if aimx*24>=curposx:
					curposx = aimx*24
					step.delete()
				self.objs[a.obj_id].posx = curposx
			if aimx*24>curposx:
				curposx += 2
				#print "-- MOVE ++ POSCURX:"+str(curposx)
				if aimx*24<=curposx:
					curposx = aimx*24
					step.delete()
				self.objs[a.obj_id].posx = curposx
			self.objs[a.obj_id].x = int(curposx/24)
			self.objs[a.obj_id].y = int(curposy/24)
			
			#self.objs[a.obj_id].save()
			
			desc = "OID: " +str(a.obj_id)+ " (" + str(len(steps)) + ") "
			#if len(steps)>0:
			#	desc = desc + " " + steps[0].x + ":" + steps[0].y + " -> " + steps[len(steps)-1].x + ":" + steps[len(steps)-1].y
			animations.append( desc )
		if self.refresh and len(animations)>0:
			print "---- ANIMATIONS:"+str("\n".join(animations))
	"""

if __name__=="__main__":
	setup_environ(settings)
	from django.db.models.loading import get_models
	loaded_models = get_models()
	from django.utils import html, translation, simplejson
	from rts.models import *
	
	print "start"
	# parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], "n:d:s:gph", ["help"])
	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	# process options
	srv = Server()
	for o, a in opts:
		if o in ("-n", "--new"):
			ass = a.split(":")
			print "New game (name:"+str(ass[0])+" mapid:"+str(ass[1])
			srv.new_game( ass[0], ass[1] )
			sys.exit(0)
		#if o in ("-d", "--display"):
		#    print "Display " + str(a)
		#    srv.display( a )
		#    sys.exit(0)
		if o in ("-s", "--start"):
			print "Start game " + str(a)
			srv.start_game( a )
			sys.exit(0)
		if o in ("-g", "--generate"):
			print "Generate map " + str(a)
			srv.gen_map( a )
			sys.exit(0)
		if o in ("-h", "--help"):
			print __doc__
			sys.exit(0)
		if o in ("-p", "--p"):
			load_game()
			ground = load_ground( game )
			"""
			grid = []
			for y,xs in ground.items():
				#l = []
				for x,v in xs.items():
					if v[0:4]=="wall":
						grid.append( 1 )
					else:
						grid.append( 0 )
			"""
			startpoint = [2,2]
			endpoint = [5,5]
			"""
			astar = AStar.AStar(AStar.SQ_MapHandler(grid,len(ground[0]),len(ground)))
			start = AStar.SQ_Location(startpoint[0],startpoint[1])
			end = AStar.SQ_Location(endpoint[0],endpoint[1])
			"""
			start = self.startpoint
			end = self.endpoint
			astar = AStarJS( ground )
			p = astar.findPath(start,end)
			#for n in p.nodes:
			#	print "x:%d y:%d" % (n.location.x, n.location.y)
			sys.exit(0)
	srv.run()

