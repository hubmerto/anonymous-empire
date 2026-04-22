/* ============================================
   VIEW: Timeline
   3-tier, drill-down navigation:
     (1) Overview  — every release as a 1-wide stripe across the full range,
                     colored by its dominant color. Click / drag = jump.
     (2) Decades   — 1980s / 1990s / … segments. Click to zoom into a decade.
                     Click active decade again → zoom out.
     (3) Year cols — each year is a column with covers stacked upward.
                     Click a year's label to zoom into that single year.
   Zoom level grows the covers: all-time (small) → decade (medium) → year (big).
   ============================================ */

window.ViewTimeline = {
    isInitialized: false,
    yearColumns: {},
    columnObserver: null,
    _scrollRaf: null,
    _zoom: { mode: 'all', value: null },  // mode: 'all' | 'decade' | 'year'

    init(container) {
        this.container = container;

        this.container.innerHTML = `
            <div class="timeline-year-label"></div>
            <div class="timeline-nav">
                <div class="timeline-overview" title="All releases — click to jump">
                    <div class="timeline-overview-bars"></div>
                    <div class="timeline-viewport"></div>
                </div>
                <div class="timeline-decades"></div>
            </div>
            <div class="timeline-strip"></div>
        `;
        this.yearLabel   = this.container.querySelector('.timeline-year-label');
        this.overview    = this.container.querySelector('.timeline-overview');
        this.overviewBars = this.container.querySelector('.timeline-overview-bars');
        this.viewport    = this.container.querySelector('.timeline-viewport');
        this.decadesRow  = this.container.querySelector('.timeline-decades');
        this.strip       = this.container.querySelector('.timeline-strip');

        // Vertical wheel → horizontal scroll on the main strip.
        this.strip.addEventListener('wheel', e => {
            if (Math.abs(e.deltaX) < Math.abs(e.deltaY)) {
                e.preventDefault();
                this.strip.scrollLeft += e.deltaY;
            }
        }, { passive: false });

        // Main-strip scroll → update overview viewport + active decade + year label.
        this.strip.addEventListener('scroll', () => {
            if (this._scrollRaf) return;
            this._scrollRaf = requestAnimationFrame(() => {
                this._scrollRaf = null;
                this._syncNav();
            });
        });

        this.overview.addEventListener('click', e => this._jumpFromOverview(e));

        // Populate columns lazily as they enter the viewport.
        this.columnObserver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const year = parseInt(entry.target.dataset.year, 10);
                    this._populateColumn(entry.target, year);
                }
            });
        }, { root: this.strip, rootMargin: '0px 300px', threshold: 0.01 });

        this.isInitialized = true;
    },

    render(filtered) {
        // Reset strip + decades (keep the "All" button).
        this.strip.innerHTML = '';
        this.overviewBars.innerHTML = '';
        while (this.decadesRow.firstChild) this.decadesRow.removeChild(this.decadesRow.firstChild);
        this.yearColumns = {};

        const dated = filtered.filter(r => r.year && r.year > 0);
        if (dated.length === 0) {
            this.strip.innerHTML = '<div class="timeline-empty">No releases with year data.</div>';
            this.viewport.style.display = 'none';
            return;
        }
        this.viewport.style.display = '';

        dated.sort((a, b) => (a.year - b.year) || ((a.id || 0) - (b.id || 0)));
        const minYear = dated[0].year;
        const maxYear = dated[dated.length - 1].year;
        this.minYear = minYear;
        this.maxYear = maxYear;

        // ---- Tier 1: overview ---------------------------------------------
        const ovFrag = document.createDocumentFragment();
        dated.forEach(r => {
            const bar = document.createElement('div');
            bar.className = 'tl-ov-bar';
            bar.style.background = r.color || '#333';
            bar.dataset.year = r.year;
            bar.title = `${r.year} — ${r.artist}`;
            ovFrag.appendChild(bar);
        });
        this.overviewBars.appendChild(ovFrag);

        // ---- Tier 2: decades ----------------------------------------------
        const byYear = {};
        dated.forEach(r => (byYear[r.year] = byYear[r.year] || []).push(r));

        const decadeCounts = {};
        for (let y = minYear; y <= maxYear; y++) {
            const d = Math.floor(y / 10) * 10;
            decadeCounts[d] = (decadeCounts[d] || 0) + (byYear[y] ? byYear[y].length : 0);
        }
        const firstDecade = Math.floor(minYear / 10) * 10;
        const lastDecade  = Math.floor(maxYear / 10) * 10;

        for (let d = firstDecade; d <= lastDecade; d += 10) {
            const segStart = Math.max(d, minYear);
            const segEnd   = Math.min(d + 9, maxYear);
            const span     = segEnd - segStart + 1;
            const seg = document.createElement('button');
            seg.type = 'button';
            seg.className = 'tl-decade';
            seg.dataset.decade = d;
            seg.style.flex = `${span} 0 0`;
            seg.innerHTML = `
                <span class="tl-decade-label">${d}s</span>
                <span class="tl-decade-count">${decadeCounts[d] || 0}</span>
            `;
            seg.addEventListener('click', () => {
                if (this._zoom.mode === 'decade' && this._zoom.value === d) {
                    this._setZoom({ mode: 'all', value: null });
                } else {
                    this._setZoom({ mode: 'decade', value: d });
                }
            });
            this.decadesRow.appendChild(seg);
        }

        // ---- Tier 3: year columns -----------------------------------------
        const stripFrag = document.createDocumentFragment();
        for (let y = minYear; y <= maxYear; y++) {
            const col = document.createElement('div');
            col.className = 'tl-column';
            col.dataset.year = y;

            const releasesForYear = byYear[y] || [];
            col.dataset.count = releasesForYear.length;
            if (releasesForYear.length === 0) col.classList.add('tl-column--empty');

            const covers = document.createElement('div');
            covers.className = 'tl-covers';
            col.appendChild(covers);

            // Year label under every column — clickable to zoom into that year.
            const label = document.createElement('button');
            label.type = 'button';
            label.className = 'tl-year';
            if (y % 10 === 0) label.classList.add('tl-year--decade');
            label.textContent = y;
            label.addEventListener('click', () => {
                if (this._zoom.mode === 'year' && this._zoom.value === y) {
                    // Already zoomed to this year → step back to its decade.
                    this._setZoom({ mode: 'decade', value: Math.floor(y / 10) * 10 });
                } else {
                    this._setZoom({ mode: 'year', value: y });
                }
            });
            col.appendChild(label);

            stripFrag.appendChild(col);
            this.yearColumns[y] = {
                el: col, covers, data: releasesForYear, populated: false,
            };
            this.columnObserver.observe(col);
        }
        this.strip.appendChild(stripFrag);

        // Apply current zoom state (all by default on fresh render).
        this._setZoom(this._zoom || { mode: 'all', value: null }, { preserveScroll: false });

        window.removeEventListener('resize', this._resizeHandler);
        this._resizeHandler = () => this._sizeThumbs();
        window.addEventListener('resize', this._resizeHandler);
    },

    // ---- Zoom -----------------------------------------------------------

    _setZoom(zoom, opts = {}) {
        this._zoom = zoom;
        const { mode, value } = zoom;

        const visibleForYear = (y) => {
            if (mode === 'all') return true;
            if (mode === 'decade') return Math.floor(y / 10) * 10 === value;
            if (mode === 'year') return y === value;
            return true;
        };

        // Show / hide columns (keep empty ones visible in 'all' and 'decade' so the
        // timeline reads as continuous time; hide them in single-year zoom).
        for (const y in this.yearColumns) {
            const col = this.yearColumns[y].el;
            const show = visibleForYear(+y);
            col.style.display = show ? '' : 'none';
        }

        // Mark decade buttons active.
        const activeDecade = mode === 'decade' ? value
                           : mode === 'year'   ? Math.floor(value / 10) * 10
                           : null;
        this.decadesRow.querySelectorAll('.tl-decade').forEach(seg => {
            const d = seg.dataset.decade ? parseInt(seg.dataset.decade, 10) : null;
            seg.classList.toggle('active', d === activeDecade);
        });

        // Mark year labels active.
        for (const y in this.yearColumns) {
            const lbl = this.yearColumns[y].el.querySelector('.tl-year');
            if (lbl) lbl.classList.toggle('active', mode === 'year' && +y === value);
        }

        // Flex-fill columns when zoomed so each cover grows.
        this.strip.classList.toggle('zoomed', mode !== 'all');
        this.strip.classList.toggle('zoomed-year', mode === 'year');

        this._sizeThumbs();

        // Scroll into the zoomed range.
        if (!opts.preserveScroll) {
            if (mode === 'all') {
                this.strip.scrollLeft = 0;
            } else {
                const targetYear = mode === 'year' ? value : value; // decade first year
                const col = this.yearColumns[targetYear]?.el;
                if (col) {
                    this.strip.scrollLeft = Math.max(0, col.offsetLeft - 8);
                }
            }
        }

        this._syncNav();
    },

    _sizeThumbs() {
        // Available vertical space for covers inside a column.
        const stripH = this.strip.clientHeight;
        const labelReserve = 28; // year label
        const avail = Math.max(60, stripH - labelReserve);

        // Densest *visible* year determines how small thumbs must shrink.
        let maxCount = 0;
        let visibleCols = 0;
        for (const y in this.yearColumns) {
            const info = this.yearColumns[y];
            if (info.el.style.display === 'none') continue;
            visibleCols++;
            if (info.data.length > maxCount) maxCount = info.data.length;
        }
        maxCount = Math.max(1, maxCount);

        // In single-year zoom, we can wrap into multiple rows inside the column,
        // so size the thumb by available width split into a comfy grid.
        if (this._zoom.mode === 'year' && visibleCols === 1) {
            const stripW = this.strip.clientWidth;
            const cols = Math.max(4,
                Math.ceil(Math.sqrt(maxCount * (stripW / Math.max(1, avail)))));
            const size = Math.max(60, Math.min(180,
                Math.floor((stripW - (cols + 1) * 2) / cols)));
            this.strip.style.setProperty('--tl-thumb-size', `${size}px`);
            return;
        }

        const gap = 1;
        // Height-constrained: fit all covers of the densest year stacked upward.
        const sizeByH = Math.floor((avail - (maxCount - 1) * gap) / maxCount);
        // Width-constrained: don't overflow column width either.
        const stripW = this.strip.clientWidth;
        const sizeByW = visibleCols ? Math.floor(stripW / visibleCols) - 4 : 56;

        // Per-tier clamps: sizes must fit, but the tier sets the upper bound
        // so zoom levels are visually distinct.
        const [min, max] =
            this._zoom.mode === 'all'    ? [4, 120] :
            this._zoom.mode === 'decade' ? [16, 160] :
                                           [40, 200];
        let size = Math.min(sizeByH, sizeByW);
        size = Math.max(min, Math.min(max, size));
        this.strip.style.setProperty('--tl-thumb-size', `${size}px`);
    },

    // ---- Column population ---------------------------------------------

    _populateColumn(colEl, year) {
        const info = this.yearColumns[year];
        if (!info || info.populated) return;
        info.populated = true;

        info.data.forEach(r => {
            const thumb = document.createElement('div');
            thumb.className = 'tl-thumb';
            thumb.addEventListener('click', () => APP.openOverlay(r));

            const rawSrc = r.image || r.thumb;
            const imgSrc = rawSrc && !/^(https?:)?\/\//.test(rawSrc) && rawSrc[0] !== '/' ? '/' + rawSrc : rawSrc;
            if (imgSrc) {
                const img = document.createElement('img');
                img.setAttribute('data-src', imgSrc);
                img.alt = `${r.artist} — ${r.title}`;
                thumb.appendChild(img);
                if (APP.observer) APP.observer.observe(img);
            }
            info.covers.appendChild(thumb);
        });
    },

    // ---- Navigation sync ------------------------------------------------

    _syncNav() {
        if (!this.minYear) return;

        // Viewport indicator: the *full-range* rectangle that the visible slice
        // of the main strip corresponds to. Computed from the visible year
        // columns' offsetLeft within the strip vs the overview's full range.
        const totalYears = this.maxYear - this.minYear + 1;
        const viewW = this.strip.clientWidth;
        const scroll = this.strip.scrollLeft;
        const ovW = this.overview.clientWidth;

        // Which years are currently on-screen?
        let firstVisibleYear = null, lastVisibleYear = null;
        for (const y in this.yearColumns) {
            const col = this.yearColumns[y].el;
            if (col.style.display === 'none') continue;
            const left = col.offsetLeft;
            const right = left + col.offsetWidth;
            if (right >= scroll && left <= scroll + viewW) {
                if (firstVisibleYear === null) firstVisibleYear = +y;
                lastVisibleYear = +y;
            }
        }
        if (firstVisibleYear !== null) {
            const leftRatio = (firstVisibleYear - this.minYear) / totalYears;
            const widthRatio = ((lastVisibleYear - firstVisibleYear + 1)) / totalYears;
            this.viewport.style.left  = (leftRatio * ovW) + 'px';
            this.viewport.style.width = (Math.max(0.01, widthRatio) * ovW) + 'px';
        }

        // Center year for the big label.
        const centerX = scroll + viewW / 2;
        let centerYear = firstVisibleYear ?? this.minYear;
        for (const y in this.yearColumns) {
            const col = this.yearColumns[y].el;
            if (col.style.display === 'none') continue;
            if (col.offsetLeft <= centerX && col.offsetLeft + col.offsetWidth >= centerX) {
                centerYear = +y;
                break;
            }
        }
        if (this.yearLabel) this.yearLabel.textContent = centerYear;
    },

    _jumpFromOverview(e) {
        const rect = this.overview.getBoundingClientRect();
        const ratio = (e.clientX - rect.left) / rect.width;
        // Map ratio → year in [min, max], then find that column.
        const totalYears = this.maxYear - this.minYear + 1;
        const targetYear = Math.floor(this.minYear + ratio * totalYears);
        const col = this.yearColumns[targetYear]?.el || this.yearColumns[this._nearestYear(targetYear)]?.el;
        if (col) this.strip.scrollTo({ left: Math.max(0, col.offsetLeft - 8), behavior: 'smooth' });
    },

    _nearestYear(year) {
        let nearest = null, best = Infinity;
        for (const y of Object.keys(this.yearColumns).map(Number)) {
            const d = Math.abs(y - year);
            if (d < best) { best = d; nearest = y; }
        }
        return nearest;
    },

    destroy() {
        if (this.columnObserver) this.columnObserver.disconnect();
    },
};
