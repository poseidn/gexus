function fireGet(target) {
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", target, true);
	xmlHttp.send();
}

function fireGetSync(target) {
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", target, false);
	xmlHttp.send( null);
	
	return xmlHttp.responseText;
}

function activateButton( buttonId ) {
	fireGet( "controlActivate/" + g_userId + "/" +buttonId)
}

function checkForTask() {
	console.log("loading game state");
	xmlHttp = new XMLHttpRequest();
	if (xmlHttp) {
		xmlHttp.open('GET', 'gameState/' + g_userId, true);
		xmlHttp.onreadystatechange = function() {
			if (xmlHttp.readyState == 4) {
				gameData = JSON.parse(xmlHttp.responseText);
				// document.write( gameData["player"][0] );
				// = gameData["player"][0];
				playerTask = document.getElementById("playerTask");
				// playerRep.style.left = 100 - (gameData["player"][0] * 8.0);
				if (gameData.playerTask == 0) {
					playerTask.innerHTML = "- no task - ";
				} else {
					playerTask.innerHTML = gameData.playerTask.taskName;
				}
				
				playerId = document.getElementById("playerId");
				playerId.innerHTML = gameData.playerId
				// alert(gameData["player"][0]);
			}
		};
		xmlHttp.send();
	}

}

function WebSocketTest() {
	if ("WebSocket" in window) {
		console.log("puh, web sockets is supported");
	} else {
		// The browser doesn't support WebSocket
		alert("WebSocket NOT supported by your Browser!");
	}
}

function initWebSocket() {
	if ("WebSocket" in window) {
		// Let us open a web socket
		// todo: query web socket uri from the server
		var ws = new WebSocket("ws://192.168.1.33:8080/EvaderWs/ws");
		ws.onopen = function() {
			// Web Socket is connected, send data using send()
			ws.send("Message to send");
			// alert("Message is sent...");
		};
		ws.onmessage = function(evt) {
			var received_msg = evt.data;
			// console.log("Message is received...");

			var gameData = JSON.parse(received_msg);
			var playerRep = document.getElementById("view");
			playerRep.style.left = 500 - (gameData["player"][0] * 40.0);
		};
		ws.onclose = function() {
			// websocket is closed.
			alert("Connection is closed...");
		};
	} else {
		// The browser doesn't support WebSocket
		alert("WebSocket NOT supported by your Browser!");
	}
}

function enableGameStateCallback() {
	// WebSocketTest();
	// initWebSocket();
	g_userId = fireGetSync("registerPlayer");
	console.log( "players id will be " + g_userId);
	
	window.setInterval(checkForTask, 1000);
	console.log("interval set");

}