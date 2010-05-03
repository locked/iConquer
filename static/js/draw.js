var groundImg;
var basex = 0;
var basey = 0;
var tile_size = 24;
var half_tile_size = Math.floor( tile_size/2 );
var grounds_tiles = {};
var tiles;

var shadowTile;
var shadows = {};

var all_imgs = [];
var explosionTile;
var explosions = {};

var imagesLoaded = 0;
var imagesToPreload = 0;

function loadGroundTiles() {
	explosionTile = preload_image('/static/graphics/general/explosion.png');
	groundImg = preload_image('/static/graphics/grounds.png');
	
	for( var i=0; i<255; i++ )
		grounds_tiles[i] = [0,0];
	grounds_tiles[1] = [0,24];
	grounds_tiles[2] = [96,48];
	grounds_tiles[3] = [120,48];
	grounds_tiles[4] = [172,48];
	grounds_tiles[5] = [148,48];
	//grounds_tiles[6] = [0,48];
	grounds_tiles[7] = [192,48];
	grounds_tiles[8] = [0,48];
	//grounds_tiles[9] = [0,48];
	//grounds_tiles[10] = [0,48];
	//grounds_tiles[11] = [0,48];
	grounds_tiles[20] = [0,24];
	
	loadShadows();
}

function loadShadows() {
	shadowTile = preload_image('/static/graphics/general/shadow-trans.png');
	
	shadows["3,-1,0,-1,0"] = 1; //ok
	shadows["3,-2,0,-1,0"] = 3; //ok
	shadows["1,-1,0,0,0"] = 33; //ok
	shadows["3,-1,-1,3,0"] = 9; //ok
	shadows["1,3,3,1,0"] = 6; //ok
	shadows["0,1,3,1,0"] = 4; //ok
	shadows["-1,1,3,3,0"] = 12; //ok
	shadows["-1,0,-1,3,0"] = 8; //ok
	shadows["2,-2,0,0,0"] = 3; //ok
	shadows["2,3,1,0,0"] = 3; //ok
	shadows["3,3,1,-1,0"] = 3; //ok

	shadows["3,3,3,3,0"] = 46; //ok
	shadows["4,3,3,3,1"] = 14; //ok
	shadows["3,4,3,3,1"] = 13; //ok
	shadows["3,3,4,3,1"] = 11; //ok
	shadows["3,3,3,4,1"] = 7; //ok

	shadows["-1,0,0,-1,0"] = 32; //ok
	shadows["3,-1,0,-2,0"] = 9; //ok
	shadows["-2,0,0,-1,0"] = 1; //ok

 	shadows["0,0,-2,1,0"] = 4; //ok
 	shadows["0,0,-1,1,0"] = 35; //ok
 	shadows["0,1,3,2,0"] = 12; //ok

	shadows["1,-1,-2,1,0"] = 26; //ok
	shadows["2,-1,-1,1,0"] = 24; //ok
	
	shadows["-2,0,0,-1,0"] = 1;
	shadows["2,-1,0,0,0"] = 1;

 	shadows["0,0,-1,2,0"] = 8;
 	shadows["-1,0,0,-2,0"] = 8;

 	shadows["1,3,1,0,0"] = 2;

 	shadows["1,-2,0,0,0"] = 2;
 	shadows["0,2,3,1,0"] = 6;
 	shadows["0,1,1,0,0"] = 34;
 	shadows["0,1,2,0,0"] = 4;
 	shadows["-1,0,-2,3,0"] = 12;
 	shadows["1,3,2,0,0"] = 6;
 	shadows["0,2,1,0,0"] = 2;
 	shadows["-2,0,-1,3,0"] = 9;
 	shadows["0,0,-2,2,0"] = 12;
	
 	//shadows["0,0,4,0,0"] = 35; // totest
}

function loadTiles() {
	var uri = "/game/get_all_obj_tiles";
	$.getJSON( uri, function ( json ) {
		for( var i in json ) {
			preload_image( json[i] );
		}
		loadObjects();
	} );
}


function loadImages() {
	loadGroundTiles();
	
	//alert( imagesLoaded+" >= "+imagesToPreload );
	for( var i in all_imgs ) {
		load_image( all_imgs[i][1], all_imgs[i][0] );
	}
}

function load_image(img,uri) {
	//var img = new Image();
	img.onload = on_image_load_event;
	img.onerror = on_image_load_event;
	img.onabort = on_image_load_event;
	img.src = uri;
	return img;
}

function preload_image(uri) {
	var i=0;
	for( i in all_imgs ) {
		if( all_imgs[i][0]==uri )
			break;
	}
	if( all_imgs[i] && all_imgs[i][0]==uri ) {
		var img = all_imgs[i][1];
		//debug( "LOAD IMG [CACHED]: "+uri );
	} else {
		imagesToPreload++;
		//debug( "LOAD IMG: "+uri );
		var img = new Image();
		all_imgs.push( [uri,img] );
	}
	return img;
}

function on_image_load_event() {
	imagesLoaded++;
	if (imagesLoaded >= imagesToPreload) {
		realStartGame();
	}
}



function getGround( kkx, kky ) {
	if( kkx>=0 && kky>=0 && kkx<map_tiles_x && kky<map_tiles_y )
		return shadow[kky][kkx].v;
	return 1;
}

function getShadow( x, y ) {
	for( var k=-1; k<2; k+=2 ) {
		var tmp = 0;
		var sum = getGround( x-1, y+k ) + getGround( x, y+k ) + getGround( x+1, y+k );
		if( sum==3 ) tmp = 3;
		else if( sum==2 && getGround( x, y+k )==0 ) tmp = 4;
		else if( sum==2 && getGround( x-1, y+k )==1 ) tmp = -2;
		else if( sum==2 && getGround( x+1, y+k )==1 ) tmp = 2;
		else if( sum==1 && getGround( x-1, y+k )==1 ) tmp = -1;
		else if( sum==1 && getGround( x+1, y+k )==1 ) tmp = 1;
		//if( tmp==4 )
		//	debug( "k:"+k+" tmp:"+tmp+" sum:"+sum+"<br>" );
		if( k==-1 )
			var top = tmp;
		else
			var bottom = tmp;
	}
	
	for( var k=-1; k<2; k+=2 ) {
		var tmp = 0;
		var sum = getGround( x+k, y-1 ) + getGround( x+k, y ) + getGround( x+k, y+1 );
		if( sum==3 ) tmp = 3;
		else if( sum==2 && getGround( x+k, y )==0 ) tmp = 4;
		else if( sum==2 && getGround( x+k, y-1 )==1 ) tmp = -2;
		else if( sum==2 && getGround( x+k, y+1 )==1 ) tmp = 2;
		else if( sum==1 && getGround( x+k, y-1 )==1 ) tmp = -1;
		else if( sum==1 && getGround( x+k, y+1 )==1 ) tmp = 1;
		//if( tmp==4 )
		//	debug( "k:"+k+" tmp:"+tmp+"<br>" );
		if( k==1 )
			var right = tmp;
		else
			var left = tmp;
	}
	
	var hash = top+","+right+","+bottom+","+left+","+getGround( x, y );
	return hash;
}

function getIndFromHash( hash ) {
	if( hash=="0,0,0,0,0" )
		return 0;
	if( typeof shadows[hash]=="undefined" )
		ind = 0
	else
		ind = parseInt( shadows[hash] );
	if( ind>48 ) ind = 0;
	return ind;
}


/*
 * DRAW
 */
function drawShadow( ctx ) {
	var basex = parseInt(layerScrollX/tile_size);
	var y = parseInt(layerScrollY/tile_size);
	var tilesx = parseInt((layerScrollX+layer_width+tile_size)/tile_size);
	var tilesy = parseInt((layerScrollY+layer_height+tile_size)/tile_size);
	if( tilesx>map_tiles_x ) tilesx = map_tiles_x-1;
	if( tilesy>map_tiles_y ) tilesy = map_tiles_y-1;
	var _y = (tile_size-layerScrollY%tile_size) - tile_size;
	while (y < tilesy) {
		var x = basex, _x = (tile_size-layerScrollX%tile_size) - tile_size;
		while (x < tilesx) {
			if( shadow[y][x].redraw==1 || real_redraw_all ) {
				if( shadow[y][x].v==0 ) {
					var hash = getShadow( x, y );
					var shadowind = getIndFromHash( hash );
					if( shadowind>0 )
						ctx.drawImage(shadowTile, shadowind*tile_size, 0, tile_size, tile_size, _x, _y, tile_size, tile_size);
					if( typeof shadows[hash]=="undefined" && hash!="0,0,0,0,0" ) {
						ctx.fillText( hash, _x, _y );
					}
				} else {
					ctx.drawImage(shadowTile, 0, 0, tile_size, tile_size, _x, _y, tile_size, tile_size);
				}
				shadow[y][x].redraw = 0;
			}
			x+=1;
			_x += tile_size;
		}
		y+=1;
		_y += tile_size;
	}
}


function drawGround( ctx ) {
	//ctx.clearRect(0,0,layer_width+tile_size,layer_height+tile_size); // IE (excanvas) optimisation, clear the canvas
	
	// Draw each brick
	var basex = parseInt(layerScrollX/tile_size);
	var y = parseInt(layerScrollY/tile_size);
	var tilesx = parseInt((layerScrollX+layer_width+tile_size)/tile_size);
	var tilesy = parseInt((layerScrollY+layer_height+tile_size)/tile_size);
	if( tilesx>map_tiles_x ) tilesx = map_tiles_x-1;
	if( tilesy>map_tiles_y ) tilesy = map_tiles_y-1;
	var _y = (tile_size-layerScrollY%tile_size) - tile_size;
	//alert( ground.length );
	while (y < tilesy) {
		var x = basex, _x = (tile_size-layerScrollX%tile_size) - tile_size;
		while (x < tilesx) {
			if( typeof ground!='undefined' )
				if( typeof ground[y][x]!='undefined' )
					tile = grounds_tiles[ground[y][x][0]];
				else
					tile = [0,0];
			else
				tile = [0,0];
			if( ground[y][x][2]==1 || real_redraw_all ) {
				if( shadow[y][x].v==0 ) {
					ctx.drawImage(groundImg, tile[0], tile[1], tile_size, tile_size, _x, _y, tile_size, tile_size);
				}
				//ctx.fillText( ground[y][x][0]+":"+ground[y][x][1]+":"+ground[y][x][2], _x, _y );
				//ctx.fillText( ground[y][x][1]+":"+ground[y][x][2], _x, _y );
				//ctx.fillText( ground[y][x][3], _x, _y );
				ground[y][x][2] = 2;
				shadow[y][x].redraw = 1;	//for shadows
			}
 			//ctx.drawImage(groundImg, 0, 0, tile_size, tile_size, _x, _y, tile_size, tile_size);
			x+=1;
			_x += tile_size;
		}
		y+=1;
		_y += tile_size;
	}
}
