/* ============================================
   TRAIL — mouse drops covers as it moves, they fade out.
   Touch devices also supported.
   ============================================ */
(function () {
    const MIN_DIST = 22;       // px between drops along the trail
    const SIZE_MIN = 38;
    const SIZE_MAX = 70;
    const LIFETIME = 5800;     // ms until full fade
    const MAX_ACTIVE = 400;    // cap DOM nodes

    function init(covers) {
        const frame = document.getElementById('trail-frame');
        if (!frame) return;
        let pool = covers.slice();
        // Shuffle so draws aren't data-ordered.
        for (let i = pool.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [pool[i], pool[j]] = [pool[j], pool[i]];
        }
        let pi = 0;
        const active = [];
        let lastX = null, lastY = null;

        function drop(x, y) {
            if (active.length >= MAX_ACTIVE) {
                const old = active.shift();
                if (old && old.parentNode) old.parentNode.removeChild(old);
            }
            const rel = pool[pi++ % pool.length];
            const src = rel.thumb || rel.image;
            if (!src) return;
            const size = SIZE_MIN + Math.random() * (SIZE_MAX - SIZE_MIN);
            const rot = (Math.random() - 0.5) * 20;
            const el = document.createElement('div');
            el.className = 'trail-drop';
            el.style.width = size + 'px';
            el.style.height = size + 'px';
            el.style.transform =
                `translate(${(x - size / 2).toFixed(1)}px, ${(y - size / 2).toFixed(1)}px) rotate(${rot.toFixed(1)}deg)`;
            const img = document.createElement('img');
            img.src = src;
            img.alt = '';
            img.loading = 'lazy';
            el.appendChild(img);
            frame.appendChild(el);
            active.push(el);
            // Kick fade on next frame so the initial opacity:1 renders first.
            requestAnimationFrame(() => el.classList.add('fading'));
            setTimeout(() => {
                if (el.parentNode) el.parentNode.removeChild(el);
                const i = active.indexOf(el);
                if (i >= 0) active.splice(i, 1);
            }, LIFETIME);
        }

        function onMove(clientX, clientY) {
            const r = frame.getBoundingClientRect();
            const x = clientX - r.left;
            const y = clientY - r.top;
            if (x < 0 || y < 0 || x > r.width || y > r.height) return;
            if (lastX === null) { lastX = x; lastY = y; drop(x, y); return; }
            const dx = x - lastX, dy = y - lastY;
            const d = Math.hypot(dx, dy);
            if (d < MIN_DIST) return;
            // Fill intermediate positions so a fast move still draws a continuous line.
            const steps = Math.min(8, Math.floor(d / MIN_DIST));
            for (let i = 1; i <= steps; i++) {
                const t = i / steps;
                drop(lastX + dx * t, lastY + dy * t);
            }
            lastX = x; lastY = y;
        }

        frame.addEventListener('mousemove', e => onMove(e.clientX, e.clientY));
        frame.addEventListener('mouseleave', () => { lastX = lastY = null; });
        frame.addEventListener('touchmove', e => {
            if (e.touches.length) {
                const t = e.touches[0];
                onMove(t.clientX, t.clientY);
            }
        }, { passive: true });
        frame.addEventListener('touchend', () => { lastX = lastY = null; });
    }

    function start() {
        // Use the page's hero-loaded data if available to avoid a second fetch.
        fetch('/data/releases.json')
            .then(r => r.json())
            .then(d => init((d.releases || []).filter(r => r.image || r.thumb)))
            .catch(err => console.error('trail:', err));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
