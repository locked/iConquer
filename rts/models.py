import random, datetime
from math import sqrt
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from librts import *

TILE_SIZE = 24
HALF_TILE_SIZE = 12

INTEGER_MAX = 9999999

class Vector:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class PlayerManager(models.Manager):
	def get_by_natural_key(self, id):
		return self.get(id=id)

# All players, kind of a profile of User
class Player(models.Model):
	user = models.ForeignKey(User, unique=True)
	games = models.ManyToManyField('Game',blank=True,null=True,related_name='player_games')
	game = models.ForeignKey('Game',blank=True,null=True,related_name='player_game')
	name = models.CharField(max_length=255,blank=True,null=True)
	level = models.IntegerField(blank=True,null=True)
	status = models.IntegerField(blank=True,null=True)
	
	def natural_key(self):
		return { "id": self.id, "level": self.level, "name": self.name }
	
	def __unicode__(self):
		if self.name is not None:
			return self.name
		elif self.user and self.user.username:
			return "Player of %s" % self.user.username
		return "Player None"

def create_player(sender, instance=None, **kwargs):
    if instance is None:
        return
    player, created = Player.objects.get_or_create(user=instance)

post_save.connect(create_player, sender=User)


class GameStatus(models.Model):
	game = models.ForeignKey('Game')
	player = models.ForeignKey('Player')
	team = models.ForeignKey('Team')
	money_level = models.IntegerField(blank=True,null=True,default=0)
	point_level = models.IntegerField(blank=True,null=True,default=0)
	energy_production = models.IntegerField(blank=True,null=True,default=0)
	energy_consumption = models.IntegerField(blank=True,null=True,default=0)
	viewx = models.IntegerField(blank=True,null=True,default=0)
	viewy = models.IntegerField(blank=True,null=True,default=0)
	
	def serialize(self):
		vs = { 'objid':self.id, 'viewx':self.viewx, 'viewy':self.viewy, 'money_level':self.money_level, 'energy_production':self.energy_production, 'energy_consumption':self.energy_consumption }
		return vs
	
	def __unicode__(self):
		if self.game is not None and self.player is not None:
			if self.game.name is not None and self.player.name is not None:
				return "Game:%s Player:%s" % (self.game.name, self.player.name)
		return "Game None Player None"

# All games
class Game(models.Model):
	name = models.CharField(max_length=255,blank=True,null=True)
	ground = models.ForeignKey('Ground')
	status = models.IntegerField(blank=True,null=True)
	def __unicode__(self):
		return self.name
	"""
	def __init__(self, *args, **kwargs):
		super(Game, self).__init__(*args, **kwargs)
		#self.id = g[0]
		self.objs = []
		x = 10;
		y = 10;
		self.objs.append( obj( OBJ_SOLDIER, x, y ) )
		self.objs.append( obj( OBJ_JEEP, x+1, y ) )
		self.objs.append( obj( OBJ_PLANT, x+3, y-1 ) )
		self.objs.append( obj( OBJ_REFINERY, x+3, y-5 ) )
	"""
	def get_objs(self):
		return self.objs

class AnimationStep(models.Model):
	obj = models.ForeignKey('Obj')
	x = models.IntegerField()
	y = models.IntegerField()
	type = models.IntegerField(blank=True,null=True,default=0)	# move, rotate
	
	def __unicode__(self):
		return "[%d:%d]" % (self.x,self.y)

class ObjAction(models.Model):
	name = models.CharField(max_length=255,blank=True,null=True)
	js = models.CharField(max_length=255,blank=True,null=True)
	
	def __unicode__(self):
		return self.name

class TeamManager(models.Manager):
	def get_by_natural_key(self, id):
		return self.get(id=id)

class Team(models.Model):
	type_choices = (
         #(u'allies', 'allies'),
         (u'nod', 'nod'),
	)
	type = models.CharField(max_length=255, choices=type_choices, default='nod')
	color_choices = (
         (u'blue', 'blue'),
         (u'red', 'red'),
         (u'yellow', 'yellow'),
	)
	color = models.CharField(max_length=255, choices=color_choices, default='blue')
	
	def natural_key(self):
		return { "id": self.id, "type": self.type, "color": self.color }
	
	def __unicode__(self):
		return "%s:%s" % (self.type, self.color)

class ObjTypeManager(models.Manager):
	def get_by_natural_key(self, id):
		return self.get(id=id)

class ObjType(models.Model):
	name = models.CharField(max_length=255,blank=True,null=True)
	surface_choices = (
        (u'1x1', '1x1'),
        (u'1x2', '1x2'),
        (u'2x1', '2x1'),
        (u'2x2', '2x2'),
        (u'2x3', '2x3'),
        (u'3x2', '3x2'),
        (u'3x3', '3x3'),
        (u'4x4', '4x4'),
	)
	surface = models.CharField(max_length=4, choices=surface_choices, blank=True,null=True,default="1x1")
	objclass = models.CharField(max_length=255,blank=True,null=True)
	objtype_choices = (
        (u'batiment', 'Batiment'),
        (u'mobile', 'Mobile'),
	)
	objtype = models.CharField(max_length=30, choices=objtype_choices,blank=True,null=True)
	available_actions = models.ManyToManyField('ObjAction',blank=True,null=True)
	require = models.ManyToManyField('ObjType',blank=True,null=True,symmetrical=False,related_name='required_objtypes')
	cost = models.IntegerField(blank=True,null=True,default=0)
	spice_capacity = models.IntegerField(blank=True,null=True,default=0)
	life_capacity = models.IntegerField(blank=True,null=True,default=0)
	width = models.IntegerField(blank=True,null=True,default=24)
	height = models.IntegerField(blank=True,null=True,default=24)
	capabilities = models.CharField(max_length=255,blank=True,null=True,default='move')
	build_steps = models.IntegerField(blank=True,null=True,default=0)
	destruction_steps = models.IntegerField(blank=True,null=True,default=0)
	animation_steps = models.IntegerField(blank=True,null=True,default=0)
	energy_consumption = models.IntegerField(blank=True,null=True,default=0)
	energy_production = models.IntegerField(blank=True,null=True,default=0)
	attack_distance = models.IntegerField(blank=True,null=True,default=0)
	attack_damage = models.IntegerField(blank=True,null=True,default=0)
	attack_accuracy = models.IntegerField(blank=True,null=True,default=0)
	srctype = models.ForeignKey('ObjType',blank=True,null=True,related_name='src_objtype')
	
	def natural_key(self):
		actions = []
		for aa in self.available_actions.all():
			actions.append( aa.name )
		return { "id": self.id, "name": self.name, "surface": self.surface, 'objclass': self.objclass, 'objtype': self.objtype, 'actions':actions, 'width':self.width, 'height':self.height, 'capabilities':self.capabilities, 'spice_capacity':self.spice_capacity, 'life_capacity':self.life_capacity, 'energy_production':self.energy_production, 'build_steps':self.build_steps, 'destruction_steps':self.destruction_steps, 'animation_steps':self.animation_steps }
	
	def __unicode__(self):
		return "ObjType:%s" % (self.name)


class Obj(models.Model):
	game = models.ForeignKey('Game')
	player = models.ForeignKey('Player')
	team = models.ForeignKey('Team')
	type = models.ForeignKey('ObjType')
	x = models.IntegerField()
	y = models.IntegerField()
	posx = models.IntegerField(blank=True,null=True)
	posy = models.IntegerField(blank=True,null=True)
	orient = models.IntegerField(blank=True,null=True,default=0)
	turret_orient = models.IntegerField(blank=True,null=True,default=0)
	current_action = models.ForeignKey('ObjAction',blank=True,null=True)
	meta_state = models.CharField(max_length=255,blank=True,null=True,default="")
	state = models.CharField(max_length=255,blank=True,null=True,default="")
	spice_level = models.IntegerField(blank=True,null=True,default=0)
	life_level = models.IntegerField(blank=True,null=True,default=0)
	attack_target = models.ForeignKey('Obj',blank=True,null=True)
	animationsteps = []
	dying_time = None
	
	def __init__(self, *args, **kwargs):
		super(Obj, self).__init__(*args, **kwargs)
		if self.x is not None and self.y is not None:
			if self.posx is None: self.posx = self.x*TILE_SIZE+12
			if self.posx is not None and int(self.posx)==0: self.posx = self.x*TILE_SIZE+12
			if self.posy is None: self.posy = self.y*TILE_SIZE+12
			if self.posy is not None and int(self.posy)==0: self.posy = self.y*TILE_SIZE+12
			self.save()
	
	def setMetaState(self, meta_state):
		self.meta_state = meta_state
		if self.meta_state=='':
			self.setState( '' )
	def setState(self, state):
		self.state = state
	
	def hasAnim(self):
		if self.animationsteps==None:
			return False
		if len(self.animationsteps)==0:
			return False
		return True
	
	
	def markGround(self):
		s = self.type.surface.split("x")
		w = int(s[0])
		h = int(s[1])
		# Set this object ID on the ground
		for k in range( self.y, self.y+h ):
			for j in range( self.x, self.x+w ):
				if k>=0 and j>=0:
					self.gamereactor.ground[k][j][1] = self.id
		self.markShadow()
	
	def markShadow(self):
		s = self.type.surface.split("x")
		w = int(s[0])
		h = int(s[1])
		# Set shadow
		visi = 5
		for k in range( self.y-visi, self.y+h+visi ):
			for j in range( self.x-visi, self.x+w+visi ):
				if k>=0 and j>=0 and k<40 and j<40:
					if self.gamereactor.shadows[self.player.id][k][j].v==1:
						print "UNSET SHADOW: ", j, k, self.player.id
						self.gamereactor.shadows[self.player.id][k][j].v = 0
						self.gamereactor.push( 'shadow', {'x':j, 'y':k, 'v':0}, [self.player.id] )
			
		
	def unmarkGround(self):
		s = self.type.surface.split("x")
		w = int(s[0])
		h = int(s[1])
		for k in range( self.y, self.y+h ):
			for j in range( self.x, self.x+w ):
				self.gamereactor.ground[k][j][1] = 0
			
		
	def anim_clear( self ):
		#from rts.models import AnimationStep
		# Clear animation for an object
		for s in self.animationstep_set.all():
			s.delete()
		self.animationsteps = None
	
	def get_rotate( self, p1 ):
		if p1[0]<self.x:
			rotate = 270
			if p1[1]<self.y:
				rotate += 45
			elif p1[1]>self.y:
				rotate -= 45
		elif p1[0]>self.x:
			rotate = 90
			if p1[1]<self.y:
				rotate -= 45
			elif p1[1]>self.y:
				rotate += 45
		else:
			rotate = 0
			if p1[1]<self.y:
				rotate = 0
			elif p1[1]>self.y:
				rotate = 180
		return rotate
	
	def anim_new_path( self, path, exclude=None ):
		if len(path)==0:
			return path
		self.anim_clear()
		from rts.models import AnimationStep
		# For some object (heavy vehicules), we rotate before moving
		if 'rotate' in self.type.capabilities.split(","):
			p1 = path[0]
			rotate = self.get_rotate( p1 )
			path = [[rotate,0,1]] + path
			#print "ADD ROTATE TO PATH:", rotate, path
		
		# Push animation to clients
		#print "PUSH PATH:", path
		s = "["+str(",".join(["["+str(p[0])+","+str(p[1])+",'"+str(p[2])+"']" for p in path]))+"]"
		#print "-----------------------------------------"
		print "*** PUSH: %s ***" % s
		#print "-----------------------------------------"
		params = { 'objid': self.id, 'path': s }
		self.gamereactor.push('path', params, exclude=exclude)
		
		# Add animation steps
		self.animationsteps = []
		for p in path:
			s = AnimationStep(obj=self,x=p[0],y=p[1],type=p[2])
			s.save()
			self.animationsteps.append( s )
		return path
	
	
	
	def doAnims(self, ground, refresh=True):
		if self.type.objtype=='batiment':
			return;
		#animations = []
		#print "ANIMS:"+str(len(steps))
		steps = self.animationsteps
		if steps is not None and len(steps)>0:
			step = steps[0]
			if step.type==0:
				#continue
				#print "STEPID:"+str(step.id)
				aimx = step.x*TILE_SIZE + int(TILE_SIZE/float(2))
				aimy = step.y*TILE_SIZE + int(TILE_SIZE/float(2))
				
				curx = self.x
				cury = self.y
				curposx = self.posx
				curposy = self.posy
				#print "ANIMATION: OBJID:"+str(self.objs[a.obj_id].id)+" :"+str(aimx)+"/"+str(aimy)+" CURX:"+str(curx)+"/"+str(cury)+" POSCURX:"+str(curposx)+"/"+str(curposy)
				reached = False
				if aimy<curposy:
					curposy -= 2
					#print "-- MOVE -- POSCURY:"+str(curposy)
					if aimy>=curposy:
						curposy = aimy
						#reached = True
					self.posy = curposy
				if aimy>curposy:
					curposy += 2
					#print "-- MOVE ++ POSCURY:"+str(curposy)
					if aimy<=curposy:
						curposy = aimy
						#reached = True
					self.posy = curposy
				if aimx<curposx:
					curposx -= 2;
					#print "-- MOVE -- POSCURX:"+str(curposx)
					if aimx>=curposx:
						curposx = aimx
						#reached = True
					self.posx = curposx
				if aimx>curposx:
					curposx += 2
					#print "-- MOVE ++ POSCURX:"+str(curposx)
					if aimx<=curposx:
						curposx = aimx
						#reached = True
					self.posx = curposx
				if aimx==self.posx and aimy==self.posy:
					reached = True
				if reached==True:
					#print "REACHED: ", aimx, aimy, self.posx, self.posy
					step.delete()
					self.animationsteps.pop( 0 )
					if len(self.animationsteps)==0:
						#print "animation_steps:", len(self.animationsteps)
						if self.meta_state=='attack':
							self.setState( 'attack' )
						else:
							self.setState( '' )
				oldx = self.x
				oldy = self.y
				self.x = int(float(curposx-HALF_TILE_SIZE)/TILE_SIZE)
				self.y = int(float(curposy-HALF_TILE_SIZE)/TILE_SIZE)
				if (oldx!=self.x or oldy!=self.y) and self.x>=0 and self.y>=0:
					ground[oldy][oldx][1] = 0
					#print "REMOVE ON %d:%d ID %d AND SET ON GRD:%d:%d" % (oldx, oldy, self.id, self.x, self.y)
					#ground[self.y][self.x][1] = self.id
					self.markGround()
			if step.type==1:
				aim = step.x;
				#print "[ANIM] ROTATE, aim:", aim
				if aim<self.orient:
					self.rotate( -15 );
				if aim>self.orient:
					self.rotate( 15 );
				if aim==self.orient:
					step.delete()
					self.animationsteps.pop( 0 )
			#desc = "OID: " +str(self.id)+ " (" + str(len(steps)) + ") "
			#animations.append( desc )
		#if refresh and len(animations)>0: print "---- ANIMATIONS:"+str("\n".join(animations))
	
	
	def rotate(self, degree):
		self.orient += degree
		if self.orient<0: self.orient = (360+self.orient)
		if self.orient>=360: self.orient = (self.orient-360)
	
	
	def findNearest(self, target, ground=None, objs=None):
		from librts import ObjType, GRD_SPICE
		
		vs = target.split(":")
		ty = vs[0]
		ta = vs[1]
		if ty=='grd':
			if ta=='spice':
				#spices = []
				mindist = INTEGER_MAX
				minval = None
				for y,xs in ground.items():
					for x,v in xs.items():
						if v[0]==GRD_SPICE and v[1]==0:
							#spices.append( [x,y] )
							dist = self.distance( Vector( x, y ) )
							if dist<mindist:
								mindist = dist
								minval = [x,y]
							#print "SPICE DISTANCE/MINDIST: ", dist, mindist
				if minval:
					return minval
				return None
		elif ty=='obj':
			if ta=='refinery':
				for k,o in objs.items():
					if 'collect' in o.type.capabilities.split(",") and o.player_id==self.player_id:
						ty = o.y
						tx = o.x
						#print "ground:"
						#print  ground[ty][tx][1]
						while ground[ty][tx][1]>0:
							#print "STEP:"
							#print [self.x,self.y]
							#print [o.x,o.y]
							if o.x<self.x:
								tx += 1
							elif o.x>self.x:
								tx -= 1
							if o.y<self.y:
								ty += 1
							elif o.y>self.y:
								ty -= 1
						#print "GOTO:"
						#print [tx,ty]
						return [tx,ty]
		return None
	
	
	def distance(self, Goal):
		return sqrt(pow(self.x - Goal.x, 2) + pow(self.y - Goal.y, 2))
	
	
	def findAttackPosition( self, gamereactor ):
		o = self.attack_target
		ty = o.y
		tx = o.x
		while gamereactor.ground[ty][tx][1]>0:
			#print "findAttackPosition STEP:"
			#print [self.x,self.y]
			#print [o.x,o.y]
			if o.x<self.x:
				tx += 1
			elif o.x>self.x:
				tx -= 1
			if o.y<self.y:
				ty += 1
			elif o.y>self.y:
				ty -= 1
		dest = [tx,ty]
		from librts import find_path
		path = find_path([int(self.x),int(self.y)], dest, gamereactor.ground)
		newpath = []
		for p in path:
			dest = Vector( p[0],p[1] )
			dist = o.distance( dest )
			#print "DISTANCE:", p, dist, self.type.attack_distance
			newpath.append( p )
			if dist<=self.type.attack_distance*0.8:
				#print "  DIST OK, PATH:", newpath
				return newpath
		return None
	
	
	def attack(self):
		if self.attack_target:
			dist = self.distance( self.attack_target )
			#print "[ATTACK] DISTANCE: %0.3f" % dist,
			if dist<=self.type.attack_distance:
				# Ok in reach
				rand = random.randint( 0, 100 )
				#print "[ATTACK] RAND: %d" % rand
				if rand<self.type.attack_accuracy:
					shoot = self.type.attack_damage
					self.attack_target.life_level -= shoot
				#print "[ATTACK] LIFE: %d" % self.attack_target.life_level
				if self.attack_target.life_level<0:
					print "[ATTACK] DIED"
					self.attack_target.life_level = 0
					self.attack_target.dying_time = datetime.datetime.now()
					self.attack_target.setMetaState( 'dying' )
					self.attack_target = None
					self.setMetaState( '' )
			else:
				# Move to closer position
				target = self.getBestAttackSpot()
		else:
			self.setMetaState( '' )
	
	
	def getBestAttackSpot(self):
		return 0
	
	def serialize(self):
		vs = { 'objid':int(self.id) }
		vs['type_id'] = int(self.type.id)
		vs['team_id'] = int(self.team.id)
		vs['player_id'] = int(self.player.id)
		vs['id'] = int(self.id)
		vs['x'] = int(self.x)
		vs['y'] = int(self.y)
		vs['orient'] = int(self.orient)
		vs['turret_orient'] = int(self.turret_orient)
		vs['state'] = str(self.state)
		vs['meta_state'] = str(self.meta_state)
		if self.type.spice_capacity>0:
			vs['spice_level_percent'] = str(int(float(self.spice_level/float(self.type.spice_capacity))*100))
		vs['spice_level'] = str(int(self.spice_level))
		vs['life_level'] = int(self.life_level)
		if self.type.life_capacity>0:
			vs['life_level_percent'] = int(float(self.life_level/float(self.type.life_capacity))*100)
		else:
			vs['life_level_percent'] = 0
		return vs
	
	def __unicode__(self):
		return "Obj:"+str(self.type.name)



# All available map, used as a based to create a ground when beginning new game
class Map(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    status = models.IntegerField(blank=True,null=True)
    def __unicode__(self):
        return self.name

class MapData(models.Model):
    map = models.ForeignKey('Map')
    x = models.IntegerField(blank=True,null=True)
    y = models.IntegerField(blank=True,null=True)
    v = models.IntegerField(blank=True,null=True)
    def __unicode__(self):
        return "%s: %d, %d = %d" % (self.map.name, self.x, self.y, self.v)

# For each game, the state of the map
class Ground(models.Model):
    map = models.ForeignKey('Map')
    def __unicode__(self):
        return self.map.name

class GroundData(models.Model):
    ground = models.ForeignKey('Ground')
    x = models.IntegerField(blank=True,null=True)
    y = models.IntegerField(blank=True,null=True)
    v = models.IntegerField(blank=True,null=True)
    def __unicode__(self):
        return self.x

class Shadow(models.Model):
    gamestatus = models.ForeignKey('GameStatus')
    x = models.IntegerField(blank=True,null=True)
    y = models.IntegerField(blank=True,null=True)
    v = models.IntegerField(blank=True,null=True)
    redraw = False
    
    def __unicode__(self):
        if self.gamestatus and self.gamestatus.player and self.gamestatus.player.name:
            return self.gamestatus.player.name
        return "None Shadow"


import simplejson
class ShadowEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, Shadow):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            #return loads(serialize('json', obj))
            return { "v": o.v, "redraw": 0 }
        return JSONEncoder.default(self,o)
    

"""
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `level` int(10) NOT NULL DEFAULT '0',
  `status` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='All players';



DROP TABLE IF EXISTS `player_game`;
CREATE TABLE `player_game` (
  `player_id` int(10) unsigned NOT NULL,
  `game_id` int(10) unsigned NOT NULL,
  `status` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`player_id`,`game_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='players/games';



DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `status` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='All games';



DROP TABLE IF EXISTS `map`;
CREATE TABLE `map` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `x` int(10) unsigned NOT NULL,
  `y` int(10) unsigned NOT NULL,
  `v` int(10) unsigned NOT NULL,
  `status` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Map';


DROP TABLE IF EXISTS `ground`;
CREATE TABLE `ground` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `mapid` int(10) unsigned NOT NULL,
  `x` int(10) unsigned NOT NULL,
  `y` int(10) unsigned NOT NULL,
  `v` int(10) unsigned NOT NULL,
  `status` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Ground';

"""
