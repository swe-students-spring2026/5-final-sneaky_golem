const input   = document.getElementById('import-file');
const wrap    = document.getElementById('import-preview-wrap');
const preview = document.getElementById('import-preview');
const confirm = document.getElementById('import-confirm');

input.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;
    preview.src = URL.createObjectURL(file);
    wrap.classList.add('import-preview-visible');
    confirm.disabled = false;
});