var redraw_all = true;
var real_redraw_all = true;
var toredraw = {};
var currentSelection;
var currentAction;
var ground;
var shadow;
var new_object = null;
var players;
var objtypes;
var teams;
var team_id;
var layer_left;
var layer_top;
var cursor;
var isDragMouseDown = false;
var layerScrollX = null;
var layerScrollY = null;
// global position records
var lastMouseX;
var lastMouseY;
var lastElemTop;
var lastElemLeft;
var energy_production = 0;
var energy_consumption = 0;
var energy_max = 20000;

var money_max = 30000;

function Vector( x, y ) {
	this.x = x;
	this.y = y;
}

// returns the mouse (cursor) current position
var getMousePosition = function(e){
	if (e.pageX || e.pageY) {
		var posx = e.pageX;
		var posy = e.pageY;
	}
	else if (e.clientX || e.clientY) {
		var posx = e.clientX
		var posy = e.clientY
	}
	return { 'x': posx, 'y': posy };
};

$(document).ready(function () {
	// use yellow overlay 
	//$.blockUI.defaults.overlayCSS.backgroundColor = '#000'; 
	// make overlay more transparent 
	//$.blockUI.defaults.overlayCSS.opacity = .2;
	//$.blockUI.defaults.applyPlatformOpacityRules = false;

	$.blockUI({ message: '<h1><img src="/static/busy.gif" /> Loading...</h1>' });
	
	// Init 4 panes layout
	$('body').layout({
		applyDefaultStyles: true,
		closable: false,
		resizable: false,
		west__closable: true,
		south__size: 220,
		north__size: 42,
		north__spacing_open: 2,
		south__spacing_open: 2,
		center__onresize: function() {
			layer_width = parseInt( $(".ui-layout-center").get(0).style["width"] );
			layer_height = parseInt( $(".ui-layout-center").get(0).style["height"] );
			$('#layer0').get(0).height = layer_height+tile_size;
			redraw_all = true;
		}
	});
	
	// Disable right menu
	$(document).bind("contextmenu",function(e){
              return false;
	});
	
	// Bind keys
	$(document).keyup( function(event) {
		if( event.keyCode==27 ) {
			reset();
		}
	} );
	
	init();
});


/**
 * PUSH stuff
 */
function getAll() {
	//getNewMessages();
	watchPathEvents();
	watchObjEvents();
	watchShadowEvents();
}


function watchPathEvents() {
	var uri = '/push/objs_'+player_id+'/path.json';
	debug( "START PUSH: "+uri );
	$.ajax( {
		url: uri,
		data: [],
		dataType: "json",
		success: function( json ){
		//$.getJSON('/push/push/path.json', function gotData(json) {
			//debug( "RCV PUSH" );
			watchPathEvents();
			path = eval("("+json.res[0].path+")");
			objid = json.res[0].objid;
			//$(".ui-layout-south").append( "[BEF] alen:"+anims.length );
			//anim_clear( objid );
			//$(".ui-layout-south").append( "[AFT] alen:"+anims.length );
			//anims.push( { 'obj':objid, 'plist':path, 'curp':0 } );
			objs[objid].plist = path;
		},
		error: function( json ){
			//debug( "PUSH FAILED" );
		}
	} );
}

function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"\"");
}
function ltrim(stringToTrim) {
	return stringToTrim.replace(/^\s+/,"\"");
}
function rtrim(stringToTrim) {
	return stringToTrim.replace(/\s+$/,"\"");
}

function watchShadowEvents() {
	var uri = '/push/objs_'+player_id+'/shadow.json';
	//debug( "START SHADOW PUSH" );
	$.ajax( { url: uri, data: [], dataType: "json", success: function( jsonraw ){
		watchShadowEvents();
		//debug( "SHADOW EVENT "+jsonraw );
		for( var i in jsonraw["res"] ) {
			var json = jsonraw["res"][i];
			var x = json.x;
			var y = json.y;
			var v = json.v;
			//debug( "SHADOW EVENT "+x+" "+y );
			shadow[y][x].v = v;
			var pos = getPosFromTile( new Vector( x, y ) );
			setGround( pos, 1, 1 );
		}
	} } );
}

function watchObjEvents() {
	var uri = '/push/objs_'+player_id+'/objs.json';
	$.ajax( { url: uri, data: [], dataType: "json", success: function( jsonraw ){
		watchObjEvents();
		var json = jsonraw.res[0];
		debug( "OBJ EVENT"+json.event_type );
		if( json.event_type=='addobj' ) {
			/*
			objstr = json.obj[0];
			objstr = objstr.replace(/'/g,"\"");
			debug( objstr );
			obj = jQuery.parseJSON( objstr ); //<-- only in 1.4.1
			*/
			obj = json.obj;
			objid = obj.id;
			debug( "ADD OBJ: "+objid );
			var no = createObj( obj.type_id, objid, obj.team_id, obj.player_id );
			no.add( obj );
			// Add obj
		} else if( json.event_type=='sellobj' || json.event_type=='destroyobj' ) {
			obj = json.obj;
			//objstr = objstr.replace(/'/g,"\"");
			//debug( objstr );
			//obj = jQuery.parseJSON( objstr ); //<-- only in 1.4.1
			debug( "DELETE OBJ: "+obj.id );
			// Delete obj
			if( obj.id ) {
				objs[obj.id].del( json.event_type );
			}
		}
		},
		error: function( xhr, ajaxOptions, thrownError ){
			debug( "OBJS PUSH FAILED"+xhr.status );
			debug( thrownError );
	} } );
}

function getNewMessages() {
	$.getJSON('/push/push/msg.json', function gotData(json) {
		//alert( json );
		$(".ui-layout-south").append( json.max );
		for( var m in json.res ) {
			$(".ui-layout-south").append( m.x );
		}
		getNewMessages();
	} );
}



function reset() {
	setSelection( null );
	setAction( null );
	new_object = null;
	redraw_all = true;
}

/**
 * Init:
 *  - Status bars
 *  - Ground
 *  - Objects
 */
function init() {
	loadGround();
	
	var energy_w = (energy/5000)*140;
	$(".energy_bar_inner").attr("style","width:"+energy_w+"px");
	$(".energy_bar_label").html(energy);
	var money_w = (money/5000)*140;
	$(".money_bar_inner").attr("style","width:"+money_w+"px");
	$(".money_bar_label").html(money+" $");
	
	layer_left = parseInt( $(".ui-layout-center").get(0).style["left"] );
	layer_top = parseInt( $(".ui-layout-center").get(0).style["top"] );
	layer_width = parseInt( $(".ui-layout-center").get(0).style["width"] );
	layer_height = parseInt( $(".ui-layout-center").get(0).style["height"] );
	//alert( layer_left );
	
	$('#layer0').get(0).width = layer_width+tile_size;
	$('#layer0').get(0).height = layer_height+tile_size;
	$('#cmap').get(0).width = map_tiles_x;
	$('#cmap').get(0).height = map_tiles_y;
	$('#cmap').attr('style',"margin: "+parseInt(((100-(map_tiles_y/2))/2) - 2)+"px 0px 0px "+parseInt(((120-(map_tiles_x/2))/2) - 2)+"px");
	//alert(parseInt(((160-(map_tiles_x/2))/2) - 2));
	
	// when the mouse is moved while the mouse button is pressed
	$('#layer0').mousemove(function(e) {
		var pos = getMousePosition(e);
		realLastMouseX = pos.x;
		realLastMouseY = pos.y;
		
		if(isDragMouseDown) {
			// Drag the map
			setViewPort( new Vector( layerScrollXBase - (pos.x - lastMouseX), layerScrollYBase - (pos.y - lastMouseY) ) );
			return false;
		} else {
			if( currentAction=="addobj" ) {
				if( new_object!=null ) {
					//new_object.unselect();
					new_object.setPos( getMouseTile( pos ), false );
					//redraw_all = true;
				}
			} else {
				// Try to get a selection on object
				o = getHoverObj( pos );
				cursor.setType( -1 );
				cursor.update( pos );
				if( o!=null ) {
					o.mouseover();
					cursor.setType( 0 );
					if( o.team.id==team_id ) {
						// Current team of player
						if( currentAction=="repair" )
							cursor.setType( 4 );
						else if( currentAction=="sell" )
							cursor.setType( 5 );
					} else {
						// Not current team
						if( currentSelection!=null && objs[currentSelection] && objs[currentSelection].team.id==team_id )
							cursor.setType( 2 );
					}
				} else {
					if( currentSelection!=null && objs[currentSelection] && objs[currentSelection].type.objtype=='mobile' && objs[currentSelection].team.id==team_id ) {
						cursor.setType( 1 );
					}
				}
			}
		}
	});
	
 	$('#layer0').mouseout( function(e){
 		isDragMouseDown = false;
		cursor.setType( -1 );
 	} );
 	
	$('#cmap').mousedown( function(e){
		var el = $(e.target).get(0);
		var pos = getMousePosition(e);
		p = new Vector( (pos.x-el.offsetLeft) * tile_size - layer_width/2, (pos.y-el.offsetTop-48) * tile_size - layer_height/2 );
		setViewPort( p );
	} );
	
	$('#layer0').mousedown( function(e){
		if( e.which==3 ) {
			reset();
			return false;
		}
		//var el = $(e.target).get(0);
		// retrieve positioning properties
		var pos = getMousePosition(e);
		lastMouseX = pos.x;
		lastMouseY = pos.y;
		o = getHoverObj( pos );
		if( currentSelection!=null && objs[currentSelection] && objs[currentSelection].type.objtype=='mobile' ) {
			if( o==null ) {
				if( objs[currentSelection].team.id==team_id ) {
					setAction( "move" );
				}
			} else {
				if( objs[currentSelection].team.id==team_id && o.team.id!=team_id ) {
					setAction( "attack" );
				} else if( objs[currentSelection].team.id==team_id && o.team.id==team_id ) {
					setAction( null );
				}
			}
		}
		if( currentAction=="move" ) {
			// Get the position of target and ask a path
			tile = getMouseTile( pos );
			o = objs[currentSelection];
			if( o )
				o.askPath( tile.x, tile.y );
			//setAction( null );
		} else if( currentAction=="attack" ) {
			if( currentSelection!=null && objs[currentSelection] )
				objs[currentSelection].askAttack( o );
		} else if( currentAction=="addobj" ) {
			if( new_object!=null ) {
				tile = getMouseTile( pos );
				addObj( tile );
			}
		} else if( currentAction=="sell" ) {
			if( o!=null && o.team.id==team_id )
				o.sell();
		} else {
			layerScrollXBase = layerScrollX;
			layerScrollYBase = layerScrollY;
			
			if( o!=null ) {
				o.mouseselect();
			} else {
				// Enable drag
				isDragMouseDown = true;
			
				// Clear selection
				setSelection( null );
			}
		}
	} );
	
	// when the mouse button is released
	$('#layer0').mouseup(function(e) {
		isDragMouseDown = false;
	});
	
	cursor = new Cursor();
	
	loopStatus();
	
	
	//setTimeout( askFirstPush, 250 );
}



function setViewPort( p ) {
	layerScrollX = p.x;
	layerScrollY = p.y;
	if( layerScrollX<0 ) layerScrollX = 0;
	if( layerScrollY<0 ) layerScrollY = 0;
	if( layerScrollX>map_width-layer_width-tile_size ) layerScrollX = map_width-layer_width-tile_size;
	if( layerScrollY>map_height-layer_height-tile_size ) layerScrollY = map_height-layer_height-tile_size;
	drawMap();
	redraw_all = true;
}



/*
 * Called when all images loaded
 */
function realStartGame() {
	$.unblockUI();

	//$("body").get(0).style.cursor = "url('/static/cursor.cur')";
	//$("body").get(0).style.cursor = 'crosshair'; //"url('/static/cursor.cur')";
	
	//$(document).ajaxStop(getAll);
	setTimeout( getAll, 500 );
	
	setSelection( null );
	setAction( null );
	drawMap();
	showAllActions( null );
	
	// Start anims loop
	setInterval( loopObjects, 40 );
	setInterval( loopStatus, 5000 );
}


function loopStatus() {
	var uri = build_uri("get_gamestatus" ); //"/game/get_gamestatus/"+game;
	if( layerScrollX!=null ) {
		var view = new Vector( parseInt(layerScrollX/tile_size), parseInt(layerScrollY/tile_size) );
		uri += "?viewx="+view.x+"&viewy="+view.y;
	}
	$.getJSON( uri, function ( json ) {
		//var fields = json[0].fields;
		var fields = json.gs;
		energy_production = Math.floor(fields.energy_production);
		energy_consumption = Math.floor(fields.energy_consumption);
		var energy_w = Math.floor( (energy_consumption/energy_production)*140 );
		$(".energy_bar_inner").attr("style","width:"+energy_w+"px");
		$(".energy_bar_label").html(energy_consumption+" / "+energy_production);
		var money = parseInt(fields.money_level);
		var money_w = (money/money_max)*140;
		$(".money_bar_inner").attr("style","width:"+money_w+"px");
		$(".money_bar_label").html(money+" $");
		for( var k in json.objs ) {
			id = json.objs[k].id;
			//debug( id );
			if( objs[id] ) {
				objs[id].fill( json.objs[k], false );
			}
		}
		//$(".ui-layout-south").html( json[0].fields.money_level );
	} );
}


function loadAnims() {
	$.getJSON( build_uri("get_anims"), function ( json ) {
		for( var k in json ) {
			a = json[k];
			plist = a.path;
			objid = a.objid;
			if( objid>0 && plist.length>0 )
				objs[objid].plist = plist;
		}
		loadImages();
	} );
}


/**
 * Load ground
 */
function loadGround() {
	var uri = build_uri( 'get_ground' );
	$.getJSON( uri, function (r) {
		ground = r.ground;
		shadow = r.shadow;
		/*
		for( var y=0; y<30; y++ ) {
			for( var x=0; x<30; x++ ) {
				debug( "shadow x:"+x+" y:"+y+" v:"+shadow[y][x].v+" redraw:"+shadow[y][x].redraw );
			}
		}
		*/
		var view = new Vector( parseInt(r.gs.viewx) * tile_size, parseInt(r.gs.viewy) * tile_size );
		setViewPort( view );
		
		team_id = r.gs.team_id;
		
		// Load objects and anims by RPC
		// in loadObjects: loadAnims();
		loadAudio();
		loadTiles();
	} );
}




function drawMap() {
	var ctxmap = document.getElementById('cmap').getContext('2d');
	ctxmap.save();
	ctxmap.clearRect(0,0,map_width,map_height);
	for( var y in ground ) {
		xs = ground[y];
		for( var x in xs ) {
			v = xs[x][0];
			if( v==0 )
				ctxmap.fillStyle = '#364';
			else if( v==20 )
				ctxmap.fillStyle = '#a93';
			else
				ctxmap.fillStyle = '#333';
			ctxmap.fillRect(x, y, 0.5, 0.5);
			//ctxmap.drawImage(groundImg, 0, 0, tile_size, tile_size, 0, 0, tile_size, tile_size);
		}
	}
	for( var i in objs ) {
		obj = objs[i];
		if( Math.round(obj.player.id)==Math.round(player_id) ) {
			ctxmap.strokeStyle = '#03E';
		} else {
			//debug( player_id +" player_id:"+obj.player.id );
			ctxmap.strokeStyle = '#E30';
		}
		ctxmap.beginPath();
		ctxmap.moveTo(obj.x, obj.y);
		ctxmap.lineTo(obj.x, obj.y+0.5);
		ctxmap.stroke();
	}
	var basex = parseInt(layerScrollX/tile_size);
	var basey = parseInt(layerScrollY/tile_size);
	var tilesx = parseInt((layer_width+tile_size)/tile_size);
	var tilesy = parseInt((layer_height+tile_size)/tile_size);
	ctxmap.strokeStyle = '#f00';
	ctxmap.strokeRect(basex+0.5, basey+0.5, tilesx+0.5, tilesy+0.5);
	ctxmap.restore();
}




/**
 * Load objects
 */
function loadObjects() {
	objs = {};
	$.getJSON( build_uri( "get_objs" ), function ( objects ) {
		for( var i in objects ) {
			objs[objects[i].pk] = new Obj( objects[i].pk, objects[i].fields );
		}
		loadAnims();
	} );
	
	objtypes = {};
	for( var i in objtypes_raw ) {
		objtypes[objtypes_raw[i].pk] = new ObjType( objtypes_raw[i].pk, objtypes_raw[i].fields );
	}
	teams = {};
	for( var i in teams_raw ) {
		teams[teams_raw[i].pk] = new Team( teams_raw[i].pk, teams_raw[i].fields );
	}
	players = {};
	for( var i in players_raw ) {
		players[players_raw[i].pk] = new Player( players_raw[i].pk, players_raw[i].fields );
	}
}



var lasttime = 0;
var fps = "";
var frame = 0;
/**
 * Animation loop
 */
function loopObjects() {
	var ctx = document.getElementById('layer0').getContext('2d');
	ctx.save();
	
	ctx.fillStyle = "#fff";
	ctx.font = 'arial 6px';
	
	real_redraw_all = redraw_all;
	redraw_all = false;
	
	for( var id in objs ) {
		objs[id].doAnim();
	}
	//if( new_object!=null )
	//	new_object.doAnim();
	
	for( var id in explosions ) {
		explosions[id].doAnim();
	}
	
	if( !real_redraw_all ) {
		doToRedraw();
		toredraw = {};
	}
	
	drawGround( ctx );
	
	for( var id in objs ) {
		objs[id].render( ctx );
	}

	for( var id in explosions ) {
		explosions[id].render( ctx );
	}
	
	if( new_object!=null )
		new_object.render( ctx );
	
	drawShadow( ctx );
	
	cursor.render( ctx );
	cursor.check();
	
	frame++;
	if( frame%50==0 ) {
		var curtime = (new Date()).getTime();
		fps = frame/((curtime-lasttime)/1000);
		lasttime = curtime;
		frame = 0;
		//debug( fps );
	}
	//ctx.fillText( fps, 30, 30 );
	
	ctx.restore();
}



function ObjFields() {
	// Empty
}
function Player( id, fields ) {
	this.id = id;
	for( var f in fields ) {
		this[f] = fields[f];
	}
}

function Team( id, fields ) {
	this.id = id;
	for( var f in fields ) {
		this[f] = fields[f];
	}
}

function ObjType( id, fields ) {
	this.id = id;
	for( var f in fields ) {
		this[f] = fields[f];
	}
	this.imgsrc = '/static/graphics/btn/'+this.objclass+'.gif';
	//this.img.src = this.imgsrc;
	//this.width = 32;
	//this.height = 32;
}


function addObj( tile ) {
	$.getJSON( build_uri( "add_obj" ), {'type_id':new_object.type.id, 'x':tile.x, 'y':tile.y}, function ( json ) {
		if( json.status=='ok' ) {
			new_object.id = json.obj.id;
			//new_object.is_building = true;
			new_object.add( json.obj );
			new_object = null;
			setAction( null );
			showAllActions( null );
		} else {
			debug( "CANNOT PLACE OBJECT" );
			reset();
		}
	} );
}

function showAllActions( o ) {
	var action_str = "";
	var ots = [];
	var have = [];
	for( var ko in objs ) {
		//debug( player_id+" have: "+objs[ko].player.id+" ("+objs[ko].type.objclass+")" );
		if( objs[ko].player.id==player_id )
			have.push( objs[ko].type.id );
	}
	//debug( "player_id: "+player_id );
	hs = ","+have.join(",")+",";
	//debug( " hs:"+hs );
	for( var k in objtypes ) {
		ot = objtypes[k];
		if( o && Math.round(ot.srctype)!=Math.round(o.type.id) )
			continue;
		if( !o )
			if( ot.objtype=='mobile' )
				continue;
		req = ot.require; //.split(",");
		//debug( ot.id+"require: "+ot.require );
		notenough = false;
		for( var kr in req ) {
			//debug( "test: "+req[kr]+" hs:"+hs );
			if( hs.search( ","+req[kr]+"," )==-1 )
				notenough = true;
		}
		//debug( " PASS: "+notenough );
		if( !notenough )
			ots.push( ot )
	}
	for( var k in ots ) {
		var ot = ots[k];
		var desc = "cost:"+ot.cost+" $";
		action_str+= "<a href=\"javascript:setAction('addobj:"+ot.id+"');\"><img class=\"action\" src=\""+ot.imgsrc+"\" alt=\""+desc+"\"></a>";
	}
	$("#actions").html( action_str );
}




/*
 * Selection / Actions
 */
function getSelection() {
	return currentSelection;
}
function setSelection( sel ) {
	if( sel!=currentSelection ) {
		$("#sel").html( "" );
		$("#actions").html( "" );
		$("#properties").html( "" );
		if( sel==null ) {
			showAllActions( null );
			cursor.setType( -1 );
		}
		if( sel==null || sel!=currentSelection ) {
			if( objs[currentSelection] )
				objs[currentSelection].unselect();
		}
		currentSelection = sel;
		setAction(null);
	}
}

function createObj( type, id, teamid, playerid ) {
	fields = new ObjFields();
	fields.team = teams[teamid];
	fields.type = objtypes[type];
	fields.player = players[playerid];
	no = new Obj( id, fields );
	no.setLifeLevel( no.type.life_capacity );
	no.is_building = true;
	return no
}

function setAction( act ) {
	currentAction = act;
	if( currentAction!=null ) {
		// Test if add_obj
		s = currentAction.split(":");
		if( s[0]=='addobj' ) {
			new_object = createObj( s[1], 0, team_id, player_id );
			if( new_object.type.objtype=='batiment' ) {
				currentAction = 'addobj';
			} else {
				o = objs[currentSelection];
				debug( o.type.id+" / "+new_object.type.srctype );
				if( currentSelection && o.type.id==new_object.type.srctype ) {
					tile = new Vector( o.x-1, o.y-1 );
					while( (ground[tile.y][tile.x][0]>0 && ground[tile.y][tile.x][0]<20) || ground[tile.y][tile.x][1]>0 ) {
						tile.y+=1;
					}
					if( ground[tile.y][tile.x][1]==0 && !(ground[tile.y][tile.x][0]>0 && ground[tile.y][tile.x][0]<20) )
						addObj( tile );
				}
				currentAction = '';
			}
		}
		debug( currentAction );
	}
}



function translatePos(pos) {
	var pane = $(".ui-layout-center").get(0);
	var panex = parseInt(pane.style['left']);
	var paney = parseInt(pane.style['top']);
	var pos = new Vector( (pos.x-panex) + layerScrollX-half_tile_size, (pos.y-paney) + layerScrollY-half_tile_size );
	return pos;
}

function untranslatePos(pos) {
	return new Vector( pos.x-layerScrollX, pos.y-layerScrollY );
}

function getMouseTile( pos ) {
	return getTileFromPos( translatePos( pos ) );
}


function get_coord(x, y) {
	return [x-layerScrollX, y-layerScrollY];
}


function getHoverObj( pos ) {
	var tpos = translatePos(pos);
	var tile = getTileFromPos(tpos);
	return getHoverObjDD( tile );
}


function getHoverObjD( tpos, use_team ) {
	// Try to get a selection on object
	for( var id in objs ) {
		if( use_team )
			if( objs[id].team.id!=team_id )
				continue;
		//xy = get_coord( objs[id].posx, objs[id].posy );
		xy = [objs[id].posx-half_tile_size, objs[id].posy-half_tile_size];
		//debug( "obj "+objs[id].type.objclass+" x: "+xy[0] + " y: "+ xy[1]+" mouse: x:"+relMouseX+" y:"+relMouseY );
		//if( xy[0]<=relMouseX && xy[0]+objs[id].w>=relMouseX && xy[1]<=relMouseY && xy[1]+objs[id].h>=relMouseY ) {
		if( xy[0]<=tpos.x && xy[0]+objs[id].w>=tpos.x && xy[1]<=tpos.y && xy[1]+objs[id].h>=tpos.y ) {
			return objs[id];
		}
	}
}


function getHoverObjDD( tile ) {
	if( ground[tile.y] && ground[tile.y][tile.x] ) {
		id = ground[tile.y][tile.x][1];
		if( id>0 ) {
			//debug( "found: "+id );
			return objs[id];
		}
	}
	return null;
}




function getTileFromPos(pos) {
	return new Vector( parseInt( pos.x/tile_size ), parseInt( pos.y/tile_size ) );
}
function getPosFromTile(tile) {
	return new Vector( (tile.x*24)-half_tile_size, (tile.y*24)-half_tile_size);
}


function doToRedraw() {
	for( var k in toredraw ) {
		var t = toredraw[k];
		//if( shadow[t.y][t.x].v==0 ) {
			ground[t.y][t.x][2] = 1;
			shadow[t.y][t.x].redraw = 1;
			o = getHoverObjDD( t );
			if( o ) o.markRedraw();
		//}
	}
}
function setGroundVal( x, y, ind, v ) {
	if( x>=0 && y>=0 && x<map_tiles_x && y<map_tiles_y && ground[y][x] )
		shadow[y][x].redraw = 1;
}
function addRedraw( t ) {
	//debug( t.x+" y:"+t.y );
	toredraw[t.x+":"+t.y] = t;
}
function setGround( pos, w, h ) {
	tile = getTileFromPos(pos);
	//p = new Vector( pos.x, pos.y );
		//debug( " pos x:"+pos.x+"y:"+pos.y+" tile.x:"+tile.x+" tile.y:"+tile.y+" w:"+w+" h:"+h );
		for( var y=-h-1; y<=h; y++ ) {
			for( var x=-w-1; x<=w; x++ ) {
				t = new Vector( tile.x+x, tile.y+y );
				//debug( "tile.x:"+t.x+" tile.y:"+tile.y+" -- t.x:"+t.x+" t.y:"+t.y+" x:"+x+" y:"+y+" pos:"+p.x+"y:"+p.y );
				if( t.x>=0 && t.y>=0 && ground[t.y][t.x] ) {
					addRedraw( t );
					// Check y+1 for batiment because they overlay on top
					if( x==w ) {
						o = getHoverObjDD( new Vector( t.x+1, t.y ) );
						if( o ) o.markRedraw();
					}
					if( x==-w-1 ) {
						o = getHoverObjDD( new Vector( t.x-1, t.y ) );
						if( o ) o.markRedraw();
					}
					if( y==h ) {
						o = getHoverObjDD( new Vector( t.x, t.y+1 ) );
						if( o ) {
							o.markRedraw();
							//debug( "Y+1 ti.x:"+t.x+" ti.y:"+tile.y+" -- t.x:"+t.x+" t.y:"+t.y+" x:"+x+" y:"+y+" o:"+o.id+" r:"+r );
						}
					}
					if( y==-h-1 ) {
						o = getHoverObjDD( new Vector( t.x, t.y-1 ) );
						if( o ) o.markRedraw();
					}
				}
			}
		}
}

/*
 * Cursor class
 */
function Cursor() {
	this.anim = 0;
	this.speed = 0;
	this.type = -1;
	this.pos = null;
	//this.lastpos = null;
	this.lasttype = this.type;
	this.tile = preload_image( '/static/graphics/cursors.png' );
}
Cursor.prototype.check = function() {
	if( this.type==-1 && this.lasttype==this.type ) return;
	this.lasttype = this.type;
	this.pos = translatePos( new Vector( realLastMouseX, realLastMouseY ) );
	//this.lastpos = this.pos;
	if( !real_redraw_all )
		setGround( this.pos, 1, 1 );
}
Cursor.prototype.setType = function( type ) {
	this.type = type;
	if( this.type==-1 )
		$("#layer0").get(0).style.cursor = 'move';
	else
		$("#layer0").get(0).style.cursor = '';
}
Cursor.prototype.update = function( pos ) {
	if( this.type==-1 ) return;

}
Cursor.prototype.render = function ( ctx ) {
	if( this.type==-1 ) return;
	var x = realLastMouseX-tile_size;
	var y = realLastMouseY-tile_size;
	var pane = $(".ui-layout-center").get(0);
	var panex = parseInt(pane.style['left']);
	var paney = parseInt(pane.style['top']);
	if( panex>0 && paney>0 ) {
		if( this.speed%4==0 )
			this.anim++;
		this.speed++;
		if( this.anim>2 ) this.anim = 0;
		ctx.drawImage(this.tile, this.type*24, 0+this.anim*24, 24, 24, x-panex, y-paney, 24, 24);
	}
}


function rand( min, max ) {
	return parseInt(Math.random()*max);
}

var logs = [];
function debug( s ) {
	logs.push( s );
	if( logs.length>83 )
		logs.splice( 0, 1 );
	$("#log").html( logs.join( "<br>" ) ).get(0).scrollTop = $("#log").get(0).scrollHeight;
}
function build_uri( cmd ) {
	uri = "/srv/" + game_id + "/" + player_id + "/" + cmd;
	//debug( uri );
	return uri;
}

