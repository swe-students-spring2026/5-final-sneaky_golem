function mirror() {
	for (row = 0; row < board.length; row++) {
		board[row].reverse();
		for (i = 0; i < board[row].length; i++) {
			if (board[row][i].t == 1) board[row][i].c = reversed[board[row][i].c];
		}
	}
	for (i = 0; i < queue.length; i++) {
		queue[i] = reversed[queue[i]];
	}
	holdP = reversed[holdP];
	piece = reversed[piece];

	xPOS = spawn[0];
	yPOS = spawn[1];
	rot = 0;
	clearActive();
	updateGhost();
	updateQueue();
	setShape();
	updateHistory();
}

function fullMirror() {
	for (i = 0; i < hist.length; i++) {
		tempBoard = JSON.parse(hist[i]['board']);
		for (row = 0; row < tempBoard.length; row++) {
			tempBoard[row].reverse();
			for (j = 0; j < tempBoard[row].length; j++) {
				if (tempBoard[row][j].t == 1) tempBoard[row][j].c = reversed[tempBoard[row][j].c];
			}
		}
		hist[i]['board'] = JSON.stringify(tempBoard);
		tempQueue = JSON.parse(hist[i]['queue']);
		for (j = 0; j < tempQueue.length; j++) {
			tempQueue[j] = reversed[tempQueue[j]];
		}
		hist[i]['queue'] = JSON.stringify(tempQueue);

		hist[i]['hold'] = reversed[hist[i]['hold']];
		hist[i]['piece'] = reversed[hist[i]['piece']];
	}
	board = tempBoard;
	queue = tempQueue;
	holdP = reversed[holdP];
	xPOS = spawn[0];
	yPOS = spawn[1];
	rot = 0;
	updateQueue();
	clearActive();
	updateGhost();
	setShape();
}

let test = [['X', 'X', 'X', 'X', 'X', 'X', 'G', 'G', 'G', 'G'], ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'], ['L', 'X', 'X', 'X', 'X', 'X', 'I', 'I', 'I', 'I'], ['L', 'X', 'X', 'X', 'X', 'T', 'X', 'Z', 'X', 'X'], ['L', 'L', 'O', 'O', 'T', 'T', 'Z', 'Z', 'X', 'X'], ['Z', 'Z', 'O', 'O', 'J', 'T', 'Z', 'S', 'X', 'X'], ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'], ['G', 'G', 'G', 'X', 'G', 'G', 'G', 'G', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G'], ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G']];

function garbage(column, amount = 1) {
	parseBoard(test);
	/*
	for (i = 0; i < amount; i++) {
		garbageRow = new Array(10).fill({ t: 1, c: 'X' });
		garbageRow[column] = { t: 0, c: '' };
		board.shift();
		board.push(garbageRow);
	}
	xPOS = spawn[0];
	yPOS = spawn[1];
	updateGhost();
	*/
}

function parseBoard(boardState){
	print("run");
	for(let y = 0; y < boardState.length; y++){
		let row = new Array(10).fill({ t: 0, c: '' });
		for(let x = 0; x < boardState[y].length; x++){
			const piece = boardState[y][x].toUpperCase();
			switch(piece){
				case "G":
					row[x] = { t: 1, c: 'X' };
					break;
				case "X":
					break;
				default:
					row[x] = { t: 1, c: piece };
			}
		}
		board.shift();
		board.push(row);
		print("ranner");
	}
}
//example board
/*
[['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
['X', 'X', 'X', 'X', 'X', 'X', 'G', 'G', 'G', 'G'],
['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
['J', 'X', 'X', 'X', 'X', 'X', 'S', 'S', 'S', 'S'],
['J', 'X', 'X', 'X', 'X', 'T', 'X', 'J', 'X', 'X'],
['J', 'J', 'I', 'I', 'T', 'T', 'J', 'J', 'X', 'X'],
['J', 'J', 'I', 'I', 'Z', 'T', 'J', 'I', 'X', 'X'],
['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G', 'G'],
['G', 'G', 'G', 'X', 'G', 'G', 'G', 'G', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G'],
['G', 'G', 'G', 'G', 'G', 'G', 'G', 'X', 'G', 'G']]
*/
