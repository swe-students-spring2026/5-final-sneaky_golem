function PC(PC_num) {
    restart();
    var currBag = ('ZLOSIJT'.split('').shuffle().slice(0, (10 - 3*PC_num) % 7));
    if (PC_num == 8) {
        currBag = 'ZLOSIJT'.split('').shuffle();
        currBag.splice(Math.ceil(Math.random()*6), 1, currBag[0]);
    } else if (PC_num == 9) {
        var ninths = ["TLI", "TJI", "TLS", "TJS", "TLO", "TJO", "TLZ", "TJZ"];
        currBag = (ninths[Math.floor(Math.random() * 8)]).split('').shuffle();
        currBag.unshift("T");
    }
    currBag.push('|');
    queue = currBag;
    newPiece();
}

function doc_keyUp(e) {
    // you can grab keycode values off a tool such as https://keycode.info/
    switch (e.keyCode) {
        case 49:
            PC(1);
            break;
        case 50:
            PC(2);
            break;
        case 51:
            PC(3);
            break;
        case 52:
            PC(4);
            break;
        case 53:
            PC(5);
            break;
        case 54:
            PC(6);
            break;
        case 55:
            PC(7);
            break;
        case 56:
            PC(8);
        case 57:
            PC(9);
        default:
            break;
    }
}

document.addEventListener('keyup', doc_keyUp, false);

function restart() {
	if (board[board.length - 1].filter((c) => c.t == 0).length == boardSize[0]) {
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
	board = [];
	for (let i = 0; i < boardSize[1]; i++) {
		board.push(aRow());
	}
	queue = [];
	rot = 0;
	piece = '';
	holdP = '';
	held = false;
	xPOS = spawn[0];
	yPOS = spawn[1];
	xGHO = spawn[0];
    yGHO = spawn[1];

    combo = -1;
    b2b = -1;
	newPiece();
}

function updateQueue() {
	temp = false;
	ctxN.clearRect(0, 0, 90, 360);
	ctxH.clearRect(0, 0, 90, 60);
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
			ctxN.drawImage(imgs[queue[i]], 0, j * 60);
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
}

function updateKickTable() {
	kicks = kicksets[document.getElementById('kickset').value];
}

function game(){
	callback();
}
