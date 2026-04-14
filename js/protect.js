/* ============================================
   Light client-side deterrents:
   - disable right-click context menu
   - block common devtools / view-source shortcuts
   - disable text selection + image dragging
   Note: this is NOT real security — any determined user can still
   open DevTools or view the source. It just discourages casual inspection.
   ============================================ */
(function () {
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('dragstart', e => {
        if (e.target && e.target.tagName === 'IMG') e.preventDefault();
    });
    document.addEventListener('selectstart', e => {
        const t = e.target;
        if (t && t.closest && t.closest('input, textarea, [contenteditable]')) return;
        e.preventDefault();
    });
    document.addEventListener('keydown', e => {
        const k = e.key.toLowerCase();
        // F12
        if (e.key === 'F12') { e.preventDefault(); return; }
        // Ctrl/Cmd+Shift+I/J/C  → DevTools / console / inspector
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && ['i','j','c'].includes(k)) {
            e.preventDefault(); return;
        }
        // Ctrl/Cmd+U → view source
        if ((e.ctrlKey || e.metaKey) && k === 'u') { e.preventDefault(); return; }
        // Ctrl/Cmd+S → save page
        if ((e.ctrlKey || e.metaKey) && k === 's') { e.preventDefault(); return; }
    });
})();
