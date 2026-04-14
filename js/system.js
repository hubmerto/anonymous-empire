/* ============================================
   Visual System Breakdown: pulls 5 representative covers
   from the archive, one per element.
   ============================================ */
(function () {
    fetch('data/releases.json')
        .then(r => r.json())
        .then(d => fill(d.releases || []))
        .catch(err => console.error('system:', err));

    function fill(rs) {
        const withImg = rs.filter(r => r.image || r.thumb);
        if (!withImg.length) return;
        // Shuffle seeded-ish so the 5 picks differ each load but stay cohesive.
        for (let i = withImg.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [withImg[i], withImg[j]] = [withImg[j], withImg[i]];
        }
        document.querySelectorAll('.system-item').forEach((el, i) => {
            const r = withImg[i % withImg.length];
            const img = document.createElement('img');
            img.src = r.thumb || r.image;
            img.alt = '';
            img.loading = 'lazy';
            el.querySelector('.system-img').appendChild(img);
        });
    }
})();
