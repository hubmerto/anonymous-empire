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
    // Perceptual chroma threshold — anything below this treats the cover as
    // achromatic regardless of its dominant colour. Tuned so white/grey sleeves
    // with a stray pop of colour still sort into the achromatic tier.
    CHROMA_THRESHOLD: 22,

    // Recompute a better (hue, lightness, chroma, isChromatic) from the palette.
    // Previously we trusted extract_colors.py's sort_hue, which picked the
    // dominant swatch and often mis-sorted near-grey covers.
    _analyze(r) {
        const palette = Array.isArray(r.palette) ? r.palette : [];
        const primary = r.hsl || {};
        // Circular-mean hue weighted by (frac × chroma)
        let sumX = 0, sumY = 0, sumW = 0, chromaTotal = 0, totalFrac = 0, lightAvg = 0;
        palette.forEach(p => {
            const c = typeof p.c === 'number' ? p.c : 0;
            const f = typeof p.frac === 'number' ? p.frac : 0;
            const w = c * f;
            const hRad = (p.h || 0) * Math.PI / 180;
            sumX += Math.cos(hRad) * w;
            sumY += Math.sin(hRad) * w;
            sumW += w;
            chromaTotal += c * f;
            totalFrac += f;
            lightAvg += (p.l || 0) * f;
        });
        const l = totalFrac > 0 ? lightAvg / totalFrac : (primary.l || 0);
        let hue = 0;
        if (sumW > 0.001) {
            hue = Math.atan2(sumY, sumX) * 180 / Math.PI;
            if (hue < 0) hue += 360;
        } else if (typeof primary.h === 'number') {
            hue = primary.h;
        }
        const effectiveChroma = totalFrac > 0 ? chromaTotal / totalFrac : 0;
        const isChromatic = effectiveChroma >= this.CHROMA_THRESHOLD;
        return { hue, l, chroma: effectiveChroma, isChromatic };
    },

    _sortKey(r) {
        const a = this._analyze(r);
        const bi = this._bucketOf(r, a);
        if (!a.isChromatic) {
            // Achromatic tier — sort by lightness (dark first, then light last)
            return [bi, a.l, 0];
        }
        // Chromatic tier — sort by hue then lightness, with chroma as tiebreaker
        return [bi, a.hue, a.l, -a.chroma];
    },

    _bucketOf(r, a) {
        a = a || this._analyze(r);
        if (!a.isChromatic) {
            return a.l >= this.LIGHT_L_THRESHOLD ? 13 : 12;
        }
        const h = a.hue;
        if (h >= 345 || h < 15) return 0;  // red
        if (h < 45)  return 1;  // orange
        if (h < 75)  return 2;  // amber
        if (h < 105) return 3;  // yellow
        if (h < 150) return 4;  // green
        if (h < 180) return 5;  // teal
        if (h < 210) return 6;  // cyan
        if (h < 240) return 7;  // blue
        if (h < 270) return 8;  // indigo
        if (h < 300) return 11; // purple (last chromatic)
        if (h < 330) return 9;  // magenta
        return 10;              // pink
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
