/* ============================================
   HERO — living pile of covers
   Real-time 2D physics: gravity, circle-circle collisions, friction,
   mouse repulsion. Drops spawn from the top-center and settle into
   a shifting pile at the bottom of the hero frame.
   ============================================ */

(function () {
    // Smaller screens → fewer, smaller covers (still enough to cover the frame).
    const IS_MOBILE = window.matchMedia('(max-width: 720px)').matches;
    const SPAWN_INTERVAL_MS = IS_MOBILE ? 70 : 50;
    const MAX_DROPS = IS_MOBILE ? 90 : 250;
    const MIN_SIZE = IS_MOBILE ? 24 : 32;
    const MAX_SIZE = IS_MOBILE ? 54 : 78;
    const GRAVITY = 0.55;
    const FRICTION = 0.985;
    const RESTITUTION = 0.35;
    const WALL_BOUNCE = 0.45;
    const MOUSE_AVOID = 140;
    const MOUSE_FORCE = 2.2;

    function init() {
        const hero = document.getElementById('hero');
        const stage = document.getElementById('hero-drops');
        if (!hero || !stage) return;
        // Use APP.data if present (library page), otherwise fetch directly (home page).
        if (typeof APP !== 'undefined') {
            const tryStart = () => {
                if (APP.data && APP.data.releases) start(hero, stage, APP.data.releases);
                else setTimeout(tryStart, 150);
            };
            tryStart();
        } else {
            fetch('data/releases.json')
                .then(r => r.json())
                .then(d => start(hero, stage, d.releases))
                .catch(err => console.error('hero: failed to load releases', err));
        }
    }

    function start(hero, stage, releases) {
        const withImages = releases.filter(r => r.image || r.thumb);
        if (!withImages.length) return;
        // Shuffle so the pile isn't data-ordered.
        for (let i = withImages.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [withImages[i], withImages[j]] = [withImages[j], withImages[i]];
        }

        const bodies = [];
        let dropCount = 0;
        let spawner = null;
        let W = 0, H = 0;
        function measure() {
            const hr = hero.getBoundingClientRect();
            W = hr.width; H = hr.height;
        }
        measure();

        function spawn() {
            if (dropCount >= MAX_DROPS) { clearInterval(spawner); return; }
            const rel = withImages[dropCount % withImages.length];
            const src = rel.image || rel.thumb;
            const size = MIN_SIZE + Math.random() * (MAX_SIZE - MIN_SIZE);
            const r = size / 2;

            const el = document.createElement('div');
            el.className = 'hero-drop';
            el.style.width = size + 'px';
            el.style.height = size + 'px';
            el.style.top = '0px';
            el.style.left = '0px';
            el.style.transition = 'none';   // physics drives transform directly
            el.style.willChange = 'transform';

            const img = document.createElement('img');
            img.src = src; img.alt = ''; img.loading = 'lazy';
            el.appendChild(img);
            stage.appendChild(el);

            bodies.push({
                x: W / 2,
                y: -r - 10,
                vx: (Math.random() - 0.5) * 1.6,
                vy: 1.5 + Math.random() * 1.2,
                r,
                angle: 0,
                angVel: (Math.random() - 0.5) * 2,
                el,
            });
            dropCount++;
        }

        function step() {
            measure();
            const n = bodies.length;

            // integrate
            for (let i = 0; i < n; i++) {
                const b = bodies[i];
                b.vy += GRAVITY;
                b.vx *= FRICTION;
                b.vy *= FRICTION;

                b.x += b.vx;
                b.y += b.vy;
                b.angle += b.angVel;
                b.angVel *= 0.97;

                // walls
                if (b.x - b.r < 0) { b.x = b.r; b.vx = -b.vx * WALL_BOUNCE; b.angVel += b.vy * 0.015; }
                if (b.x + b.r > W) { b.x = W - b.r; b.vx = -b.vx * WALL_BOUNCE; b.angVel -= b.vy * 0.015; }
                if (b.y + b.r > H) {
                    b.y = H - b.r;
                    if (b.vy > 0) b.vy = -b.vy * WALL_BOUNCE;
                    b.vx *= 0.92;                  // ground friction
                    b.angVel = b.vx * 0.15;        // rolling
                }
            }

            // pairwise collisions (a few passes to stabilize the pile)
            for (let pass = 0; pass < 6; pass++) {
                for (let i = 0; i < n; i++) {
                    const a = bodies[i];
                    for (let j = i + 1; j < n; j++) {
                        const b = bodies[j];
                        const dx = b.x - a.x, dy = b.y - a.y;
                        const rr = a.r + b.r;
                        const d2 = dx * dx + dy * dy;
                        if (d2 < rr * rr && d2 > 0.0001) {
                            const d = Math.sqrt(d2);
                            const nx = dx / d, ny = dy / d;
                            const overlap = (rr - d) * 0.5;
                            a.x -= nx * overlap; a.y -= ny * overlap;
                            b.x += nx * overlap; b.y += ny * overlap;

                            if (pass === 0) {
                                // relative velocity along normal
                                const rvx = b.vx - a.vx, rvy = b.vy - a.vy;
                                const vn = rvx * nx + rvy * ny;
                                if (vn < 0) {
                                    const imp = -(1 + RESTITUTION) * vn / 2;
                                    a.vx -= imp * nx; a.vy -= imp * ny;
                                    b.vx += imp * nx; b.vy += imp * ny;
                                    // tangential kick → spin
                                    const tKick = (rvx * -ny + rvy * nx) * 0.06;
                                    a.angVel -= tKick;
                                    b.angVel += tKick;
                                }
                            }
                        }
                    }
                }
            }

            // render
            for (let i = 0; i < n; i++) {
                const b = bodies[i];
                b.el.style.transform =
                    `translate(${b.x - b.r}px, ${b.y - b.r}px) rotate(${b.angle}deg)`;
            }
            requestAnimationFrame(step);
        }
        requestAnimationFrame(step);

        spawner = setInterval(spawn, SPAWN_INTERVAL_MS);

        window.addEventListener('resize', () => {
            const prevW = W, prevH = H;
            measure();
            if (!prevW || !prevH) return;
            const sx = W / prevW, sy = H / prevH;
            bodies.forEach(b => { b.x *= sx; b.y *= sy; });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
