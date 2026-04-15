/* ============================================
   VIEW: Color
   Full-screen mosaic of covers ordered by color.
   Sort order: chromatic first, hue 0 → 360 (red→orange→yellow→
   green→cyan→blue→purple→pink), then achromatic dark → light.
   Within a hue, dark → light; within achromatic, dark → light.
   ============================================ */

window.ViewColor = {
    isInitialized: false,

    // Rainbow order (red → purple), then black, then white.
    // Order in this array == order on the spectrum bar and in the mosaic.
    BUCKETS: [
        { idx: 0,  label: 'red',     hue: 0   },
        { idx: 1,  label: 'orange',  hue: 30  },
        { idx: 2,  label: 'amber',   hue: 60  },
        { idx: 3,  label: 'yellow',  hue: 90  },
        { idx: 4,  label: 'green',   hue: 130 },
        { idx: 5,  label: 'teal',    hue: 170 },
        { idx: 6,  label: 'cyan',    hue: 195 },
        { idx: 7,  label: 'blue',    hue: 225 },
        { idx: 8,  label: 'indigo',  hue: 255 },
        { idx: 9,  label: 'magenta', hue: 315 },
        { idx: 10, label: 'pink',    hue: 340 },
        { idx: 11, label: 'purple',  hue: 285 },
        { idx: 12, label: 'dark',    hue: null, tone: 'dark'  },
        { idx: 13, label: 'light',   hue: null, tone: 'light' },
    ],
    LIGHT_L_THRESHOLD: 55,

    init(container) {
        this.container = container;
        container.innerHTML = `
            <div class="color-spectrum"></div>
            <div class="color-mosaic"></div>
            <div class="color-empty empty-state">
                <p>No releases with color data.</p>
            </div>
        `;
        this.spectrum   = container.querySelector('.color-spectrum');
        this.mosaic     = container.querySelector('.color-mosaic');
        this.emptyState = container.querySelector('.color-empty');
        this.isInitialized = true;
    },

    render(filtered) {
        // Sort by sort_hue (chromatic 0..360, then achromatic -1..0 by lightness).
        // Chromatic tier: by hue, then lightness (dark → light) within a hue slice.
        // Achromatic tier: follow the same dark → light rule via sort_hue (-1 + l/100).
        const sorted = [...filtered].sort((a, b) => {
            const ka = this._sortKey(a);
            const kb = this._sortKey(b);
            for (let i = 0; i < ka.length; i++) {
                if (ka[i] !== kb[i]) return ka[i] - kb[i];
            }
            return 0;
        });

        // Count per bucket for spectrum widths.
        const bucketCounts = new Array(14).fill(0);
        const bucketFirstIdx = new Array(14).fill(-1);
        sorted.forEach((r, i) => {
            const bi = this._bucketOf(r);
            bucketCounts[bi]++;
            if (bucketFirstIdx[bi] === -1) bucketFirstIdx[bi] = i;
        });

        this._buildSpectrum(bucketCounts, bucketFirstIdx);
        this._renderMosaic(sorted);

        this.emptyState.classList.toggle('visible', sorted.length === 0);
        APP.updateResultCount();
    },

    // ---- Sort & bucket --------------------------------------------------

    // Sort hue is pre-computed by scripts/extract_colors.py using a
    // chroma-weighted palette scan: -1..0 = achromatic (by lightness),
    // 0..360 = chromatic hue. Trust it.
    // Order: rainbow (red → purple), then black (dark tier), then white (light tier).
    // _bucketOf returns the rainbow-ordered index; we sort primarily by that,
    // then by hue within the bucket (for smooth transitions), then by lightness.
    _sortKey(r) {
        const hue = (typeof r.sort_hue === 'number') ? r.sort_hue : null;
        const l = (r.hsl && typeof r.hsl.l === 'number') ? r.hsl.l : 0;
        const bi = this._bucketOf(r);
        const isAchromatic = (hue === null || hue < 0);
        if (isAchromatic) {
            // Dark tier: black (low L) first, lighter darks next.
            // Light tier: less-light first, pure white last.
            return [bi, l, 0];
        }
        return [bi, hue, l];
    },

    _bucketOf(r) {
        const hue = (typeof r.sort_hue === 'number') ? r.sort_hue : null;
        const l = (r.hsl && typeof r.hsl.l === 'number') ? r.hsl.l : 0;
        if (hue === null || hue < 0) {
            return l >= this.LIGHT_L_THRESHOLD ? 13 : 12;
        }
        // Rainbow-ordered bucket indices matching BUCKETS array
        if (hue >= 345 || hue < 15) return 0;  // red
        if (hue < 45)  return 1;  // orange
        if (hue < 75)  return 2;  // amber
        if (hue < 105) return 3;  // yellow
        if (hue < 150) return 4;  // green
        if (hue < 180) return 5;  // teal
        if (hue < 210) return 6;  // cyan
        if (hue < 240) return 7;  // blue
        if (hue < 270) return 8;  // indigo
        if (hue < 300) return 11; // purple (last chromatic)
        if (hue < 330) return 9;  // magenta
        return 10;                // pink
    },

    // ---- Spectrum -------------------------------------------------------

    _buildSpectrum(counts, firstIndices) {
        this.spectrum.innerHTML = '';
        const max = Math.max(...counts, 1);
        this.BUCKETS.forEach(b => {
            const n = counts[b.idx];
            if (!n) return;
            const seg = document.createElement('div');
            seg.className = 'spectrum-segment';
            seg.style.flex = `${n}`;
            seg.style.background = b.hue !== null
                ? `hsl(${b.hue}, 55%, 45%)`
                : (b.tone === 'light' ? '#e8e8e8' : '#111');
            seg.title = `${b.label} · ${n}`;
            seg.addEventListener('click', () => this._jumpTo(firstIndices[b.idx]));
            this.spectrum.appendChild(seg);
        });
    },

    _jumpTo(cardIdx) {
        if (cardIdx < 0) return;
        const card = this.mosaic.children[cardIdx];
        if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    // ---- Mosaic ---------------------------------------------------------

    _renderMosaic(sorted) {
        this.mosaic.innerHTML = '';
        const frag = document.createDocumentFragment();
        sorted.forEach(r => {
            const card = APP.createCard(r);
            frag.appendChild(card);
        });
        this.mosaic.appendChild(frag);

        if (APP.observer) {
            this.mosaic.querySelectorAll('img[data-src]:not([src])').forEach(img => {
                APP.observer.observe(img);
            });
        }
    },

    _hexToHsl(hex) {
        const r = parseInt(hex.slice(1, 3), 16) / 255;
        const g = parseInt(hex.slice(3, 5), 16) / 255;
        const b = parseInt(hex.slice(5, 7), 16) / 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        const l = (max + min) / 2;
        if (max === min) return { h: 0, s: 0, l: l * 100 };
        const d = max - min;
        const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        let h;
        if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        else if (max === g) h = ((b - r) / d + 2) / 6;
        else h = ((r - g) / d + 4) / 6;
        return { h: h * 360, s: s * 100, l: l * 100 };
    },

    destroy() {}
};
