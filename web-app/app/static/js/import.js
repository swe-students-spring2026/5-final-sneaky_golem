const uploadEl = document.getElementById('import-upload');
const processingEl = document.getElementById('import-processing');
const resultEl = document.getElementById('import-result');
const boardEl = document.getElementById('import-board');
const fileInput = document.getElementById('import-file');
const confirmBtn = document.getElementById('import-confirm');
const deleteBtn = document.getElementById('import-delete');

const ROWS = 20;
const COLS = 10;

let currentMatrix = null;

function show(el) { el.classList.remove('import-hidden'); }
function hide(el) { el.classList.add('import-hidden'); }

function renderBoard(matrix) {
    boardEl.innerHTML = '';
    for (let r = 0; r < ROWS; r++) {
        const row = document.createElement('div');
        row.className = 'board-row';
        for (let c = 0; c < COLS; c++) {
            const cell = document.createElement('div');
            cell.className = 'board-cell';
            const piece = matrix && matrix[r] && matrix[r][c];
            if (piece) cell.dataset.piece = piece;
            row.appendChild(cell);
        }
        boardEl.appendChild(row);
    }
}

function reset() {
    currentMatrix = null;
    fileInput.value = '';
    hide(resultEl);
    hide(processingEl);
    show(uploadEl);
}

fileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;

    hide(uploadEl);
    show(processingEl);

    const body = new FormData();
    body.append('image', file);

    fetch('/board/import', { method: 'POST', body })
        .then(function (res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.json();
        })
        .then(function (data) {
            currentMatrix = data.matrix;
            renderBoard(currentMatrix);
            hide(processingEl);
            show(resultEl);
        })
        .catch(function (err) {
            console.error('[import] Processing failed:', err);
            reset();
        });
});

confirmBtn.addEventListener('click', function () {
    if (!currentMatrix) return;
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'SAVING\u2026';

    fetch('/board/import/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matrix: currentMatrix }),
    })
        .then(function (res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            window.location.href = '/dashboard';
        })
        .catch(function (err) {
            console.error('[import] Confirm failed:', err);
            confirmBtn.textContent = 'ERROR';
            setTimeout(function () {
                confirmBtn.textContent = 'CONFIRM';
                confirmBtn.disabled = false;
            }, 2000);
        });
});

deleteBtn.addEventListener('click', reset);