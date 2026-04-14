/* ============================================
   VIEW: Grid / List
   Render everything at once — IntersectionObserver lazy-loads images,
   so even ~700 cards stays light. No pagination.
   ============================================ */

window.ViewGrid = {
    isInitialized: false,
    currentMode: 'grid', // 'grid' | 'list'

    init(container) {
        this.container = container;
        this.grid = container.querySelector('.grid');
        this.loadMore = container.querySelector('.load-more');
        this.emptyState = container.querySelector('.empty-state');
        this.modeToggle = container.querySelector('.grid-mode-toggle');

        // Load-more button kept hidden — pagination removed per design.
        if (this.loadMore) this.loadMore.classList.remove('visible');

        this.modeToggle.addEventListener('click', e => {
            const btn = e.target.closest('.view-btn');
            if (!btn) return;
            const mode = btn.dataset.mode;
            if (mode === this.currentMode) return;
            this.currentMode = mode;
            this.modeToggle.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            this.render(APP.filtered);
        });

        this.isInitialized = true;
    },

    render(filtered) {
        this.grid.innerHTML = '';
        const frag = document.createDocumentFragment();
        filtered.forEach(release => frag.appendChild(APP.createCard(release)));
        this.grid.appendChild(frag);

        if (APP.observer) {
            this.grid.querySelectorAll('img[data-src]:not([src])').forEach(img => {
                APP.observer.observe(img);
            });
        }

        this.emptyState.classList.toggle('visible', filtered.length === 0);
        this.grid.className = this.currentMode === 'list' ? 'grid view-list' : 'grid';
        APP.updateResultCount();
    },

    destroy() {}
};
