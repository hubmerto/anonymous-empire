/* ============================================
   TECHNO VISUAL ARCHIVE — App
   Orchestrator: data, filters, view switching.
   ============================================ */

const APP = {
    data: null,
    filtered: [],
    currentView: 'grid',
    observer: null,
    searchTimeout: null,
    views: {
        grid: window.ViewGrid,
        timeline: window.ViewTimeline,
        map: window.ViewMap,
        color: window.ViewColor,
    },
};

// --- Init ---
async function init() {
    try {
        const resp = await fetch('/data/releases.json?v=' + Date.now());
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        APP.data = await resp.json();
    } catch (err) {
        document.getElementById('loading').textContent =
            'Could not load data. Run the collection script first.';
        console.error('Failed to load releases.json:', err);
        return;
    }

    populateFilters();
    updateStats();
    setupLazyLoading();
    setupEventListeners();

    // Read initial view from hash
    const hash = location.hash.replace('#', '');
    if (APP.views[hash]) {
        APP.currentView = hash;
    }

    // Init and activate starting view
    switchView(APP.currentView);
    applyFilters();

    document.getElementById('loading').classList.add('hidden');
}

// --- Populate filter dropdowns ---
function populateFilters() {
    const releases = APP.data.releases;

    const scenes = [...new Set(releases.map(r => r.scene))].sort();
    const sceneSelect = document.getElementById('filter-scene');
    scenes.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        sceneSelect.appendChild(opt);
    });

    const labels = [...new Set(releases.map(r => r.label))].sort();
    const labelSelect = document.getElementById('filter-label');
    labels.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        labelSelect.appendChild(opt);
    });
}

// --- Update header stats ---
function updateStats() {
    const meta = APP.data.meta;
    const t = document.getElementById('stat-total');
    const l = document.getElementById('stat-labels');
    const r = document.getElementById('stat-range');
    if (t) t.textContent = `${meta.total.toLocaleString()} releases`;
    if (l) l.textContent = `${meta.labels} labels`;
    if (r) r.textContent = `${meta.year_range[0]}–${meta.year_range[1]}`;
}

// --- View switching ---
function switchView(viewName) {
    const view = APP.views[viewName];
    if (!view) return;

    APP.currentView = viewName;
    // Keep URL clean — views stay under /library/ without hash suffixes.

    // Update tabs (legacy) + nav links
    document.querySelectorAll('.view-tab, .site-nav-links a[data-view]').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.view === viewName);
    });

    // Show/hide containers
    document.querySelectorAll('.view-container').forEach(vc => {
        vc.classList.toggle('active', vc.id === `view-${viewName}`);
    });

    // Lazy init the view
    const container = document.getElementById(`view-${viewName}`);
    if (!view.isInitialized) {
        view.init(container);
    }

    // Re-render with current filter
    if (APP.data) view.render(APP.filtered);
}

// --- Apply filters ---
function applyFilters() {
    const search = document.getElementById('search').value.toLowerCase().trim();
    const scene = document.getElementById('filter-scene').value;
    const label = document.getElementById('filter-label').value;
    const decade = document.getElementById('filter-decade').value;

    APP.filtered = APP.data.releases.filter(r => {
        if (scene && r.scene !== scene) return false;
        if (label && r.label !== label) return false;
        if (decade) {
            const d = parseInt(decade);
            if (r.year < d || r.year >= d + 10) return false;
        }
        if (search) {
            const haystack = `${r.artist} ${r.title} ${r.label} ${r.catno}`.toLowerCase();
            if (!haystack.includes(search)) return false;
        }
        return true;
    });

    // Render active view
    const view = APP.views[APP.currentView];
    if (view && view.isInitialized) {
        view.render(APP.filtered);
    }

    updateResultCount();
    updateActiveFilters();
}

// --- Create a release card ---
APP.createCard = function(release, compact) {
    const card = document.createElement('div');
    card.className = 'release-card';
    if (compact) card.classList.add('compact');
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');

    const rawSrc = release.image || release.thumb;
    const imgSrc = rawSrc && !/^(https?:)?\/\//.test(rawSrc) && rawSrc[0] !== '/' ? '/' + rawSrc : rawSrc;
    if (imgSrc) {
        const img = document.createElement('img');
        img.setAttribute('data-src', imgSrc);
        img.alt = `${release.artist} — ${release.title}`;
        img.loading = 'lazy';
        card.appendChild(img);
    } else {
        const ph = document.createElement('div');
        ph.className = 'placeholder';
        ph.textContent = release.catno || release.title;
        card.appendChild(ph);
    }

    const info = document.createElement('div');
    info.className = 'card-info';
    info.innerHTML = `
        <div class="card-artist">${escapeHtml(release.artist)}</div>
        <div class="card-title">${escapeHtml(release.title)}</div>
        <div class="card-meta">${release.label} · ${release.year || '—'}</div>
    `;
    card.appendChild(info);

    card.addEventListener('click', () => APP.openOverlay(release));
    card.addEventListener('keydown', e => {
        if (e.key === 'Enter') APP.openOverlay(release);
    });

    return card;
};

// --- Detail overlay ---
// Build a Discogs search URL from artist/title/catno — lands on the release page
// when there's an exact match, otherwise on scoped search results.
APP.discogsUrl = function(release) {
    if (release.discogs_url) return release.discogs_url;
    const params = new URLSearchParams();
    const q = [release.artist, release.title].filter(Boolean).join(' ').trim();
    if (q) params.set('q', q);
    if (release.catno) params.set('catno', release.catno);
    params.set('type', 'release');
    return 'https://www.discogs.com/search/?' + params.toString();
};

APP.openOverlay = function(release) {
    const overlay = document.getElementById('overlay');
    const body = document.getElementById('overlay-body');

    // Track position within the currently filtered list for arrow-key navigation.
    APP.currentRelease = release;
    APP.currentReleaseIdx = APP.filtered.indexOf(release);

    const rawThumb = release.image || release.thumb || '';
    const thumbUrl = rawThumb && !/^(https?:)?\/\//.test(rawThumb) && rawThumb[0] !== '/' ? '/' + rawThumb : rawThumb;
    const discogsHref = APP.discogsUrl(release);

    // Color swatches
    let colorHtml = '';
    if (release.colors && release.colors.length > 0) {
        const swatches = release.colors.map(c =>
            `<div class="overlay-swatch" style="background:${c}" title="${c}"></div>`
        ).join('');
        colorHtml = `<div class="overlay-colors">${swatches}</div>`;
    }

    body.innerHTML = `
        <a class="overlay-image" href="${discogsHref}" target="_blank" rel="noopener" title="View on Discogs">
            ${thumbUrl ? `<img src="${thumbUrl}" alt="${escapeHtml(release.title)}" id="overlay-img">` : '<span style="color: var(--text-muted)">No image</span>'}
        </a>
        <div class="overlay-details">
            <h2>${escapeHtml(release.title)}</h2>
            <div class="overlay-artist">${escapeHtml(release.artist)}</div>
            <div class="overlay-meta">
                <div class="overlay-meta-item">
                    <label>Label</label>
                    <span>${escapeHtml(release.label)}</span>
                </div>
                <div class="overlay-meta-item">
                    <label>Year</label>
                    <span>${release.year || '—'}</span>
                </div>
                <div class="overlay-meta-item">
                    <label>Catalog</label>
                    <span>${escapeHtml(release.catno || '—')}</span>
                </div>
                <div class="overlay-meta-item">
                    <label>Scene</label>
                    <span>${escapeHtml(release.scene)}</span>
                </div>
                <div class="overlay-meta-item">
                    <label>Format</label>
                    <span>${escapeHtml(release.format || '—')}</span>
                </div>
            </div>
            ${colorHtml}
            <div class="overlay-link">
                <a href="${discogsHref}" target="_blank" rel="noopener">View on Discogs →</a>
            </div>
        </div>
    `;

    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';

};

function closeOverlay() {
    document.getElementById('overlay').classList.remove('open');
    document.body.style.overflow = '';
}

// --- Active filter tags ---
function updateActiveFilters() {
    const container = document.getElementById('active-filters');
    container.innerHTML = '';

    const filters = [
        { id: 'filter-scene', label: 'Scene' },
        { id: 'filter-label', label: 'Label' },
        { id: 'filter-decade', label: 'Decade' },
    ];

    filters.forEach(f => {
        const el = document.getElementById(f.id);
        if (el.value) {
            const tag = document.createElement('span');
            tag.className = 'filter-tag';
            const display = f.id === 'filter-decade' ? `${el.value}s` : el.value;
            tag.innerHTML = `${f.label}: ${escapeHtml(display)} <button data-clear="${f.id}">&times;</button>`;
            container.appendChild(tag);
        }
    });

    const search = document.getElementById('search').value.trim();
    if (search) {
        const tag = document.createElement('span');
        tag.className = 'filter-tag';
        tag.innerHTML = `Search: "${escapeHtml(search)}" <button data-clear="search">&times;</button>`;
        container.appendChild(tag);
    }

    container.querySelectorAll('button[data-clear]').forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.clear;
            if (target === 'search') {
                document.getElementById('search').value = '';
            } else {
                document.getElementById(target).value = '';
            }
            applyFilters();
        });
    });
}

// --- Result count ---
APP.updateResultCount = function() { updateResultCount(); };
function updateResultCount() {
    const el = document.getElementById('result-count');
    el.textContent = `${APP.filtered.length.toLocaleString()} releases`;
}

// --- Lazy loading ---
function setupLazyLoading() {
    APP.observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const src = img.getAttribute('data-src');
                if (src) {
                    img.src = src;
                    img.onload = () => img.classList.add('loaded');
                    img.onerror = () => {
                        img.style.display = 'none';
                        const ph = document.createElement('div');
                        ph.className = 'placeholder';
                        ph.textContent = img.alt || '—';
                        img.parentNode.appendChild(ph);
                    };
                    img.removeAttribute('data-src');
                }
                APP.observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '200px',
        threshold: 0.01,
    });
}

// --- Event listeners ---
function setupEventListeners() {
    // Search (debounced)
    document.getElementById('search').addEventListener('input', () => {
        clearTimeout(APP.searchTimeout);
        APP.searchTimeout = setTimeout(applyFilters, 250);
    });

    // Filters
    ['filter-scene', 'filter-label', 'filter-decade'].forEach(id => {
        document.getElementById(id).addEventListener('change', applyFilters);
    });

    // View tabs + nav links
    document.querySelectorAll('.view-tab, .site-nav-links a[data-view]').forEach(tab => {
        tab.addEventListener('click', (e) => {
            if (tab.tagName === 'A') e.preventDefault();
            switchView(tab.dataset.view);
        });
    });

    // Overlay close
    document.getElementById('overlay-close').addEventListener('click', closeOverlay);
    document.getElementById('overlay-backdrop').addEventListener('click', closeOverlay);

    // Keyboard shortcuts
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeOverlay();

        // Arrow navigation within the open overlay (works even when focus is nowhere useful).
        const overlayOpen = document.getElementById('overlay').classList.contains('open');
        if (overlayOpen && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            e.preventDefault();
            navigateOverlay(e.key === 'ArrowRight' ? 1 : -1);
            return;
        }

        if (document.activeElement.tagName === 'INPUT') return;
        if (e.key === '/') { e.preventDefault(); document.getElementById('search').focus(); }
        if (e.key === '1') switchView('grid');
        if (e.key === '2') switchView('timeline');
        if (e.key === '3') switchView('map');
        if (e.key === '4') switchView('color');
    });
}

function navigateOverlay(dir) {
    if (!APP.filtered.length) return;
    let idx = APP.currentReleaseIdx;
    if (idx === undefined || idx < 0) idx = 0;
    idx = (idx + dir + APP.filtered.length) % APP.filtered.length;
    APP.openOverlay(APP.filtered[idx]);
}

// --- Util ---
APP.escapeHtml = escapeHtml;
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// --- Boot ---
document.addEventListener('DOMContentLoaded', init);
