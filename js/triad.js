/* ============================================
   TRIAD — three words cycle through S/M/L sizes,
   always stacked 100vh, font-size fits container width.
   ============================================ */
(function () {
    const CYCLE_MS = 14000;
    // Size weights as fractions of 100vh.
    const SMALL = 0.10;
    const MED   = 0.20;
    const LARGE = 0.70;
    // Phase offsets per row (same order as DOM): SCARCITY, REFUSAL, RUIN.
    // Frame 0: SCARCITY=small, REFUSAL=medium, RUIN=large
    // So row 0 is at phase 0 (S→M), row 1 at 1/3 (M→L), row 2 at 2/3 (L→S).
    const PHASES = [0, 1/3, 2/3];

    function smoothstep(u) { return u * u * (3 - 2 * u); }

    // Piece-wise cosine-smoothed weight f(phase):
    //   [0,   1/3]: SMALL → MED
    //   [1/3, 2/3]: MED   → LARGE
    //   [2/3, 1  ]: LARGE → SMALL
    function weight(phase) {
        let p = ((phase % 1) + 1) % 1;
        if (p < 1/3) {
            const u = smoothstep(p / (1/3));
            return SMALL + (MED - SMALL) * u;
        } else if (p < 2/3) {
            const u = smoothstep((p - 1/3) / (1/3));
            return MED + (LARGE - MED) * u;
        } else {
            const u = smoothstep((p - 2/3) / (1/3));
            return LARGE + (SMALL - LARGE) * u;
        }
    }

    function init() {
        const section = document.getElementById('triad');
        if (!section) return;
        const rows = Array.from(section.querySelectorAll('.triad-row'));
        if (rows.length !== 3) return;
        const spans = rows.map(r => r.querySelector('span'));

        // Cache each word's reference pixel-width at a reference font-size
        // so we can compute fit-to-width with a single multiplication per frame.
        const REF_SIZE = 200; // px
        const refWidths = spans.map(() => 0);

        function measureRefWidths() {
            const probe = document.createElement('span');
            probe.style.position = 'absolute';
            probe.style.visibility = 'hidden';
            probe.style.whiteSpace = 'nowrap';
            probe.style.fontFamily = getComputedStyle(spans[0]).fontFamily;
            probe.style.fontWeight = getComputedStyle(spans[0]).fontWeight;
            probe.style.letterSpacing = getComputedStyle(spans[0]).letterSpacing;
            probe.style.textTransform = 'uppercase';
            probe.style.fontSize = REF_SIZE + 'px';
            document.body.appendChild(probe);
            spans.forEach((s, i) => {
                probe.textContent = s.textContent;
                refWidths[i] = probe.offsetWidth || 1;
            });
            probe.parentNode.removeChild(probe);
        }

        const start = performance.now();
        let lastW = 0, lastH = 0;

        function frame(now) {
            const t = ((now - start) % CYCLE_MS) / CYCLE_MS;
            const w = section.clientWidth;
            const h = section.clientHeight;
            if (w !== lastW || h !== lastH) {
                lastW = w;
                lastH = h;
                measureRefWidths();
            }
            // Weights for each row and their band heights (px).
            const weights = PHASES.map(off => weight(t + off));
            // Normalize (should already sum to 1 but float drift).
            const sum = weights.reduce((a, b) => a + b, 0) || 1;
            const bandH = weights.map(ww => (ww / sum) * h);

            for (let i = 0; i < 3; i++) {
                rows[i].style.height = bandH[i].toFixed(2) + 'px';
                // Fit font-size to container width (with 2% side padding → 96%).
                const widthFont = (w * 0.96 / refWidths[i]) * REF_SIZE;
                // Cap by band height so a large word doesn't overflow vertically.
                // Typical cap-height ratio for blocky display fonts ≈ 0.78 of font-size.
                const heightFont = bandH[i] / 0.82;
                const fs = Math.min(widthFont, heightFont);
                spans[i].style.fontSize = fs.toFixed(1) + 'px';
                // Tighter tracking at large sizes, slightly looser when small.
                const sizeRatio = fs / (h * 0.6);
                const ls = -0.04 + 0.035 * (1 - Math.min(1, sizeRatio));
                spans[i].style.letterSpacing = ls.toFixed(3) + 'em';
            }
            requestAnimationFrame(frame);
        }
        // Kick off after fonts settle so measurement is correct.
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(() => {
                measureRefWidths();
                requestAnimationFrame(frame);
            });
        } else {
            measureRefWidths();
            requestAnimationFrame(frame);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
