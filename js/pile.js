(function(){
  var container = document.getElementById('cover-pile');
  if (!container || !window.ALL_COVERS || !ALL_COVERS.length) return;

  var pool = ALL_COVERS.slice();
  for (var i = pool.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp;
  }

  var INTERVAL = 300;   // ms between new covers
  var LIFETIME = 4000;  // ms before a cover fades out
  var idx = 0;
  var z = 1;

  function addCover() {
    var src = pool[idx % pool.length];
    idx++;
    var img = document.createElement('img');
    img.className = 'pile-cover';
    img.src = 'images/' + src;
    img.alt = '';
    img.loading = 'lazy';

    // Constrain so cover (35% wide, square) stays fully within container
    var rect = container.getBoundingClientRect();
    var coverW = rect.width * 0.35;
    var coverH = coverW; // square
    var maxDxPct = rect.width > 0 ? ((rect.width - coverW) / 2) / rect.width * 100 : 15;
    var maxDyPct = rect.height > 0 ? ((rect.height - coverH) / 2) / rect.height * 100 : 15;
    maxDxPct = Math.max(0, maxDxPct - 2);
    maxDyPct = Math.max(0, maxDyPct - 2);
    var dx = (Math.random() - 0.5) * 2 * maxDxPct;
    var dy = (Math.random() - 0.5) * 2 * maxDyPct;
    var rot = (Math.random() - 0.5) * 12;
    img.style.left = 'calc(50% + ' + dx + '%)';
    img.style.top = 'calc(50% + ' + dy + '%)';
    var baseTransform = 'translate(-50%, -50%) rotate(' + rot + 'deg)';
    img.style.transform = baseTransform + ' scale(1)';
    img.style.opacity = '1';
    img.style.transition = 'none';
    img.style.zIndex = String(z++);

    container.appendChild(img);

    // Each cover lives 4s, then fades and is removed
    setTimeout(function(){
      img.style.transition = 'opacity 0.5s ease';
      img.style.opacity = '0';
      setTimeout(function(){
        if (img.parentNode) img.parentNode.removeChild(img);
      }, 600);
    }, LIFETIME);
  }

  var started = false;
  var handle;

  function start() {
    if (started) return;
    started = true;
    addCover();
    handle = setInterval(addCover, INTERVAL);
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { start(); io.disconnect(); }
      });
    }, { threshold: 0.15 });
    io.observe(container);
  } else {
    start();
  }
})();
