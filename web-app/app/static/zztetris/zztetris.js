let queueData = [];
let boardStart = [];
let log = [];

function restart() {
	if (board[board.length - 1].filter((c) => c.t != 1).length == boardSize[0]) {
		// lazy check, will have false positives, but whatever
		if (queue[6] == '|' && holdP == '') {
			// if they reset after resetting, just restart hist
			hist = [
				{
					board: JSON.stringify(board),
					queue: JSON.stringify(queue),
					hold: holdP,
					piece: piece,
				},
			];
			histPos = 0;
		}
	}
	board = structuredClone(boardStart);
	//console.log(boardStart);
	console.log(queueData);
	queue = [...queueData];
	console.log(queue);
	rot = 0;
	piece = '';
	holdP = '';
	held = false;
	xPOS = spawn[0];
	yPOS = spawn[1];
	xGHO = spawn[0];
	yGHO = spawn[1];
    oldcombo = combo;
	combo = -1;
    oldb2b = b2b;
	b2b = -1;
	log = [];
	newPiece()
}

function updateQueue() {
	temp = false;
	ctxN.clearRect(0, 0, 90, 360);
	ctxH.clearRect(0, 0, 90, 60);
	print(queue);
	//notes to self. Generates a set of 6, then a | to indicate that another 6 needs to be generated. Never hits 6 pieces. Always adds more if 6 is hit
	for (let i = 0; i < 7; i++) {
		if (queue[i] == '|') {
			ctxN.beginPath();
			ctxN.moveTo(0, i * 60);
			ctxN.lineTo(90, i * 60);
			ctxN.stroke();
			temp = true;
		} else {
			j = i;
			if (temp) j--;
			if(imgs[queue[i]]){
				ctxN.drawImage(imgs[queue[i]], 0, j * 60);
			}
		}
	}
	if (holdP) ctxH.drawImage(imgs[holdP], 0, 0);
}

function shuffleQueue() {
	// locate bag separator
	index = 0;
	while (index < queue.length && queue[index] != '|') index++;

	tempQueue = queue.slice(0, index).concat(piece).shuffle().concat('|');
	// the queue before the bag separator (the current bag), plus active piece; shuffle it; add bag separator to end
	piece = tempQueue.shift();
	queue = tempQueue;

	while (queue.length < 10) {
		var shuf = names.shuffle();
		shuf.map((p) => queue.push(p));
		queue.push('|');
	}
	xPOS = spawn[0];
	yPOS = spawn[1];
	rot = 0;
	clearActive();
	checkTopOut();
	updateQueue();
	updateGhost();
	setShape();
	updateHistory();
}

function shuffleQueuePlusHold() {
	if (!holdP) {
		shuffleQueue();
		return;
	}

	index = 0;
	while (index < queue.length && queue[index] != '|') index++;

	tempQueue = queue.slice(0, index).concat(piece, holdP).shuffle().concat('|');
	holdP = tempQueue.shift();
	piece = tempQueue.shift();
	queue = tempQueue;

	while (queue.length < 10) {
		var shuf = names.shuffle();
		shuf.map((p) => queue.push(p));
		queue.push('|');
	}
	xPOS = spawn[0];
	yPOS = spawn[1];
	rot = 0;
	clearActive();
	checkTopOut();
	updateQueue();
	updateGhost();
	setShape();
	updateHistory();
	restart();
}

function setBoard(setter){
	const data = prompt("Please enter a queue:");
	const data2 = setter.replace(/'/g, '"');
	parseBoard(JSON.parse(data2));
	boardStart = structuredClone(board);
	const dataArr = data.split('');
	queue = [];
	for(let i = 0; i < dataArr.length; i++){
		if(i % 6 == 0 && i != 0){
			queue.push('|')
		}
		queue.push(dataArr[i].toUpperCase());
	}
	if(queue.length > 0 && queue[queue.length-1] != '|'){
		queue.push('|');
	}
	xPOS = spawn[0];
	yPOS = spawn[1];
	rot = 0;
	queueData = [...queue];
	clearActive();
	checkTopOut();
	updateQueue();
	updateGhost();
	setShape();
	updateHistory();
}

function logBoard(){
	log.push(structuredClone(board));
}

function endPuzzle(){
	console.log("wraps");
	data = []
	for(let i = 0; i < log.length; i++){
		column = [];
		for(let y = 0; y < log[i].length; y++){
			row = []
			for(let x = 0; x < log[i][y].length; x++){
				block = log[i][y][x].c
				if(block == ''){
					block = "X";
				}
				else if(block == "X"){
					block = "G";
				}
				row.push(block);
			}
			column.push(row);
		}
		data.push(column);
	}
	console.log(data);
	console.log(log);
	document.getElementById("solution-data").setAttribute("value", JSON.stringify(data));
}

function updateKickTable() {
	kicks = kicksets[document.getElementById('kickset').value];
}

function game() {
	callback();
}
