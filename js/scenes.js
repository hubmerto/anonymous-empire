/* ============================================
   SCENES — all 20 city/region scenes. Arrow buttons walk through; the
   active card scales up and the prose below updates.
   ============================================ */

const SCENES = {
    detroit: {
        title: 'Detroit',
        body: "Where the visual language began. Three labels on the same block of Gratiot Avenue built the genre's graphic foundation with rulers, photocopiers, and Afrofuturist illustration. Abdul Qadim Haqq and Alan Oldham created two distinct visual dialects: Haqq's mythological worldbuilding for Drexciya and Underground Resistance, Oldham's anime-inflected sci-fi for Transmat. The white label emerged here as both budget constraint and design decision. Underground Resistance performed in balaclavas, scratched messages into vinyl run-out grooves, and turned anonymity into a visual identity system more recognizable than any face could be. Metroplex, Transmat, KMS, Planet E, Axis: each label developed a distinct sleeve language, but the shared principle was refusal. No portraits, no celebrity, no personality between the listener and the sound. Detroit techno's visual identity was a deliberate counter-position to every other genre: futurism over street realism, system over personality, erasure as the most powerful formal decision.",
    },
    chicago: {
        title: 'Chicago',
        body: "Techno's sibling scene developed its own graphic conventions that diverged sharply from Detroit's abstraction. Horizontal lines, contrasting metallics, condensed angular type, vocalist photography. The design language stayed closer to soul and disco traditions, warmer and more personality-driven. Trax Records, DJ International, and Dance Mania each built recognizable sleeve formats that functioned as brand systems within tight production budgets. Where Detroit erased the body, Chicago kept it present: vocalists appeared on covers, club photography circulated, the visual culture remained connected to the dancefloor as a social space. Cajual and Relief Records carried this into the 1990s with functional, no-frills sleeve design that prioritized catalog efficiency over visual experimentation. Prescription Records and Guidance Recordings later introduced more refined typographic approaches. The distinction between Chicago and Detroit's visual output maps directly onto the distinction between their sounds: groove and voice versus machine and absence.",
    },
    berlin: {
        title: 'Berlin',
        body: "Architecture became the design brief. Tresor opened inside an abandoned bank vault in 1991. Its physical environment dictated the label's entire visual vocabulary: metal, concrete, industrial fog. Basic Channel reduced the sleeve to near-zero information. Cryptic lettering, embossed logos barely visible to the eye. No designer credits exist for their output. Ostgut Ton's Yusuf Etiman built Berghain's visual identity by refusing to look at what other labels did. The real question, in his words: what does our thing look like? Wolfgang Tillmans provided photographs. Vanja Golubovic redesigned Tresor's visual communication from 2014 using Px Grotesk typeface, grid-based layouts, and annual thematic guidelines cycling through textures, photographs, geometric shapes, and variable font typography. PAN moved the other direction entirely, building an algorithmic digital platform that treats artwork as mutable code rather than fixed image. Berlin's design range runs from maximum reduction to maximum experimentation. The constant across all of it is systematic thinking.",
    },
    cologne: {
        title: 'Cologne',
        body: "Kompakt turned corporate identity into a pop art project. Wolfgang Voigt conceived the dot-matrix aesthetic from Warhol's technique. Bianca Strauch developed it into a complete design system. Veronika Unland's Pop Ambient covers, twenty-six editions of ethereal floral imagery since 2001, proved that warmth and systematic precision can coexist in the same identity. The Kompakt system is instantly recognizable not because of any single cover, but because the logic repeats. Profan, Kompakt's harder sublabel, introduced darker palettes while maintaining the parent label's structural discipline. Traum Schallplatten added another voice with progressive, dreamlike artwork that sat between Kompakt's pop clarity and Frankfurt's theoretical density. Cologne's contribution to techno's visual culture is the clearest demonstration that a label identity is a design system, not a collection of individual covers. The dot grid, the floral series, the typographic consistency: each element serves the system, and the system is the brand.",
    },
    frankfurt: {
        title: 'Frankfurt',
        body: "Force Inc., Mille Plateaux, Playhouse, Klang Elektronik. Frankfurt's label cluster operated at the intersection of techno, theory, and post-structuralist thought. Mille Plateaux took its name from Deleuze and Guattari, and the visual output matched: conceptual, text-heavy, deliberately intellectual. Sleeve design functioned as argument. Playhouse and Klang Elektronik shared a looser, more playful sensibility, with artwork that referenced club culture's hedonism without abandoning formal rigor. Ongaku Musik bridged the Frankfurt scene's experimental edge with a more minimal, Japanese-inflected aesthetic. The Frankfurt labels were among the first in techno to treat the record sleeve as a space for critical discourse rather than pure visual identity. Where Cologne built systems and Berlin built atmospheres, Frankfurt built positions. The city's influence on techno's visual culture is intellectual before it is aesthetic: the idea that a label's design should make an argument about what the music means.",
    },
    hamburg: {
        title: 'Hamburg',
        body: "Dial and Smallville represented the quieter register of German techno. Deep house and dub-inflected electronics with visual identities to match. Restrained typography, muted palettes, almost domestic warmth. Dial's sleeve design, guided by a consistent photographic sensibility, built an identity around understatement: soft focus, muted color, images that suggest interior spaces rather than industrial ones. Smallville Records adopted a similarly warm approach with painterly, textured covers that rejected the monochrome severity of Berlin's visual language. Pudel Produkte, connected to Hamburg's legendary Golden Pudel Club, brought a scrappier, more anarchic energy to the city's design output. The Hamburg scene's visual identity is the opposite of Berlin's industrial maximalism, but equally committed to coherent systematic design. The principle: restraint is not the same as reduction, and warmth can be as rigorous as austerity.",
    },
    munich: {
        title: 'Munich',
        body: "Ilian Tape's approach is singular in the genre. Since catalog number IT020, all artwork has been created by Bettina Zenker, the mother of label founders Dario and Marco Zenker. Original oil paintings on canvas for each release. No templates, no grid system, no typographic formula. Each cover is a unique physical object before it becomes a printed sleeve. When the label withdrew its entire catalog from Spotify to protest royalty rates, the gesture was consistent: artwork belongs on a physical object, not a thumbnail. Disko B, Munich's longer-running electronic label, built a contrasting identity rooted in playful graphic experimentation across genres. But Ilian Tape is the scene's defining visual statement. In a genre dominated by systematic repetition and digital production, one label chose to commission paintings from one artist for every release. The commitment to a single hand in a faceless genre is itself a design position.",
    },
    chemnitz: {
        title: 'Chemnitz / Dresden',
        body: "Raster-Noton. Founded by Olaf Bender and Carsten Nicolai in 1996, with Frank Bretschneider as the third founder. All three grew up in East Germany, where cultural isolation produced radical minimalism. Limited-edition vinyl arrived in black cardboard, identifiable only by a debossed typographic detail on the front. Simple geometric shapes, 2D surfaces, mathematics as aesthetic principle. Bender handled most of the design personally: his approach drew on optics, signal processing, and the visual logic of digital information. Carsten Nicolai's work as Alva Noto is held by MoMA and Centre Pompidou. The label won an Ars Electronica Golden Nica in 2000. Chain Reaction, Basic Channel's sublabel, packaged CD compilations in metal cans resembling DJ record boxes. Raster-Noton's contribution is the most rigorous reduction in the genre: artwork as pure information design, where the visual and the sonic obey the same mathematical logic.",
    },
    sheffield: {
        title: 'Sheffield / Leeds',
        body: "The Designers Republic may be the single most influential design studio in electronic music history. Ian Anderson and Nick Phillips made a proposal to Warp Records co-founders Steve Beckett and Rob Mitchell that changed the genre's visual trajectory: choose a colour and make everything that colour. A single Pantone purple became the label's visual signature for an entire decade. Anderson drew the Warp globe logo from 1950s science fiction and Dan Dare comics. His reasoning was precise: nothing dates so badly as the future, so he looked at futuristic imagery from the past. The Artificial Intelligence compilation in 1992, with CGI by Phil Wolstenholme, reframed electronic music as art for headphones. The Designers Republic also created the visual world of the WipEout video games, carrying techno's graphic language into mainstream culture. Their 1994 Emigre issue remains that publication's best-selling edition and sits in MoMA's permanent collection. Editions Mego in Leeds continued the region's experimental legacy with stark, austere artwork that bridged noise, electronic, and academic music.",
    },
    london: {
        title: 'London',
        body: "The widest visual range of any single city in the archive. George Georgiou created the acid house smiley in January 1988 for Danny Rampling's Shoom night, launching a visual explosion that had almost nothing in common with Detroit's austerity. Rave flyers were survival documents first: phone numbers, pirate radio frequencies, hand-drawn maps to illegal parties. Junior Tomlin, Dave Little, and Lawrence Manning created an airbrushed, fluorescent visual language. Little's 1988 Spectrum flyer is now in the V&A's permanent collection. Tomlin's work has sold at Bonhams. Decades later, Hyperdub built a visual identity rooted in bass-weight futurism, while Blackest Ever Black drew on film noir and 1960s paperback design. Hospital Productions brought industrial confrontation. Hessle Audio and Livity Sound developed clean, functional sleeve systems for UK bass and techno hybrids. London never unified around a single design system. It absorbed, refracted, and recombined everything, which is itself a design position: the refusal of a singular identity.",
    },
    belgium: {
        title: 'Ghent / Brussels',
        body: "R&S Records, founded in 1983 by Renaat Vandepapeliere and Sabine Maes, produced one of the most distinctive visual marks in electronic music: a green triangle bearing a prancing horse silhouette. The label insists the mark is not associated with Ferrari but embodies the freedom of dance. The ambiguity is part of the design. A logo that invites misreading is a logo that generates conversation. Ian Anderson of The Designers Republic confirmed that his studio worked for both Warp and R&S, creating what he described as a visual vernacular for a certain genre of music. The crossover is significant: the same design intelligence that defined Sheffield's output also shaped the Belgian label's identity. The mark's strength was proven when Raf Simons featured the R&S logo on oversized t-shirts at Paris Fashion Week SS20. A logo designed for 12-inch vinyl sleeves in Ghent ended up on a Paris runway as cultural citation. Apollo Records, R&S's ambient sublabel, extended the system with its own restrained typographic identity, demonstrating how a strong parent brand can generate coherent sub-identities.",
    },
    netherlands: {
        title: 'Netherlands',
        body: "Clone and Delsin in Rotterdam built deep, functional visual systems for durable catalogs. Clean, modular, designed for scale. Clone's extensive sublabel network, including Clone Aqualung, Clone Jack for Daze, and Clone Classic Cuts, each maintained distinct visual identities while sharing a structural logic rooted in systematic catalog design. Delsin Records applied a similarly methodical approach, with consistent typography and restrained color palettes that emphasized the catalog as a body of work rather than a series of individual statements. Eevo Lansen, connected to the Clone ecosystem, pushed toward more experimental territory. Mord Records arrived later with a harder, darker identity built on aggressive typography and stark black-and-white imagery. Dutch techno design tends toward the systematic, where form follows catalog. The contribution is less about individual visual statements and more about demonstrating that long-term catalog management is itself a design discipline.",
    },
    paris: {
        title: 'Paris',
        body: "InFiné and Ed Banger occupy opposite ends of the same city, and between them they define the range of French electronic music's visual identity. InFiné's refined typographic restraint, rooted in classical design principles and subtle color work, represents the cerebral end. Ed Banger's maximalist pop energy, driven by the graphic work of So Me and a roster that included Justice, Busy P, and Mr. Oizo, built a visual identity so loud and so consistent it became a brand unto itself. French electronic music's design output has always been more playful and more fashion-adjacent than its German counterpart. Where Berlin communicates through austerity, Paris communicates through attitude. The relationship between French electronic labels and the fashion industry runs deeper than in any other national scene. Ed Banger's graphic language circulated on t-shirts, sneakers, and magazine covers as fluently as on record sleeves. The visual principle: design as cultural currency, not just functional packaging.",
    },
    newyork: {
        title: 'New York',
        body: "L.I.E.S. Records channels the same DIY energy that defined early Detroit, applied to New York's lo-fi underground. Hand-stamped dust jackets, vinyl-first distribution, anti-digital stance. Ron Morelli, a former punk vocalist and record store employee, runs the operation with the conviction that Instagramification is a plague and that a DJ should be heard, not seen. The visual identity is deliberately undesigned: hand-applied ink, inconsistent labeling, the dust jacket as the primary design surface. Dais Records bridges industrial, noise, and techno with deliberately confrontational packaging that echoes Throbbing Gristle's original provocations. The Bunker New York contributes a more restrained, systems-oriented approach to the city's electronic music design. New York's contribution to techno's visual culture is the reassertion of the handmade in a genre increasingly defined by digital precision. L.I.E.S. proves that anti-design, when pursued with commitment, becomes its own design system. The hand stamp is as recognizable as any grid.",
    },
    canada: {
        title: 'Canada',
        body: "Richie Hawtin's Minus and Plus 8 built some of the most branded visual identities in techno. The Plastikman logo, based on a sketch by Californian skateboard artist Ron Cameron, became a subcultural glyph. Ravers worldwide tattooed it as a rite of passage. Hawtin later said the logo became the branding for a tribe: the people who knew were like, you're one of us. The identity system extended across vinyl, CD, DVD, digital releases, and limited editions with consistent design discipline. Minus maintained a specific design aesthetic across its entire catalog, accented with special packaging and promotional products. Plus 8 developed a parallel identity that shared DNA with Minus but maintained its own visual register. NovaMute, Hawtin's collaboration with Daniel Miller's Mute Records, added a transatlantic design dimension. The Canadian contribution is the demonstration that techno's visual identity can function as lifestyle branding without betraying the music's anti-commercial origins. The logo as tribal mark, the catalog as identity system.",
    },
    japan: {
        title: 'Japan',
        body: "Under-documented in English and overdue for serious design attention. Mule Musiq, Op.disc, Sublime Records, and Far East Recording represent a scene with deep engagement with both Detroit's Afrofuturism and Berlin's reductionism, filtered through a distinct graphic sensibility rooted in Japanese design traditions. The sleeve design coming out of Tokyo's electronic music labels carries a particular quality of negative space, typographic restraint, and material sensitivity that has no direct equivalent in European or American techno. Transonic Records and WC Recordings further expand the range. Far East Recording, connected to the legendary DJ Nori, bridges disco, house, and techno with packaging that reflects Japan's deep traditions of considered object design. The Japanese techno visual archive remains one of the significant gaps in the genre's documented history. What documentation exists suggests a scene where the physical record is treated as a craft object, where sleeve design reflects the same attention to material and detail that defines Japanese graphic design broadly. This archive includes it precisely because the gap needs closing.",
    },
    georgia: {
        title: 'Georgia / Eastern Europe',
        body: "Tbilisi's Bassiani and the labels orbiting it represent one of techno's most politically charged design contexts. In a country where club culture became a site of resistance against authoritarian crackdowns on LGBTQ+ communities and civil liberties, visual identity carries weight far beyond aesthetics. The graphic language is direct, urgent, and deliberately confrontational. Bassiani's 2018 police raid, which prompted thousands to protest outside the Georgian parliament, demonstrated that the relationship between techno and its visual identity had material political consequences. Nervmusic Records and Horoom Records document the sonic output of this scene, with sleeve design that tends toward stark, high-contrast imagery reflecting the urgency of the cultural context. Eastern European techno more broadly, from Poland to Romania to Ukraine, has developed visual identities shaped by post-Soviet architecture, economic constraint, and the political charge of public gathering. The contribution is the reminder that techno's visual culture is never purely aesthetic. Design decisions are always made within conditions, and some conditions are more pressured than others.",
    },
    brazil: {
        title: 'São Paulo / South America',
        body: "Brazil's techno scene is one of the fastest-growing in the world, and its design identity is forming in real time. The anchor is D-Edge in São Paulo, open since 2003 and still operating: a black box of 200 LED-laced panels designed by visual artist Muti Randolph, where the architecture itself is an audio-reactive instrument. Renato Cohen, the first Brazilian producer to score a worldwide techno hit with Pontapé on Carl Cox's Intec in 2002, went on to found MASSA Records as a platform for emerging Brazilian talent. Warung Recordings on the southern coast, Noise Music in Belo Horizonte, and newer operations like Heels of Love and Cactunes are building label identities that range from stripped dancefloor functionality to experimental crossover. What makes the Brazilian scene distinct from a design perspective is the tension between international techno conventions and a local graphic sensibility shaped by tropicália, concrete poetry, and São Paulo's own tradition of radical urban typography. Collectives and labels are emerging from university spaces, DIY networks, and club ecosystems simultaneously. The visual language is still being written. This archive documents it while it forms.",
    },
    italy: {
        title: 'Italy',
        body: "Mannequin Records bridges Italo, EBM, and techno with archival design sensibility, building a catalog that functions as both label and historical project. The sleeve design draws on the visual language of early 1980s Italian synth-pop and industrial cassette culture: grainy photography, analog typography, a deliberate lo-fi warmth that distinguishes it from German minimalism. Danza Meccanica connects to Italy's deeper tradition of industrial and experimental electronic music. A lineage that runs from Futurism's typographic experiments and the radical design of Studio Alchimia through to the present. Italy's relationship with electronic music design has always been inflected by the country's broader visual culture: fashion, automotive design, the Memphis Group, Ettore Sottsass. Even underground labels carry a sense of material sophistication that is distinctly Italian. The result is a design language where archival sensibility and aesthetic ambition coexist. Italian techno sleeve design treats the past as living material rather than nostalgic reference, which positions it differently from both Berlin's forward-looking reduction and Detroit's Afrofuturist imagination.",
    },
    manchester: {
        title: 'Manchester',
        body: "Modern Love and Skam operated in the space between techno, ambient, and experimentalism, building visual identities defined by deliberate opacity. Andy Stott, Demdike Stare, and Autechre emerged from or adjacent to this ecosystem. Autechre's long relationship with Warp extended the Sheffield design legacy, but their solo releases pushed further into abstraction. Modern Love's sleeve design favored dark, textured imagery with minimal typographic information: covers that refused to explain themselves, that demanded the listener engage without visual guidance. Skam Records adopted a similarly austere approach, with artwork that often bordered on anti-design. The Manchester contribution to techno's visual culture is the principle that artwork should withhold rather than invite. Where other scenes used design to build identity, brand, or system, Manchester used it to create distance. The visual language communicates nothing except its own refusal to communicate, which in a genre built on anonymity, is perhaps the most honest design position of all.",
    },
};

(function () {
    function init() {
        const carousel = document.getElementById('scenes-carousel');
        const textEl = document.getElementById('scene-text');
        if (!carousel || !textEl) return;

        const titleEl = textEl.querySelector('.scene-title');
        const bodyEl = textEl.querySelector('.scene-body');

        const originals = Array.from(carousel.children);
        const COPIES = 5;
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

        requestAnimationFrame(() => showScene(sceneKeys.indexOf('berlin')));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
