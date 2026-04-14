/* ============================================
   SCENES — 6 cards in a row. Arrow buttons walk through scenes;
   the matching card slides to centre and expands.
   ============================================ */

const SCENES = {
    detroit: {
        title: 'Detroit',
        body: "Where the visual language began. Three labels on the same block of Gratiot Avenue built the genre's graphic foundation with rulers, photocopiers, and Afrofuturist illustration. Abdul Qadim Haqq and Alan Oldham created two distinct visual dialects: Haqq's mythological worldbuilding for Drexciya and Underground Resistance, Oldham's anime-inflected sci-fi for Transmat. The white label emerged here as both budget constraint and design decision. Underground Resistance turned anonymity into a visual identity system more recognizable than any face could be.",
    },
    berlin: {
        title: 'Berlin',
        body: "Architecture became the design brief. Tresor opened inside an abandoned bank vault in 1991. Its physical environment dictated the label's entire visual vocabulary: metal, concrete, industrial fog. Basic Channel reduced the sleeve to near-zero information. Cryptic lettering, embossed logos barely visible to the eye. Ostgut Ton's Yusuf Etiman built Berghain's visual identity by refusing to look at what other labels did. The real question, in his words: what does our thing look like? PAN moved the other direction entirely, building an algorithmic digital platform that treats artwork as mutable code rather than fixed image. Berlin's design range runs from maximum reduction to maximum experimentation. The constant is systematic thinking.",
    },
    london: {
        title: 'London',
        body: "The widest visual range of any single city. From George Georgiou's acid house smiley in 1988 to Hyperdub's bass-weight futurism, Blackest Ever Black's post-punk noir, and Hospital Productions' industrial confrontation. London never unified around a single design system. It absorbed, refracted, and recombined. Dave Little's 1988 Spectrum flyer is in the V&A's permanent collection. Junior Tomlin's flyer work has sold at Bonhams.",
    },
    belgium: {
        title: 'Ghent / Brussels',
        body: "R&S Records built one of the genre's most distinctive visual marks: a green triangle bearing a prancing horse silhouette. The identity crossed from music into fashion when Raf Simons featured it on oversized t-shirts at Paris Fashion Week SS20. Apollo Records extended the label's ambient wing with its own restrained typographic system.",
    },
    japan: {
        title: 'Japan',
        body: "Under-documented in English and overdue for serious design attention. Mule Musiq, Op.disc, Sublime Records, and Far East Recording represent a scene with deep engagement with both Detroit's Afrofuturism and Berlin's reductionism, filtered through a distinct graphic sensibility rooted in Japanese design traditions. The Japanese techno visual archive remains one of the significant gaps in the genre's documented history.",
    },
    brazil: {
        title: 'São Paulo / South America',
        body: 'Emerging documentation. Labels like QTV and the broader Brazilian electronic underground are building visual identities that draw on international techno conventions and local graphic traditions simultaneously. Poorly documented, rapidly evolving, and producing some of the most distinctive new sleeve design in the genre.',
    },
};

(function () {
    function init() {
        const carousel = document.getElementById('scenes-carousel');
        const textEl = document.getElementById('scene-text');
        if (!carousel || !textEl) return;

        const titleEl = textEl.querySelector('.scene-title');
        const bodyEl = textEl.querySelector('.scene-body');

        // Clone the 6 cards several times so neighbours of any active card
        // always show something — gives an infinite/repeating effect.
        const originals = Array.from(carousel.children);
        const COPIES = 5; // odd so there's a clear middle block
        for (let c = 1; c < COPIES; c++) {
            originals.forEach(card => carousel.appendChild(card.cloneNode(true)));
        }
        const cards = Array.from(carousel.children);
        const sceneKeys = Object.keys(SCENES);

        const MAX_SCALE = 1.55;

        let currentKey = null;
        let fadeTimer = null;
        function setText(key) {
            if (key === currentKey) return;
            const scene = SCENES[key];
            if (!scene) return;
            currentKey = key;
            textEl.classList.add('fading');
            clearTimeout(fadeTimer);
            fadeTimer = setTimeout(() => {
                titleEl.textContent = scene.title;
                bodyEl.textContent = scene.body;
                textEl.classList.remove('fading');
            }, 180);
        }

        function layout(activeIdx) {
            const n = cards.length;
            const widths = cards.map(c => c.offsetWidth);
            const scales = cards.map((_, i) => i === activeIdx ? MAX_SCALE : 1);

            // Cumulative lateral push so neighbours step aside for the scaled one.
            const offsets = new Array(n).fill(0);
            let acc = (scales[activeIdx] - 1) * widths[activeIdx] / 2;
            for (let i = activeIdx + 1; i < n; i++) {
                offsets[i] = acc + (scales[i] - 1) * widths[i] / 2;
                acc += (scales[i] - 1) * widths[i];
            }
            acc = (scales[activeIdx] - 1) * widths[activeIdx] / 2;
            for (let i = activeIdx - 1; i >= 0; i--) {
                offsets[i] = -(acc + (scales[i] - 1) * widths[i] / 2);
                acc += (scales[i] - 1) * widths[i];
            }

            // Extra shift so the active card centres within the carousel viewport.
            const activeCenter = cards[activeIdx].offsetLeft + widths[activeIdx] / 2 + offsets[activeIdx];
            const viewportCenter = carousel.clientWidth / 2;
            const globalShift = viewportCenter - activeCenter;

            for (let i = 0; i < n; i++) {
                const t = i === activeIdx ? 1 : 0;
                cards[i].style.transform =
                    `translate3d(${(offsets[i] + globalShift).toFixed(2)}px, 0, 0) scale(${scales[i].toFixed(4)})`;
                cards[i].style.filter = `brightness(${(0.55 + 0.45 * t).toFixed(3)})`;
                cards[i].style.zIndex = String(i === activeIdx ? 10 : 1);
            }
        }

        let sceneIdx = 0;
        function showScene(idx) {
            sceneIdx = ((idx % sceneKeys.length) + sceneKeys.length) % sceneKeys.length;
            const key = sceneKeys[sceneIdx];
            setText(key);
            // Prefer the copy of this scene nearest the middle of the row.
            const middle = cards.length / 2;
            let cardIdx = -1, best = Infinity;
            cards.forEach((c, i) => {
                if (c.dataset.scene === key) {
                    const d = Math.abs(i - middle);
                    if (d < best) { best = d; cardIdx = i; }
                }
            });
            if (cardIdx >= 0) layout(cardIdx);
        }

        // Click a card → select that scene too.
        carousel.addEventListener('click', (e) => {
            const card = e.target.closest('.scene-card');
            if (!card) return;
            const key = card.dataset.scene;
            const idx = sceneKeys.indexOf(key);
            if (idx >= 0) showScene(idx);
        });

        const prevBtn = document.getElementById('scene-prev');
        const nextBtn = document.getElementById('scene-next');
        if (prevBtn) prevBtn.addEventListener('click', () => showScene(sceneIdx - 1));
        if (nextBtn) nextBtn.addEventListener('click', () => showScene(sceneIdx + 1));

        window.addEventListener('resize', () => showScene(sceneIdx));

        // Give images a tick to measure, then lay out.
        requestAnimationFrame(() => showScene(sceneKeys.indexOf('berlin')));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
