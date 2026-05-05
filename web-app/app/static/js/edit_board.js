(function () {
    'use strict';

    const ROWS = 20, COLS = 10, CELL = 28;

    const SHAPES = {
        I: [[0,0],[0,1],[0,2],[0,3]],
        O: [[0,0],[0,1],[1,0],[1,1]],
        T: [[0,0],[0,1],[0,2],[1,1]],
        S: [[0,1],[0,2],[1,0],[1,1]],
        Z: [[0,0],[0,1],[1,1],[1,2]],
        J: [[0,0],[1,0],[1,1],[1,2]],
        L: [[0,2],[1,0],[1,1],[1,2]],
    };

    const PIECE_TYPES = ['I','O','T','S','Z','J','L'];

    let matrix = [], instances = {}, nextId = 0, rotation = 0, holeCol = 4;
    let activeTool = 'delete', painting = false, queue = [];
    let dragging = null, draggingGarbage = false;
    let ghost = null, hoverCells = [], hoverAnchor = null;

    const initMatrix = () => {
        matrix = Array.from({ length: ROWS }, () => new Array(COLS).fill(null));
    };

    const rotateCW = cells => {
        const maxRow = Math.max(...cells.map(([r]) => r));
        return cells.map(([r, c]) => [c, maxRow - r]);
    };

    const getRotatedShape = type => {
        let cells = SHAPES[type].slice();
        for (let i = 0; i < rotation; i++) cells = rotateCW(cells);
        return cells;
    };

    const getSlotSize = type => {
        let cells = SHAPES[type].slice(), maxRows = 0, maxCols = 0;
        for (let i = 0; i < 4; i++) {
            maxRows = Math.max(maxRows, Math.max(...cells.map(([r]) => r)) + 1);
            maxCols = Math.max(maxCols, Math.max(...cells.map(([,c]) => c)) + 1);
            cells = rotateCW(cells);
        }
        return { rows: maxRows, cols: maxCols };
    };

    // useRotation=true: respects current rotation (palette); false: always base shape (queue thumbnails)
    function buildPieceEl(type, size, useRotation = true) {
        const shape = useRotation ? getRotatedShape(type) : SHAPES[type];
        const slot = getSlotSize(type);
        const shapeRows = Math.max(...shape.map(([r]) => r)) + 1;
        const shapeCols = Math.max(...shape.map(([,c]) => c)) + 1;
        const offR = Math.floor((slot.rows - shapeRows) / 2);
        const offC = Math.floor((slot.cols - shapeCols) / 2);
        const wrap = document.createElement('div');
        wrap.style.cssText = `position:relative;width:${slot.cols*size}px;height:${slot.rows*size}px;flex-shrink:0`;
        shape.forEach(([r, c]) => {
            const cell = document.createElement('div');
            cell.className = 'board-cell';
            cell.dataset.piece = type;
            cell.style.cssText = `position:absolute;left:${(c+offC)*size}px;top:${(r+offR)*size}px;width:${size}px;height:${size}px`;
            wrap.appendChild(cell);
        });
        return wrap;
    }

    function buildGarbageEl(size) {
        const wrap = document.createElement('div');
        wrap.style.display = 'inline-flex';
        for (let c = 0; c < COLS; c++) {
            const cell = document.createElement('div');
            cell.className = 'board-cell';
            cell.style.width = cell.style.height = size + 'px';
            if (c !== holeCol) cell.dataset.piece = 'G';
            else cell.classList.add('garbage-hole');
            wrap.appendChild(cell);
        }
        return wrap;
    }

    function renderQueue() {
        const listEl = document.getElementById('piece-queue');
        listEl.innerHTML = '';
        if (!queue.length) {
            const empty = document.createElement('div');
            empty.className = 'queue-empty';
            empty.textContent = 'EMPTY';
            listEl.appendChild(empty);
            return;
        }
        queue.forEach((type, i) => {
            const item = document.createElement('div');
            item.className = 'queue-item';
            item.appendChild(buildPieceEl(type, 14, false));
            item.addEventListener('click', () => removeFromQueue(i));
            listEl.appendChild(item);
        });
    }

    function appendToQueue(type) {
        queue.push(type);
        renderQueue();
        const listEl = document.getElementById('piece-queue');
        listEl.scrollTop = listEl.scrollHeight;
    }

    function removeFromQueue(i) {
        queue.splice(i, 1);
        renderQueue();
    }

    function renderPalette() {
        const palette = document.getElementById('piece-palette');
        palette.innerHTML = '';
        PIECE_TYPES.forEach(type => {
            const item = buildPieceEl(type, CELL);
            item.classList.add('palette-piece');
            item.dataset.pieceType = type;
            item.addEventListener('mousedown', e => { e.preventDefault(); startDrag(type, e.clientX, e.clientY); });
            palette.appendChild(item);
        });
    }

    function renderGarbagePicker() {
        const picker = document.getElementById('garbage-picker');
        picker.innerHTML = '';
        const row = buildGarbageEl(CELL);
        Array.from(row.children).forEach((cell, c) => {
            cell.style.cursor = 'pointer';
            cell.addEventListener('click', e => {
                e.stopPropagation();
                if (draggingGarbage) return;
                holeCol = c;
                renderGarbagePicker();
            });
        });
        row.addEventListener('mousedown', e => { e.preventDefault(); startDragGarbage(e.clientX, e.clientY); });
        picker.appendChild(row);
    }

    const getCellEl = (r, c) =>
        document.querySelector(`#tetris-board [data-row="${r}"][data-col="${c}"]`);

    function syncCellDOM(r, c) {
        const el = getCellEl(r, c);
        if (!el) return;
        const entry = matrix[r][c];
        if (entry) {
            el.dataset.piece = entry.type;
            if (entry.id < 0) el.dataset.drawn = '1'; else delete el.dataset.drawn;
        } else {
            delete el.dataset.piece;
            delete el.dataset.drawn;
        }
    }

    function clearHighlight() {
        hoverCells.forEach(([r, c]) => {
            const el = getCellEl(r, c);
            if (!el || !el.dataset.hover) return;
            const entry = matrix[r][c];
            if (entry) el.dataset.piece = entry.type; else delete el.dataset.piece;
            delete el.dataset.hover;
        });
        hoverCells = [];
        hoverAnchor = null;
    }

    function highlightDrop(type, anchorR, anchorC) {
        clearHighlight();
        const cells = getRotatedShape(type).map(([dr, dc]) => [anchorR + dr, anchorC + dc]);
        const valid = cells.every(([r, c]) => r >= 0 && r < ROWS && c >= 0 && c < COLS && !matrix[r][c]);
        const tag = valid ? 'ok' : 'bad';
        cells.forEach(([r, c]) => {
            if (r < 0 || r >= ROWS || c < 0 || c >= COLS) return;
            const el = getCellEl(r, c);
            if (!el) return;
            el.dataset.hover = tag;
            if (valid) el.dataset.piece = type;
        });
        hoverCells = cells.filter(([r, c]) => r >= 0 && r < ROWS && c >= 0 && c < COLS);
        hoverAnchor = { r: anchorR, c: anchorC };
    }

    function highlightGarbageRow(r) {
        clearHighlight();
        for (let c = 0; c < COLS; c++) {
            const el = getCellEl(r, c);
            if (!el) continue;
            el.dataset.hover = 'ok';
            if (c !== holeCol) el.dataset.piece = 'G';
        }
        hoverCells = Array.from({ length: COLS }, (_, c) => [r, c]);
        hoverAnchor = { r, c: 0 };
    }

    function setActiveTool(tool) {
        activeTool = tool;
        ['delete','draw','erase'].forEach(t =>
            document.getElementById('tool-' + t).classList.toggle('sort-active', t === tool)
        );
        document.getElementById('tool-warning').style.display =
            (tool === 'draw' || tool === 'erase') ? 'block' : 'none';
        document.getElementById('tetris-board').className = 'tetris-board tool-' + tool;
    }

    function drawCell(r, c) {
        if (matrix[r][c]) return;
        matrix[r][c] = { type: 'G', id: -1 };
        syncCellDOM(r, c);
    }

    function eraseCell(r, c) {
        const entry = matrix[r][c];
        if (!entry) return;
        if (entry.id >= 0) {
            const inst = instances[entry.id];
            if (inst) {
                inst.cells = inst.cells.filter(([pr, pc]) => !(pr === r && pc === c));
                if (!inst.cells.length) delete instances[entry.id];
            }
        }
        matrix[r][c] = null;
        syncCellDOM(r, c);
    }

    function handleBoardCell(r, c) {
        if (activeTool === 'draw') drawCell(r, c);
        else if (activeTool === 'erase') eraseCell(r, c);
        else if (activeTool === 'delete') {
            const entry = matrix[r][c];
            if (entry && entry.id >= 0) removePiece(entry.id);
        }
    }

    function spawnGhost(el, clientX, clientY) {
        ghost = el;
        Object.assign(ghost.style, { position: 'fixed', pointerEvents: 'none', opacity: '0.75', zIndex: '9999' });
        positionGhost(clientX, clientY);
        document.body.appendChild(ghost);
        document.body.style.cursor = 'grabbing';
    }

    const startDrag = (type, x, y) => { dragging = { type }; spawnGhost(buildPieceEl(type, CELL), x, y); };
    const startDragGarbage = (x, y) => { draggingGarbage = true; spawnGhost(buildGarbageEl(CELL), x, y); };

    function positionGhost(clientX, clientY) {
        if (!ghost) return;
        ghost.style.left = (clientX - CELL / 2) + 'px';
        ghost.style.top = (clientY - CELL / 2) + 'px';
    }

    function endDrag(clientX, clientY) {
        const el = document.elementFromPoint(clientX, clientY);
        if (el && el.closest('#piece-queue')) {
            appendToQueue(dragging.type);
            endDragCleanup();
            return;
        }
        const cellEl = el ? el.closest('[data-row]') : null;
        if (cellEl) {
            const r = +cellEl.dataset.row, c = +cellEl.dataset.col;
            const cells = getRotatedShape(dragging.type).map(([dr, dc]) => [r + dr, c + dc]);
            const valid = cells.every(([pr, pc]) => pr >= 0 && pr < ROWS && pc >= 0 && pc < COLS && !matrix[pr][pc]);
            if (valid) {
                const id = nextId++;
                instances[id] = { type: dragging.type, cells };
                cells.forEach(([pr, pc]) => { matrix[pr][pc] = { type: dragging.type, id }; });
            }
        }
        endDragCleanup();
        renderBoard();
    }

    function endDragGarbage(clientX, clientY) {
        const el = document.elementFromPoint(clientX, clientY);
        const cellEl = el ? el.closest('[data-row]') : null;
        if (cellEl) placeGarbage(+cellEl.dataset.row);
        else endDragCleanup();
    }

    function endDragCleanup() {
        clearHighlight();
        if (ghost) { ghost.remove(); ghost = null; }
        dragging = null;
        draggingGarbage = false;
        document.body.style.cursor = '';
    }

    function renderBoard() {
        document.getElementById('tetris-board').innerHTML =
            Array.from({ length: ROWS }, (_, r) =>
                `<div class="board-row">${Array.from({ length: COLS }, (_, c) => {
                    const entry = matrix[r][c];
                    const piece = entry ? ` data-piece="${entry.type}"` : '';
                    const drawn = entry && entry.id < 0 ? ' data-drawn="1"' : '';
                    return `<div class="board-cell" data-row="${r}" data-col="${c}"${piece}${drawn}></div>`;
                }).join('')}</div>`
            ).join('');
    }

    function removePiece(id) {
        const inst = instances[id];
        if (!inst) return;
        inst.cells.forEach(([r, c]) => { matrix[r][c] = null; });
        delete instances[id];
        renderBoard();
    }

    function placeGarbage(r) {
        for (let c = 0; c < COLS; c++) {
            const entry = matrix[r][c];
            if (entry && entry.id >= 0) {
                const inst = instances[entry.id];
                if (inst) {
                    inst.cells = inst.cells.filter(([pr]) => pr !== r);
                    if (!inst.cells.length) delete instances[entry.id];
                }
            }
        }
        const id = nextId++, cells = [];
        for (let c = 0; c < COLS; c++) {
            if (c === holeCol) { matrix[r][c] = null; }
            else { matrix[r][c] = { type: 'G', id }; cells.push([r, c]); }
        }
        instances[id] = { type: 'G', cells };
        endDragCleanup();
        renderBoard();
    }

    function clearBoard() {
        initMatrix();
        instances = {};
        nextId = 0;
        renderBoard();
    }

    function setStatus(msg, isError) {
        const el = document.getElementById('status-msg');
        el.textContent = msg;
        el.style.color = isError ? '#f00' : '#888';
    }

    function readJSON(id) {
        const el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : null;
    }

    function confirmBoard() {
        const puzzleId = readJSON('data-puzzle-id');
        const name = document.getElementById('board-name-input').value.trim() || 'UNTITLED';
        const btn = document.getElementById('btn-confirm');
        btn.disabled = true;
        btn.textContent = 'SAVING\u2026';
        setStatus('');
        const submitMatrix = matrix.map(row => row.map(cell => cell ? cell.type : null));
        fetch('/board/' + puzzleId + '/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, matrix: submitMatrix, queue }),
        })
        .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
        .then(() => {
            setStatus('SAVED', false);
            btn.textContent = 'SAVE';
            btn.disabled = false;
        })
        .catch(err => {
            console.error('[edit_board]', err);
            setStatus('ERROR', true);
            btn.textContent = 'SAVE';
            btn.disabled = false;
        });
    }

    function bindEvents() {
        const boardEl = document.getElementById('tetris-board');

        boardEl.addEventListener('mousedown', e => {
            if (dragging || draggingGarbage) return;
            const cellEl = e.target.closest('[data-row]');
            if (!cellEl) return;
            e.preventDefault();
            painting = true;
            handleBoardCell(+cellEl.dataset.row, +cellEl.dataset.col);
        });

        boardEl.addEventListener('mouseover', e => {
            if (!painting) return;
            const cellEl = e.target.closest('[data-row]');
            if (cellEl) handleBoardCell(+cellEl.dataset.row, +cellEl.dataset.col);
        });

        document.addEventListener('mouseup', e => {
            painting = false;
            if (draggingGarbage) { endDragGarbage(e.clientX, e.clientY); return; }
            if (dragging) endDrag(e.clientX, e.clientY);
        });

        document.addEventListener('mousemove', e => {
            if (!dragging && !draggingGarbage) return;
            positionGhost(e.clientX, e.clientY);
            const el = document.elementFromPoint(e.clientX, e.clientY);
            const cellEl = el ? el.closest('[data-row]') : null;
            if (cellEl) {
                const r = +cellEl.dataset.row, c = +cellEl.dataset.col;
                if (draggingGarbage) {
                    if (!hoverAnchor || hoverAnchor.r !== r) highlightGarbageRow(r);
                } else {
                    if (!hoverAnchor || hoverAnchor.r !== r || hoverAnchor.c !== c) highlightDrop(dragging.type, r, c);
                }
            } else {
                clearHighlight();
            }
        });

        ['delete','draw','erase'].forEach(t =>
            document.getElementById('tool-' + t).addEventListener('click', () => setActiveTool(t))
        );

        document.getElementById('btn-rotate-left').addEventListener('click', () => { rotation = (rotation+3)%4; renderPalette(); });
        document.getElementById('btn-rotate-right').addEventListener('click', () => { rotation = (rotation+1)%4; renderPalette(); });
        document.getElementById('btn-clear').addEventListener('click', clearBoard);
        document.getElementById('btn-confirm').addEventListener('click', confirmBoard);
    }

    function init() {
        initMatrix();
        const initialBoard = readJSON('data-board');
        if (initialBoard) {
            initialBoard.forEach((row, r) => {
                row.forEach((type, c) => {
                    if (type) matrix[r][c] = { type, id: -1 };
                });
            });
        }
        const initialQueue = readJSON('data-queue');
        if (initialQueue && initialQueue.length) {
            queue = initialQueue.slice();
        }
        renderBoard();
        renderPalette();
        renderGarbagePicker();
        renderQueue();
        bindEvents();
    }

    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', init)
        : init();
}());