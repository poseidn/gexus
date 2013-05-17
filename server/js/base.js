
function fireGet(target) {
	xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", target, true);
	xmlHttp.send();
}

