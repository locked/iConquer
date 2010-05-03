function Explosion( id, pos, nb ) {
	this.id = id;
	this.pos = pos;
	this.ind = 0;
	this.w = 41;
	this.h = 35;
	this.nb = nb;
	//debug( "EXPLOSION ADD" );
	this.dec = [];
	for( var i=0; i<this.nb; i++ ) {
		this.dec[i] = new Vector( Math.floor(Math.random()*tile_size), Math.floor(Math.random()*tile_size) );
	}
}

Explosion.prototype.doAnim = function() {
	this.ind += 0.3;
	//debug( "EXPLOSION DOANIM/SETGRD: x:"+this.pos.x+" y:"+this.pos.y );
	setGround( new Vector( this.pos.x, this.pos.y ), 2, 2 );
}
Explosion.prototype.render = function(ctx) {
	var pos = untranslatePos( this.pos );
	//debug( "EXPLOSION RENDER: "+this.ind+" x:"+pos.x+" y:"+pos.y );
	if( this.ind<22 ) {
		for( var i=0; i<this.nb; i++ ) {
			ctx.drawImage(explosionTile, Math.floor(this.ind)*this.w, 0, this.w, this.h, pos.x-half_tile_size+this.dec[i].x, pos.y-tile_size+this.dec[i].y, this.w, this.h);
		}
	} else
		delete explosions[this.id];
}


/*
 * Obj class
 */
function Obj( id, fields ) {
	this.id = id;
	for( var f in fields ) {
		this[f] = fields[f];
	}
	this.posx = this.x*tile_size+half_tile_size;
	this.posy = this.y*tile_size+half_tile_size;
	
	this.indx = 0;
	this.indy = 0;
	
	this.is_building = false;
	
	this.redraw = true;

	s = this.type.surface.split("x");
	this.tilex = Math.floor(s[0]);
	this.tiley = Math.floor(s[1]);
	this.audio = {};
	if( this.type.objtype=='mobile' ) {
		this.w = this.type.width;
		this.h = this.type.height;
		this.audio['select'] = [getAudioElement( "allies/allies #2 yes sir!.ogg" ), getAudioElement( "allies/allies #3 reporting.wav" )];
		this.audio['action'] = [getAudioElement( "allies/allies #1 affirmative.ogg" ), getAudioElement( "allies/allies #2 achnoledged.wav" )];
		this.audio['ready'] = [getAudioElement( "allies/allies #2 ready & waiting.wav" )];
		//$(this).bind("onmove", function(e) {
		//} );
	} else {
		this.w = this.tilex*tile_size;
		this.h = this.tiley*tile_size;
	}
	if( id>0 )
		this.setGround();
	this.tilesrc = '/static/graphics/'+this.team.type+'/'+this.team.color+'/'+this.type.objclass+'.png';
	//debug( tilesrc );
	this.tile = preload_image(this.tilesrc);
	this.plist = [];
	this.setOrient( this.orient );
	this.setTurretOrient( this.turret_orient );
	this.setState( this.state );
	this.setLifeLevel( this.life_level );
	this.loaded = true;
}


Obj.prototype.del = function( event_type ) {
	if( currentSelection==this.id )
		setSelection( null );
	if( event_type=="destroyobj" ) {
		pos = new Vector( objs[this.id].posx, objs[this.id].posy );
		explosions[this.id] = new Explosion( this.id, pos, this.tilex );
	}
	objs[this.id].unselect();
	delete objs[this.id];
}

Obj.prototype.add = function( json ) {
	this.fill( json, true );
	objs[this.id] = this;
	this.play( 'ready' );
}

Obj.prototype.fill = function( json, update_position ) {
	this.spice_level = json.spice_level;
	this.setLifeLevel( json.life_level );
	this.setMetaState( json.meta_state );
	this.setState( json.state );
	//this.setOrient( json.orient );
	//this.setTurretOrient( json.turret_orient );
	if( update_position ) {
		this.setPos( new Vector( json.x, json.y ), true );
	}
}


Obj.prototype.play = function( type ) {
	if( this.audio[type] ) {
		i = rand( 0, this.audio[type].length );
		this.audio[type][i].play();
	}
}

Obj.prototype.unselect = function() {
	setGround( new Vector( this.posx, this.posy ), Math.floor(this.w/tile_size), Math.floor(this.h/tile_size) );
	this.markRedraw();
}

Obj.prototype.askAttack = function( target_obj ) {
	$.getJSON( build_uri( "attack?objid="+this.id+"&target_objid="+target_obj.id ), function ( json ) {
		plist = json.path;
		objid = json.objid;
		if( objid>0 ) {
			o = objs[objid];
			o.setState( json.state );
			o.setMetaState( json.meta_state );
			if( plist.length>0 ) {
				debug( "askAttack() plist:"+plist.length );
				o.plist = plist;
				o.play( 'action' );
			}
		}
		setAction( null );
	} );
}

Obj.prototype.askPath = function( tilex, tiley ) {
	//, {'objid':this.id, 'destx':tilex, 'desty':tiley},
	$.getJSON( build_uri( "move?objid="+this.id+"&destx="+tilex+"&desty="+tiley ), function ( json ) {
		plist = json.path;
		objid = json.objid;
		if( objid>0 ) {
			o = objs[objid];
			o.setState( json.state );
			o.setMetaState( json.meta_state );
			if( plist.length>0 ) {
				o.plist = plist;
				o.play( 'action' );
			}
		}
		setAction( null );
	} );
}


Obj.prototype.setPos = function( tile, set_ground ) {
	this.x = tile.x;
	this.y = tile.y;
	this.posx = tile.x*tile_size+half_tile_size;
	this.posy = tile.y*tile_size+half_tile_size;
	// Set ground to redraw
	setGround( new Vector( this.posx, this.posy ), this.tilex, this.tiley );
	this.markRedraw();
	// Set ground ids
	if( set_ground )
		this.setGround();
}

Obj.prototype.setGround = function() {
	//debug( "init(): "+this.x+":"+this.y+" // "+this.tilex+":"+this.tiley );
	for( var j=this.y; j<this.y+this.tiley; j++ ) {
		for( var k=this.x; k<this.x+this.tilex; k++ ) {
			//debug( "set ground: "+this.x+":"+this.y );
			ground[j][k][1] = this.id;
			//this.checkVisibility( k, j );	// temporary for shadow
		}
	}
}


Obj.prototype.markRedrawShadow = function () {
	for( var j=this.y-1; j<this.y+this.tiley; j++ ) {
		for( var k=this.x; k<this.x+this.tilex; k++ ) {
			if( j>=0 && k>=0 )
				shadow[j][k].redraw = 1;
		}
	}
	return true;
}
Obj.prototype.markRedraw = function () {
	var decy = this.type.objtype=='batiment'?(this.tiley>1?1:0):0;
	for( var j=this.y; j<this.y+this.tiley-decy; j++ ) {
		for( var k=this.x; k<this.x+this.tilex; k++ ) {
			if( shadow[j][k].v==0 ) {
				this.redraw = true;
				ground[j][k][2] = 1;
			}
		}
	}
	return this.redraw;
}



/* temporary for shadow
Obj.prototype.checkVisibility = function( k, j ) {
	if( this.player.id==player_id ) {
		for( var y=j-6; y<=j+5; y++ ) {
			for( var x=k-6; x<=k+5; x++ ) {
				if( x>=0 && y>=0 && x<map_tiles_x && y<map_tiles_y ) {
					ground[y][x][3] = 0;
					var pos = getPosFromTile( new Vector( x, y ) );
					setGround( pos, 1, 1 );
				}
			}
		}
	}
}
*/

Obj.prototype.sell = function () {
	//debug( this.id );
	$.getJSON( build_uri( "sell_obj" ), {'id':this.id}, function ( json ) {
		if( json.status=='ok' ) {
			objid = json.obj.id;
			//alert( objid );
			delete objs[objid];
			setAction( null );
			setSelection( null );
			showAllActions();
		}
	} );
}


Obj.prototype.mouseover = function() {
	//if( this.type.objtype=='mobile' )
	//setSelection( this.id );
}

Obj.prototype.mouseselect = function() {
	this.mouseover();
	setSelection( this.id );
	
	if( this.type.objtype=='mobile' ) {
		//debug( "PLAY:"+i );
		if( this.player.id==player_id )
			this.play( 'select' );
	}
	
	var tmps = "<div class='sel sel_"+this.type.objclass+"'></div>";
	tmps+= "<p>" + this.type.name + "</p>";
	$("#sel").html( tmps );
	
	if( this.player.id==player_id )
		this.showActions();
	this.showProperties();
	
	return false;
};


Obj.prototype.showActions = function () {
	//alert( this.id );
	var action_str = "";
	if( this.type.objtype=='mobile' ) {
		for( var k in this.type.actions ) {
			a = this.type.actions[k];
			action_str+= "<a href=\"javascript:setAction('"+a+"');\"><div class=\"action action_"+a+"\"></div></a>";
		}
		$("#actions").html( action_str );
	} else {
		showAllActions( this );
	}
}


Obj.prototype.setLifeLevel = function (life_level) {
	if( this.life_level!=life_level || !this.loaded ) {
		this.life_level = life_level;
		if( currentSelection==this.id )
			this.markRedraw();
		if( this.type.objtype=='batiment' ) {
			var step = 0;
			if( this.type.build_steps>0 && this.type.life_capacity>0 ) {
				step = this.type.destruction_steps - Math.floor((this.life_level/this.type.life_capacity)*(this.type.destruction_steps+1));
				if( step>0 ) {
					this.indx = step-1;
					this.indy = 2;
				} else {
					this.indx = 0;
					this.indy = 0;
				}
				this.markRedraw();
			}
			//debug( "setLifeLevel: "+this.type.build_steps+" - "+this.type.life_capacity+" : "+this.life_level+" step:"+step );
		}
	}
}


Obj.prototype.showProperties = function () {
	$("#properties").html( '' );
	refreshProperties( this.id );
}

function refreshProperties(objid) {
	if( currentSelection==objid ) {
		$.getJSON( build_uri( 'get_obj?objid='+objid+"&"+rand(0,100) ), function gotData(o) {
			if( o.status=='ok' ) {
				objs[currentSelection].spice_level = o.spice_level;
				objs[currentSelection].setLifeLevel( o.life_level );
				objs[currentSelection].state = o.state;
				objs[currentSelection].meta_state = o.meta_state;
				s = "state:"+o.state+"<br>meta_state:"+o.meta_state+"<br>Spice: "+o.spice_level_percent+" %";
				$("#properties").html( s );
				setTimeout( "refreshProperties("+o.objid+")", 1000 );
			} else if( o.status=='notfound' ) {
				objs[currentSelection].del();
			}
		} );
	}
}


Obj.prototype.render = function(ctx) {
	if( this.posx && this.posy ) {
		//debug( "w: "+this.w+" h:"+this.h+" indx:"+this.indx+" indy:"+this.indy );
		if( !( this.redraw || real_redraw_all ) )
			return;
		
		
		this.markRedrawShadow();
		
		this.redraw = false;
		xy = get_coord(this.posx-12, this.posy-12);
		if( this.type.objtype=='batiment' ) {
			decy = this.tiley>1?24:0;
			marginx = 0;
			marginy = 0;
		} else {
			decy = 0;
			marginx = Math.floor( ( this.w - tile_size ) / 2 );
			marginy = Math.floor( ( this.h - tile_size ) / 2 );
		}
		
		
		
		//if( this.type.objclass=="harvester" && this.team.color=='red' )
		//	debug( this.type.objclass+" src:"+this.tile+" -- "+this.w+", "+(this.h+decy)+", "+xy[0]+", "+(xy[1]-decy)+", "+this.w+", "+(this.h+decy) );
		if( this.type.objclass=='yard' ) {
			// There is a 'under' tile to draw before
			ctx.drawImage(this.tile, 0, 0+this.indy*this.h, this.w, this.h, xy[0]-marginx, xy[1]-decy-marginy, this.w, this.h);
			ctx.drawImage(this.tile, 0+this.w, 0+this.indy*this.h, this.w, this.h, xy[0]-marginx, xy[1]-decy-marginy, this.w, this.h);
		} else {
			//if( new_object==this )
				//debug( "redraw new_object:"+this.indx+" indy:"+this.indy );
			ctx.drawImage(this.tile, Math.floor(this.indx)*this.w, this.indy*this.h, this.w, this.h, xy[0]-marginx, xy[1]-decy-marginy, this.w, this.h);
			if( this.type.capabilities.search( 'turret' )>-1 ) {
				turretindx = (Math.floor( (360-this.turret_orient)/(360/this.type.animation_steps) ) )%this.type.animation_steps;
				ctx.drawImage(this.tile, Math.floor(turretindx)*this.w, this.h, this.w, this.h, xy[0]-marginx, xy[1]-decy-marginy, this.w, this.h);
			}
		}
		
		if( this.id==currentSelection ) {
			var x = xy[0]-marginx+1;
			var y = xy[1]-decy-marginy+1;
			var d = 3;
			var l = 6;
			// Stroke a box
			ctx.beginPath();
			ctx.lineWidth = 1;
			ctx.lineCap = 'square';
			//ctx.strokeStyle = '#0f0';
			ctx.strokeStyle = 'rgba(255,255,255,1)';
			locy = xy[1]-marginy-decy;
			if( this.w==50 && this.h==39 ) {
				locx = xy[0];
				locw = this.tilex*tile_size;
				loch = this.tiley*tile_size;
			} else {
				locx = xy[0]-marginx+1;
				locw = this.w;
				loch = this.h;
			}
			ctx.moveTo(locx+d+0.5, locy+d+0.5);
			ctx.lineTo(locx+d+l+0.5, locy+d+0.5);
			ctx.moveTo(locx+locw-d-l+0.5, locy+d+0.5);
			ctx.lineTo(locx+locw-d+0.5, locy+d+0.5);
			ctx.lineTo(locx+locw-d+0.5, locy+d+l+1+0.5);
			ctx.moveTo(locx+locw-d+0.5, locy+loch-d-l+0.5);
			ctx.lineTo(locx+locw-d+0.5, locy+loch-d+0.5);
			ctx.lineTo(locx+locw-d-l+0.5, locy+loch-d+0.5);
			ctx.moveTo(locx+d+l+0.5, locy+loch-d+0.5);
			ctx.lineTo(locx+d+0.5, locy+loch-d+0.5);
			ctx.lineTo(locx+d+0.5, locy+loch-d-l+0.5);
			ctx.moveTo(locx+d+0.5, locy+d+l+1+0.5);
			ctx.lineTo(locx+d+0.5, locy+d+0.5);
			/*
			ctx.moveTo(x+d+0.5, y+d+0.5);
			ctx.lineTo(x+d+l+0.5, y+d+0.5);
			ctx.moveTo(x+this.w-d-l+0.5, y+d+0.5);
			ctx.lineTo(x+this.w-d+0.5, y+d+0.5);
			ctx.lineTo(x+this.w-d+0.5, y+d+l+1+0.5);
			ctx.moveTo(x+this.w-d+0.5, y+this.h-d-l+0.5);
			ctx.lineTo(x+this.w-d+0.5, y+this.h-d+0.5);
			ctx.lineTo(x+this.w-d-l+0.5, y+this.h-d+0.5);
			ctx.moveTo(x+d+l+0.5, y+this.h-d+0.5);
			ctx.lineTo(x+d+0.5, y+this.h-d+0.5);
			ctx.lineTo(x+d+0.5, y+this.h-d-l+0.5);
			ctx.moveTo(x+d+0.5, y+d+l+1+0.5);
			ctx.lineTo(x+d+0.5, y+d+0.5);
			*/
			ctx.stroke();
			
			// Stroke life level
			ctx.beginPath();
			var w = locw-d*2-2;
			var ll = this.type.life_capacity>0?Math.floor((this.life_level/this.type.life_capacity)*w):0;
			ctx.strokeRect( locx+d+1+0.5, locy-1+0.5, w, 3 );
			ctx.moveTo(locx+d+2+0.5, locy+0.5);
			ctx.strokeStyle = 'rgba(0,255,0,1)';
			ctx.lineTo(locx+d+ll+0.5, locy+0.5);
			ctx.stroke();
			
			if( this.player.id==player_id ) {
				// Stroke spice/ammo level
				if( this.type.capabilities.search( 'harvest' )>-1 ) {
					var n = 7;
					var dy = 5;
					var sl = (this.spice_level/this.type.spice_capacity)*7;
					ctx.beginPath();
					for( var i=0; i<7; i++ ) {
						//ctx.strokeStyle = 'rgba(255,255,255,1)';
						//ctx.strokeRect( x+d+2+i*3, y+this.h-dy-1, 3, 3 );
						if( i<sl ) {
							ctx.moveTo( locx+d+3+i*3+0.5, locy+loch-dy+0.5 );
							ctx.lineTo( locx+d+4+i*3+0.5, locy+loch-dy+0.5 );
						}
					}
					ctx.stroke();
				}
			}
		}
		//ctxmap.fillRect(this.x, this.y, 1, 1);
	}
}


Obj.prototype.setMetaState = function( meta_state ) {
	this.meta_state = meta_state;
}
Obj.prototype.setState = function( state ) {
	this.state = state;
	if( this.state=='' ) {
		if( this.type.capabilities.search( 'walk' )>-1 ) {
			this.indx = this.orient_ind;
			this.indy = 0;
		}
	}
	if( this.state=='attack' ) {
		this.updateOrient();
	}
}

Obj.prototype.updateOrient = function() {
	this.orient_ind = (Math.floor( (360-this.orient)/(360/this.type.animation_steps) ) )%this.type.animation_steps;
	if( this.type.capabilities.search( 'walk' )>-1 ) {
		if( this.state=='attack' )
			this.indy = this.orient_ind+9;
		else
			this.indy = this.orient_ind+1;
	} else {
		this.indx = this.orient_ind;
	}
}

Obj.prototype.rotate = function( degree ) {
	if( this.type.objtype=='mobile' && this.type.animation_steps>0 ) {
		this.orient += degree;
		if( this.orient<0 ) this.orient = (360+this.orient);
		if( this.orient>=360 ) this.orient = (this.orient-360);
		this.updateOrient();
		//debug( "rotate() orient:"+this.orient+" ASTEPS:"+this.type.animation_steps+" INDX: "+this.orient_ind );
	}
}

Obj.prototype.setTurretOrient = function( orient ) {
	if( orient==null )
		this.turret_orient = 0;
	else
		this.turret_orient = orient;
}
Obj.prototype.setOrient = function( orient ) {
	if( this.type.objtype=='mobile' && this.type.animation_steps>0 ) {
		if( orient==null )
			this.orient = 0;
		else
			this.orient = orient;
		this.updateOrient();
		//debug( "setOrient() orient:"+this.orient+" ASTEPS:"+this.type.animation_steps+" INDX: "+this.orient_ind );
	}
}


Obj.prototype.doAnim = function() {
	if( this.id==currentSelection )
		this.markRedraw();
	
	if( this.is_building ) {
		this.indx+=0.5;
		this.indy = 1;
		//debug( "build steps: " + this.indx + "/" + this.type.build_steps );
		if( this.indx>this.type.build_steps ) {
			this.is_building = false;
			this.indy = 0;
			this.indx = 0;
		}
		this.markRedraw();
	} else {
		if( this.plist.length>0 ) {
			//var animations = [];
			pl = this.plist[0];
			if( pl[2]==0 ) {
				aimx = pl[0]*tile_size + parseInt(tile_size/2);
				aimy = pl[1]*tile_size + parseInt(tile_size/2);
				if( this.plist.length>1 ) {
					apl = this.plist[1];
					aaimx = apl[0]*tile_size + half_tile_size;
					aaimy = apl[1]*tile_size + half_tile_size;
				} else {
					aaimx = aimx;
					aaimy = aimy;
				}
				curx = this.x;
				cury = this.y;
				curposx = this.posx;
				curposy = this.posy;
				reached = false;
				//if( this.id==40 )
				//	debug( "x:"+aimx+"<"+curposx+" y:"+aimy+"<"+curposy );
				if( aaimy<curposy ) {
					this.setOrient( 0 );
					if( aaimx<curposx ) this.rotate( -45 );
					else if( aaimx>curposx ) this.rotate( 45 );
				} else if( aaimy>curposy ) {
					this.setOrient( 180 );
					if( aaimx<curposx ) this.rotate( 45 );
					else if( aaimx>curposx ) this.rotate( -45 );
				} else if( aaimx<curposx ) {
					this.setOrient( 270 );
					if( aaimy<curposy ) this.rotate( -45 );
					else if( aaimy>curposy ) this.rotate( 45 );
				} else if( aaimx>curposx ) {
					this.setOrient( 90 );
					if( aaimy<curposy ) this.rotate( 45 );
					else if( aaimy>curposy ) this.rotate( -45 );
				}
				if( aimy<curposy ) {
					curposy -= 2;
					if( aimy>=curposy ) {
						curposy = aimy;
						//reached = true;
					}
					this.posy = curposy;
				}
				if( aimy>curposy ) {
					curposy += 2;
					if( aimy<=curposy ) {
						curposy = aimy;
						//reached = true;
					}
					this.posy = curposy;
				}
				if( aimx<curposx ) {
					curposx -= 2;
					if( aimx>=curposx ) {
						curposx = aimx;
						//reached = true;
					}
					this.posx = curposx;
				}
				if( aimx>curposx ) {
					curposx += 2;
					if( aimx<=curposx ) {
						curposx = aimx;
						//reached = true;
					}
					this.posx = curposx;
				}
				if( aimx==curposx && aimy==curposy )
					reached = true;
				if( reached ) {
					//debug( "REACHED AIMX:"+aimx+" AIMY:"+aimy+" CPX:"+curposx+" CPY:"+curposy+" this.orient_ind:"+this.orient_ind );
					//debug( "plist:"+this.plist.length );
					this.plist.shift();
					if( this.plist.length==0 ) {
						// Really reached
						if( this.meta_state=='attack' )
							this.setState( 'attack' );
						else
							this.setState( '' );
					}
				}
				if( ground[this.y] && ground[this.y][this.x] && ground[this.y][this.x][1]==this.id )
					ground[this.y][this.x][1] = 0;
				this.x = parseInt((curposx-half_tile_size)/tile_size);//-half_tile_size;
				this.y = parseInt((curposy-half_tile_size)/tile_size);//-half_tile_size;
				if( ground[this.y] && ground[this.y][this.x] && ground[this.y][this.x][1]==0 ) {
					ground[this.y][this.x][1] = this.id;
				}
				////this.checkVisibility( this.x, this.y ); // temporary for shadow
				pos = new Vector( this.posx, this.posy );
				if( !redraw_all ) {
					setGround( pos, 1, 1 );
					//this.markRedraw();
				}
				/*
				var desc = "OBJ_ANIM OID: " + this.id + " (" + this.plist.length + ") ";
				if( this.plist.length>0 )
					desc += " " + this.plist[0][0] + ":" + this.plist[0][1] + " -> " + this.plist[this.plist.length-1][0] + ":" + this.plist[this.plist.length-1][1];
				animations.push( desc );
				$("#animations").html( animations.join("<br>") );
				*/
			} else if( pl[2]==1 ) {
				var aim = pl[0];
				if( this.type.capabilities.search( 'rotate' )>-1 ) {
					//debug( "AIM:"+aim+" this.orient:"+this.orient+" this.orient_ind:"+this.orient_ind );
					if( aim<this.orient ) {
						this.rotate( -15 );
					} else if( aim>this.orient ) {
						this.rotate( 15 );
					} else if( aim==this.orient ) {
						this.plist.shift();
					}
					//this.indy = 0;
					//this.indx = this.orient_ind;
				} else {
					// Direct settings for light units
					this.setOrient( aim );
					this.plist.shift();
				}
				pos = new Vector( this.posx, this.posy );
				setGround( pos, 1, 1 );
				//this.markRedraw();
			}
		}
		if( this.state=='move' || this.state=='attack' ) {
			if( this.type.capabilities.search( 'walk' )>-1 ) {
				if( this.indy>0 ) {
					this.indx+= 0.5;
					if( Math.floor(this.indx)>5 )
						this.indx = 0;
					pos = new Vector( this.posx, this.posy );
					setGround( pos, 1, 1 );
					//this.markRedraw();
				}
			}
		}
	}
}




/*
Obj.prototype.updateObject = function() {
	id = this.id
	var e = $('#obj_'+id);
	e.get(0).style['top'] = objs[id].posy+'px';
	e.get(0).style['left'] = objs[id].posx+'px';
	if( objs[id].orient!="" ) {
		//e.removeClass( 'jeep' );
		e.addClass( 'jeep-'+objs[id].orient );
	} else {
		//e.addClass( 'jeep' );
		e.removeClass( 'jeep-l90' );
	}
	var em = $('#map_obj_'+id);
	em.get(0).style['top'] = objs[id].y+'px';
        em.get(0).style['left'] = objs[id].x+'px';
	//alert( e.style['left'] );
}
*/

