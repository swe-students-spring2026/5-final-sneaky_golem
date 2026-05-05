(function () {
    'use strict';

    const PAGE_SIZE = 10;
    const ROWS = 20;
    const COLS = 10;

    let puzzleId = null;
    let board = null;
    let solutions = [];
    let activeSolution = null;
    let currentStep = 0;
    let sortMode = 'date';
    let currentPage = 1;

    function readJSON(id) {
        const el = document.getElementById(id);
        if (!el) return null;
        return JSON.parse(el.textContent.replace(/'/g, '"'));
    }

    function totalPages() {
        return Math.max(1, Math.ceil(solutions.length / PAGE_SIZE));
    }

    function pagedSolutions() {
        const start = (currentPage - 1) * PAGE_SIZE;
        return solutions.slice(start, start + PAGE_SIZE);
    }

    function escapeHtml(str) {
        const node = document.createElement('span');
        node.textContent = String(str);
        return node.innerHTML;
    }

    function formatDate(isoStr) {
        const d = new Date(isoStr);
        return d
            .toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
            .toUpperCase();
    }

    function renderBoard(matrix) {
        while(matrix.length > 20){
            matrix.shift();
        }
        const boardEl = document.getElementById('tetris-board');
        boardEl.innerHTML = '';

        for (let r = 0; r < ROWS; r++) {
            const rowEl = document.createElement('div');
            rowEl.className = 'board-row';

            for (let c = 0; c < COLS; c++) {
                const cell = document.createElement('div');
                cell.className = 'board-cell';

                const piece = matrix && matrix[r] && matrix[r][c];
                if (piece) {
                    cell.dataset.piece = piece;
                }

                rowEl.appendChild(cell);
            }

            boardEl.appendChild(rowEl);
        }
    }

    function renderStepCounter() {
        const counter = document.getElementById('step-counter');
        const btnFirst = document.getElementById('btn-first');
        const btnPrev = document.getElementById('btn-prev');
        const btnNext = document.getElementById('btn-next');
        const btnLast = document.getElementById('btn-last');

        const steps = activeSolution && activeSolution.steps;

        if (!steps || steps.length === 0) {
            counter.textContent = 'STEP \u2014 / \u2014';
            btnFirst.disabled = true;
            btnPrev.disabled = true;
            btnNext.disabled = true;
            btnLast.disabled = true;
            return;
        }

        const total = steps.length;
        counter.textContent = `STEP ${currentStep + 1} / ${total}`;
        btnFirst.disabled = currentStep === 0;
        btnPrev.disabled = currentStep === 0;
        btnNext.disabled = currentStep === total - 1;
        btnLast.disabled = currentStep === total - 1;
    }

    function goToStep(index) {
        if (!activeSolution || !activeSolution.steps || activeSolution.steps.length === 0) return;
        const total = activeSolution.steps.length;
        currentStep = Math.max(0, Math.min(index, total - 1));
        renderBoard(activeSolution.steps[currentStep]);
        renderStepCounter();
    }

    function goFirst() { goToStep(0); }
    function goPrev() { goToStep(currentStep - 1); }
    function goNext() { goToStep(currentStep + 1); }
    function goLast() {
        if (activeSolution && activeSolution.steps) {
            goToStep(activeSolution.steps.length - 1);
        }
    }

    function renderSolutionList() {
        const listEl = document.getElementById('solution-list');
        listEl.innerHTML = '';

        const paged = pagedSolutions();

        if (paged.length === 0) {
            const empty = document.createElement('div');
            empty.style.cssText = 'color:#888; font-size:12px; letter-spacing:2px; padding:16px 0;';
            empty.textContent = 'NO SOLUTIONS YET';
            listEl.appendChild(empty);
            renderPagination();
            return;
        }

        paged.forEach(function (sol) {
            const item = document.createElement('div');
            item.className = 'solution-item';

            const isActive = activeSolution && sol._id === activeSolution._id;
            if (isActive) item.classList.add('solution-active');

            item.innerHTML =
                `<div>${escapeHtml(sol.solution_name)}</div>` +
                `<div class="solution-meta">` +
                `${escapeHtml(sol.author_username)} &bull; ` +
                `${escapeHtml(sol.like_count)} &#9829; &bull; ` +
                `${formatDate(sol.created_at)}` +
                `</div>`;

            item.addEventListener('click', function () {
                console.log("WOKR")
                setActiveSolution(sol._id);
            });

            listEl.appendChild(item);
        });

        renderPagination();
    }

    function renderPagination() {
        const counter = document.getElementById('page-counter');
        const btnPrev = document.getElementById('page-prev');
        const btnNext = document.getElementById('page-next');
        const total = totalPages();

        counter.textContent = `${currentPage} / ${total}`;
        btnPrev.disabled = currentPage === 1;
        btnNext.disabled = currentPage === total;
    }

    function setActiveSolution(solutionId) {
        fetch(`/solution/${solutionId}`)
            .then(function (res) {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(function (data) {
                activeSolution = data;
                currentStep = 0;
                console.log(activeSolution)

                if (activeSolution.steps && activeSolution.steps.length > 0) {
                    renderBoard(activeSolution.steps[0]);
                } else {
                    renderBoard(activeSolution.final_board || board);
                }

                renderStepCounter();
                renderSolutionList();
            })
            .catch(function (err) {
                console.error('[saved_board] Failed to load solution:', err);
            });
    }

    function sortSolutions() {
        if (sortMode === 'likes') {
            solutions.sort(function (a, b) {
                return b.like_count - a.like_count;
            });
        } else {
            solutions.sort(function (a, b) {
                return new Date(b.created_at) - new Date(a.created_at);
            });
        }
    }

    function setSort(mode) {
        sortMode = mode;

        document.getElementById('sort-date').classList.toggle('sort-active', mode === 'date');
        document.getElementById('sort-likes').classList.toggle('sort-active', mode === 'likes');

        sortSolutions();
        currentPage = 1;
        renderSolutionList();
    }

    function setPage(n) {
        currentPage = Math.max(1, Math.min(n, totalPages()));
        renderSolutionList();
    }

    function renameBoard() {
        const input = document.getElementById('board-name-input');
        const newName = input.value.trim();
        if (!newName) return;

        const btn = document.getElementById('rename-btn');
        btn.disabled = true;
        btn.textContent = 'SAVING\u2026';

        fetch(`/board/${puzzleId}/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName }),
        })
            .then(function (res) {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(function () {
                const titleEl = document.querySelector('.page-title');
                if (titleEl) titleEl.textContent = newName;
                document.title = newName;

                btn.textContent = 'RENAMED \u2713';
                setTimeout(function () {
                    btn.textContent = 'RENAME';
                    btn.disabled = false;
                }, 2000);
            })
            .catch(function (err) {
                console.error('[saved_board] Rename failed:', err);
                btn.textContent = 'ERROR';
                setTimeout(function () {
                    btn.textContent = 'RENAME';
                    btn.disabled = false;
                }, 2000);
            });
    }

    function bindEvents() {
        document.getElementById('btn-first').addEventListener('click', goFirst);
        document.getElementById('btn-prev').addEventListener('click', goPrev);
        document.getElementById('btn-next').addEventListener('click', goNext);
        document.getElementById('btn-last').addEventListener('click', goLast);

        document.getElementById('sort-date').addEventListener('click', function () { setSort('date'); });
        document.getElementById('sort-likes').addEventListener('click', function () { setSort('likes'); });

        document.getElementById('page-prev').addEventListener('click', function () { setPage(currentPage - 1); });
        document.getElementById('page-next').addEventListener('click', function () { setPage(currentPage + 1); });

        document.getElementById('rename-btn').addEventListener('click', renameBoard);
        document.getElementById('board-name-input').addEventListener('keydown', function (e) {
            if (e.key === 'Enter') renameBoard();
        });
    }

    function init() {
        puzzleId = readJSON('data-puzzle-id');
        board = readJSON('data-board');
        solutions = readJSON('data-solutions') || [];
        activeSolution = readJSON('data-active-solution');

        sortSolutions();

        if (activeSolution && activeSolution.steps && activeSolution.steps.length > 0) {
            renderBoard(activeSolution.steps[0]);
        } else if (activeSolution && activeSolution.final_board) {
            renderBoard(activeSolution.final_board);
        } else {
            renderBoard(board);
        }

        renderStepCounter();
        renderSolutionList();
        bindEvents();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

}());
