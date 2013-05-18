function fireGet(target) {
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", target, true);
	xmlHttp.send();
}

function fireGetSync(target) {
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", target, false);
	xmlHttp.send(null);

	return xmlHttp.responseText;
}

function activateButton(buttonId) {
	fireGet("controlActivate/" + g_userId + "/" + buttonId)
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

					if (gameData.playerTask.id != g_lastTaskAction) {
						// received a new task, setup everyting
						g_lastTaskAction = gameData.playerTask.id;
						startCommandCountdown(gameData.playerTask.maxTime);
						playerTask.innerHTML = gameData.playerTask.taskName;
					}

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

function createControls(controls) {
	var controlContainer = document.getElementById("controlContainer");

	var allContent = "";

	for (i in controls) {
		var cnt = controls[i];

		console.log(cnt)
		console.log("Creating control " + cnt["name"] + " of type "
				+ cnt["type"]);
		if (cnt["type"] == "pushButton") {
			allContent += "<var class='EvaderControl' ";
			allContent += "onClick='activateButton(" + cnt["id"] + ")' ";
			allContent += ">" + cnt["name"];
			allContent += "</var>";
		}

	}

	controlContainer.innerHTML = allContent

}

function callbackCountdown() {
	g_currentCommandTime -= g_commandIntervalMs * 0.001;

	var playerTask = document.getElementById("playerTask");

	if (g_currentCommandTime < 0.0) {
		console.log("Command failed !!");
		playerTask.innerHTML = "-- NOT COMPLETED --";
		clearInterval(g_commandInterval);
		return;
	}

	console.log("Current command has " + g_currentCommandTime + " second left");

	// update the color of the thingy
	ratio = g_currentCommandTime / g_fullCommandTime;
	var maxGreen = 250.0;
	var maxRed = 250.0;

	var green = Math.round((ratio) * maxGreen);
	var red = Math.round((1.0 - ratio) * maxRed);

	var rgbString = "rgb(" + red + "," + green + ",0)"

	// console.log(playerTask.style);
	playerTask.style.backgroundColor = rgbString;
	// playerTask.innerHTML = rgbString;
}

function startCommandCountdown(timeInSeconds) {
	g_currentCommandTime = timeInSeconds;
	g_fullCommandTime = timeInSeconds;

	g_commandIntervalMs = 200;

	g_commandInterval = window.setInterval(callbackCountdown,
			g_commandIntervalMs);
}

function enableGameStateCallback() {
	// WebSocketTest();
	// initWebSocket();
	g_lastTaskAction = ""
	g_userId = fireGetSync("registerPlayer");

	var userControls = JSON.parse(fireGetSync("listControls/" + g_userId));
	createControls(userControls);
	console.log("players id will be " + g_userId);

	window.setInterval(checkForTask, 4000);
	console.log("interval set");

}
