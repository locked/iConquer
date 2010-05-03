


/*
function startAnims() {
	var animations = [];
	for( var i=0; i<anims.length; i++ ) {
		a = anims[i];
		if( a.plist.length>0 ) {
			pl = a.plist[0];
			
			aimx = pl[0]; //.x;
			aimy = pl[1]; //.y;
			
			curx = objs[a.obj].x;
			cury = objs[a.obj].y;
			curposx = objs[a.obj].posx;
			curposy = objs[a.obj].posy;
			if( aimy*24<curposy ) {
				curposy -= 2;
				objs[a.obj].orient = "";
				if( aimy*24>=curposy ) {
					curposy = aimy*24;
					a.plist.shift();
				}
				objs[a.obj].posy = curposy;
			}
			if( aimy*24>curposy ) {
				curposy += 2;
				objs[a.obj].orient = "180";
				if( aimy*24<=curposy ) {
					curposy = aimy*24;
					a.plist.shift();
				}
				objs[a.obj].posy = curposy;
			}
			if( aimx*24<curposx ) {
				curposx -= 2;
				objs[a.obj].orient = "l90";
				if( aimx*24>=curposx ) {
					curposx = aimx*24;
					a.plist.shift();
				}
				objs[a.obj].posx = curposx;
			}
			if( aimx*24>curposx ) {
				curposx += 2;
				objs[a.obj].orient = "r90";
				if( aimx*24<=curposx ) {
					curposx = aimx*24;
					a.plist.shift();
				}
				objs[a.obj].posx = curposx;
			}
			objs[a.obj].x = parseInt(curposx/24);
			objs[a.obj].y = parseInt(curposy/24);
			objs[a.obj].updateObject();
		} else {
			anims.splice(i,1);
		}
		var desc = "OID: " +a.obj + " (" + a.plist.length + ") ";
		if( a.plist.length>0 )
			desc += " " + a.plist[0][0] + ":" + a.plist[0][1] + " -> " + a.plist[a.plist.length-1][0] + ":" + a.plist[a.plist.length-1][1];
		animations.push( desc );
	}
	// Show current animations (debug)
	$("#animations").html( animations.join("<br>") );
}
*/

/*
function mouseDown( e ) {
	if( currentAction=="move" ) {
		var pos = getMousePosition(e);
		//alert( $(e.target) );
		var ground = $("#ground").get(0);
		var pane = $(".ui-layout-center").get(0);
		var panex = parseInt(pane.style['left']);
		var paney = parseInt(pane.style['top']);
		var decx = Math.abs(parseInt(ground.style['left']));
		var decy = Math.abs(parseInt(ground.style['top']));
		//alert( decx );
		var posx = (pos.x - panex) + decx;
		var posy = (pos.y - paney) + decy;
		var tilex = parseInt( posx/24 );
		var tiley = parseInt( posy/24 );
		//var curtilex = objs[currentSelection].x;
		//var curtiley = objs[currentSelection].y;
		askPath( currentSelection, tilex, tiley );
	}
}
*/

/*
function findPath( curtilex, curtiley, tilex, tiley ) {
	var startPoint = [curtilex, curtiley];
	//alert( 'X: ' + startPoint[0] + ' Y:' + startPoint[1] );
	var endPoint = [tilex, tiley];
	//alert( 'X: ' + endPoint[0] + ' Y:' + endPoint[1] );
	var method = "Manhattan";
	//alert( "Before:"+grid[13][7] );
	//alert( "After:"+grid[13][6] );
	//alert( "After:"+grid );
	var result = AStar( grid, startPoint, endPoint, method );
	//alert( 'X: ' + result[0][0] + ' Y:' + result[0][1] );
	var plist = [];
	for(var x, y, i = 1, j = result.length; i < j; i++) {
		var x = result[i][0];
		var y = result[i][1];
		pl = {'x':x,'y':y};
		plist.push( pl );
		//alert( 'X: ' + pl.x + ' Y:' + pl.y );
	}
	//alert( 'lenX: ' + plist.length );
	//plist = [{'x':11,'y':9}, {'x':11,'y':8}, {'x':10,'y':8}];
	return plist;
}
*/

/**
 * Clean animations of obj objid
function anim_clear( objid ) {
	for( var i=0; i<anims.length; i++ ) {
		a = anims[i];
		if( a.obj==objid )
			anims.splice( i, 1 );
	}
}
 */