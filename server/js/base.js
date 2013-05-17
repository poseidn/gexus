function fireGet(target) {
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", target, true);
	xmlHttp.send();
}

function checkForPositions() {
	console.log("loading game state");
	xmlHttp = new XMLHttpRequest();
	if (xmlHttp) {
		xmlHttp.open('GET', 'gameState', true);
		xmlHttp.onreadystatechange = function() {
			if (xmlHttp.readyState == 4) {
				gameData = JSON.parse(xmlHttp.responseText);
				// document.write( gameData["player"][0] );

				 //= gameData["player"][0];

				playerRep = document.getElementById("view")
				playerRep.style.top = 100 - ( gameData["player"][0] * 8.0 );

				// alert(gameData["player"][0]);
			}
		};
		xmlHttp.send();
	}

}

function enableGameStateCallback() {
	window.setInterval(checkForPositions, 20);
	console.log("interval set");
	

}