var audios = [];
var loadedAudioElements = 0;
var toloadAudioElements = 0;

var host = ""; //http://devlocked.hopto.org";


function realAudioLoad() {
	toloadAudioElements = audios.length-1;
	for( var ii in audios ) {
		var audioElement = audios[ii][1];
		audioElement.addEventListener("error", function() {
			//alert( "error"+this.src );
		}, true);
		audioElement.addEventListener("load", function() {
			loadedAudioElements++;
		}, true);
		audioElement.src = audios[ii][0];
		audioElement.load();
	}
}

function getAudioElement( audioname ) {
	//debug( audioname );
	var src = host + "/static/sounds/" + audioname;
	src = src.replace( "#", "%23" );
	for( var ii in audios )
		if( audios[ii][0]==src )
			break;
	if( audios[ii] && audios[ii][0]==src ) {
		var audioElement = audios[ii][1];
		//debug( "LOAD SOUND [CACHED]: "+src );
	} else {
		var audioElement = new Audio();
		//debug( "LOAD SOUND: "+src );
		audios.push( [src,audioElement] );
	}
	return audioElement;
}

function loadAudio() {
	var all = [];
	all.push( "allies/allies #1 achnoledged.ogg" );
	all.push( "allies/allies #1 affirmative.ogg" );
	all.push( "allies/allies #1 reporting.wav" );
	all.push( "allies/allies #1 yes sir.ogg" );
	all.push( "allies/allies #2 achnoledged.wav" );
	all.push( "allies/allies #2 agreed.ogg" );
	all.push( "allies/allies #2 as you wish.ogg" );
	all.push( "allies/allies #2 at once.wav" );
	all.push( "allies/allies #2 of course.wav" );
	all.push( "allies/allies #2 ready & waiting.wav" );
	all.push( "allies/allies #2 verry well.wav" );
	all.push( "allies/allies #2 yes sir!.ogg" );
	all.push( "allies/allies #3 achnoledged.wav" );
	all.push( "allies/allies #3 affirmative.wav" );
	all.push( "allies/allies #3 reporting.wav" );
	all.push( "russian/soviet #1 achnoledged.wav" );
	for( var iii in all ) {
		getAudioElement( all[iii] );
	}
	realAudioLoad();
}
