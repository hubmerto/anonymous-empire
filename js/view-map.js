/* ============================================
   VIEW: Map
   Leaflet + CartoDB Dark Matter tiles.
   Each release is an individual thumbnail scattered
   across its scene's geographic area.
   ============================================ */

window.ViewMap = {
    isInitialized: false,
    map: null,
    layerGroup: null,
    sidebar: null,
    sidebarOpen: false,

    init(container) {
        this.container = container;
        this.mapEl = container.querySelector('#map-container');
        this.sidebar = container.querySelector('.map-sidebar');
        this.sidebarBody = container.querySelector('.map-sidebar-body');
        this.sidebarClose = container.querySelector('.map-sidebar-close');
        this.sidebarTitle = container.querySelector('.map-sidebar-title');
        this.sidebarCount = container.querySelector('.map-sidebar-count');
        this.sidebarLabels = container.querySelector('.map-sidebar-labels');
        this.sidebarGrid = container.querySelector('.map-sidebar-grid');

        this.sidebarClose.addEventListener('click', () => this._closeSidebar());

        // Init Leaflet
        this.map = L.map(this.mapEl, {
            zoomControl: false,
            attributionControl: false,
            minZoom: 3,
            maxZoom: 12,
            worldCopyJump: false,
            maxBounds: [[-75, -180], [85, 180]],
            maxBoundsViscosity: 1.0,
        }).setView([40, 5], 4);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            subdomains: 'abcd',
            maxZoom: 19,
        }).addTo(this.map);

        this.layerGroup = L.layerGroup().addTo(this.map);

        // Update thumb size based on zoom level
        this._updateZoomClass();
        this.map.on('zoomend', () => this._updateZoomClass());

        this.isInitialized = true;
    },

    _updateZoomClass() {
        const z = this.map.getZoom();
        const el = this.mapEl;
        // Remove old zoom classes
        el.classList.remove('zoom-world', 'zoom-continent', 'zoom-country', 'zoom-region', 'zoom-city');
        if (z <= 3) el.classList.add('zoom-world');
        else if (z <= 4) el.classList.add('zoom-continent');
        else if (z <= 5) el.classList.add('zoom-country');
        else if (z <= 7) el.classList.add('zoom-region');
        else el.classList.add('zoom-city');
    },

    render(filtered) {
        const geo = APP.data.geo || {};

        // Group by scene
        const byScene = {};
        filtered.forEach(r => {
            if (!byScene[r.scene]) byScene[r.scene] = [];
            byScene[r.scene].push(r);
        });

        // Clear previous
        this.layerGroup.clearLayers();

        // Seeded random for consistent placement
        let seed = 42;
        function rand() {
            seed = (seed * 16807 + 0) % 2147483647;
            return (seed - 1) / 2147483646;
        }

        // Spread radius per scene (degrees) — scales with count
        // More releases = wider spread to fill the area
        const allMarkers = [];

        for (const scene in geo) {
            const releases = byScene[scene] || [];
            if (releases.length === 0) continue;

            const coords = Array.isArray(geo[scene]) ? geo[scene] : [geo[scene].lat, geo[scene].lng];
            const baseLat = coords[0];
            const baseLng = coords[1];

            // Spread radius: scales with sqrt(count); keeps scatter inside the country.
            // Smaller / island scenes (Japan, UK, Scandinavia) get a tighter cap.
            const count = releases.length;
            const smallScenes = new Set(['Japan', 'UK / London', 'Netherlands', 'Ghent', 'Frankfurt', 'Munich', 'Hamburg', 'Scandinavia', 'Manchester', 'Italy', 'Spain', 'Eastern Europe']);
            const maxSpread = smallScenes.has(scene) ? 3.2 : 6.5;
            // Grow spread with count so dense scenes (Berlin, Detroit) don't overlap.
            const spread = Math.min(0.8 + Math.sqrt(count) * 0.35, maxSpread);

            // Phyllotaxis (sunflower) pattern: uniform coverage, no clustering.
            // angle = i * golden_angle ensures adjacent points are maximally separated.
            const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
            // Small per-scene rotation so patterns don't all point the same way.
            const phase = rand() * Math.PI * 2;

            releases.forEach((r, idx) => {
                // radius uses sqrt for uniform-area distribution; small jitter prevents rigid look.
                const t = (idx + 0.5) / count;
                const jitter = (rand() - 0.5) * 0.08;  // tiny, keeps no-overlap property
                const dist = (Math.sqrt(t) + jitter) * spread;
                const angle = idx * GOLDEN_ANGLE + phase;
                const lat = baseLat + Math.cos(angle) * dist * 0.7;
                const lng = baseLng + Math.sin(angle) * dist;

                const src = r.image || r.thumb || '';
                const size = 24;

                let html;
                if (src) {
                    html = `<div class="map-thumb" title="${APP.escapeHtml(r.artist + ' — ' + r.title)}">
                        <img src="${src}" loading="lazy" alt="">
                    </div>`;
                } else {
                    html = `<div class="map-thumb map-thumb-empty" title="${APP.escapeHtml(r.artist + ' — ' + r.title)}"></div>`;
                }

                const icon = L.divIcon({
                    html: html,
                    className: 'map-thumb-icon',
                    iconSize: [size, size],
                    iconAnchor: [size / 2, size / 2],
                });

                const marker = L.marker([lat, lng], { icon: icon });
                marker.on('click', () => APP.openOverlay(r));
                this.layerGroup.addLayer(marker);
                allMarkers.push(marker);
            });

            // Add scene label at center
            const labelIcon = L.divIcon({
                html: `<div class="map-scene-label" data-scene="${APP.escapeHtml(scene)}">
                    <span class="map-scene-name">${APP.escapeHtml(scene)}</span>
                    <span class="map-scene-count">${count}</span>
                </div>`,
                className: 'map-label-icon',
                iconSize: [120, 30],
                iconAnchor: [60, -8],
            });
            const label = L.marker([baseLat, baseLng], { icon: labelIcon, interactive: true });
            label.on('click', () => this._openSidebar(scene, releases));
            this.layerGroup.addLayer(label);
            allMarkers.push(label);
        }

        // Fit bounds
        if (allMarkers.length > 0) {
            const group = L.featureGroup(allMarkers);
            this.map.fitBounds(group.getBounds().pad(0.15), { maxZoom: 5, minZoom: 4 });
        }

        // Refresh sidebar if open
        if (this.sidebarOpen && this._currentScene) {
            const sceneReleases = byScene[this._currentScene] || [];
            if (sceneReleases.length > 0) {
                this._renderSidebarGrid(sceneReleases);
            } else {
                this._closeSidebar();
            }
        }

        setTimeout(() => this.map.invalidateSize(), 100);
    },

    _openSidebar(scene, releases) {
        this._currentScene = scene;
        this.sidebarOpen = true;

        this.sidebarTitle.textContent = scene;
        this.sidebarCount.textContent = `${releases.length} releases`;

        const countries = {};
        releases.forEach(r => { const c = r.country || ''; if (c) countries[c] = (countries[c] || 0) + 1; });
        const countryStr = Object.entries(countries).sort((a,b) => b[1]-a[1]).map(([c,n]) => `${c} (${n})`).join(' · ');

        const labels = [...new Set(releases.map(r => r.label))].sort();
        this.sidebarLabels.textContent = (countryStr ? countryStr + '\n' : '') + labels.join(' / ');

        this._renderSidebarGrid(releases);
        this.sidebar.classList.add('open');

        setTimeout(() => this.map.invalidateSize(), 300);
    },

    _renderSidebarGrid(releases) {
        this.sidebarGrid.innerHTML = '';
        releases.slice(0, 60).forEach(r => {
            const card = APP.createCard(r, true);
            this.sidebarGrid.appendChild(card);
        });
        if (APP.observer) {
            this.sidebarGrid.querySelectorAll('img[data-src]:not([src])').forEach(img => {
                APP.observer.observe(img);
            });
        }
    },

    _closeSidebar() {
        this.sidebarOpen = false;
        this._currentScene = null;
        this.sidebar.classList.remove('open');
        setTimeout(() => this.map.invalidateSize(), 300);
    },

    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
        this.isInitialized = false;
    }
};
