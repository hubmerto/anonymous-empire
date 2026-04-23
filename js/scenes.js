/* ============================================
   SCENES — 20 city texts. An infinite photo marquee runs above the prose;
   prev/next arrows step through the text. The carousel and the text are
   independent — the carousel never stops, and photos are not mapped to
   a specific scene.
   ============================================ */

const SCENES = {
    detroit: {
        title: "Detroit",
        lead: "The auto industry collapsed and took the city's middle class with it. What remained were empty factories, cheap rent, and teenagers with access to surplus electronics. Juan Atkins founded Metroplex in 1985. Derrick May launched Transmat in 1986. Kevin Saunderson started KMS in 1987. All three on Gratiot Avenue.",
        body: "Atkins drew the Metroplex logo with a ruler because there was no budget for a designer. Transmat and KMS operated the same way: photocopied sleeves, hand-cut stencils, white labels with no printed artwork at all. The visual poverty was total, but the response was deliberate. Abdul Qadim Haqq and Alan Oldham built two graphic dialects from nothing: Haqq's Afrofuturist mythology for Underground Resistance and Drexciya, Oldham's anime-inflected sci-fi for Transmat. Underground Resistance performed in balaclavas, scratched messages into vinyl run-out grooves, and turned the absence of a marketing budget into an ideology. No portraits, no celebrity, no personality between the listener and the sound. Every other genre in American popular music put the artist's face on the cover. Detroit techno refused. That refusal was shaped by economic constraint before it became a political position, but it became a political position fast. The white label, born from necessity, became a design statement: the record exists without an image because the image was never the point.",
    },
    berlin: {
        title: "Berlin",
        lead: "The Wall fell in November 1989 and left a city full of empty buildings with no clear ownership. Tresor opened in March 1991 inside an abandoned bank vault on Leipziger Strasse. Basic Channel launched in 1993. By the mid-nineties, Berlin had more techno infrastructure than any city on earth.",
        body: "The physical environment dictated the visual vocabulary entirely: metal, concrete, industrial fog, no natural light. You did not need to invent an aesthetic when the architecture provided one. Basic Channel reduced the sleeve to near-zero information. Cryptic lettering, embossed logos barely visible to the eye. No designer credits exist for their output. This was not minimalism as style. It was minimalism as material fact: the sleeve carried only what was structurally necessary. Ostgut Ton's Yusuf Etiman built Berghain's visual identity by refusing to look at what other labels did. Vanja Golubovic redesigned Tresor's visual system from 2014 using Px Grotesk, grid-based layouts, and annual thematic guidelines. PAN moved the other direction entirely, building an algorithmic platform that treats artwork as mutable code. Berlin's post-reunification vacuum gave designers an unprecedented condition: no commercial expectations, no inherited brand language, no market pressure. The city's techno visual culture was built inside the gap between two political systems, in spaces that belonged to neither.",
    },
    belgium: {
        title: "Belgium",
        lead: "Belgium's textile and steel industries left behind cheap warehouse space and a small country with outsized cultural ambition. R&S Records was founded in Ghent in 1983 by Renaat Vandepapeliere and Sabine Maes. Joey Beltram's \"Energy Flash\" came out on R&S in 1990. Fuse Brussels opened in 1994.",
        body: "R&S produced one of the most distinctive visual marks in electronic music: a green triangle bearing a prancing horse silhouette. The label insists the mark is not associated with Ferrari but embodies the freedom of dance. The ambiguity is part of the design. A logo that invites misreading generates conversation. Ian Anderson of The Designers Republic confirmed his studio worked for both Warp and R&S, building a shared visual vernacular across two countries. The mark's cultural reach was proven when Raf Simons featured the R&S logo on oversized t-shirts at Paris Fashion Week SS20. A logo designed for 12-inch vinyl sleeves in Ghent ended up on a runway as cultural citation. From a design perspective, Belgium demonstrates that a small post-industrial economy with strong institutional arts support produces visual marks with disproportionate reach. The country's political complexity, three language communities negotiating shared identity, may explain why its labels invested heavily in symbols that communicate without words.",
    },
    birmingham: {
        title: "Birmingham",
        lead: "The city that built Britain's cars, guns, and jewelry lost its manufacturing base in the 1980s under Thatcher's deindustrialization. Downwards Records was founded by Regis and Female in 1993. The House of God launched at the Que Club the same year. What grew in that vacuum was Europe's hardest techno.",
        body: "The subgenre was severe enough to carry its own name: the Birmingham sound. Surgeon, Sandwell District, and Silent Servant extended the lineage. The graphic language matched the sonic output: stark black-and-white imagery, minimal typography, industrial textures that referenced the city's metalworking past without romanticizing it. Sandwell District, named after a nearby Black Country borough, operated with deliberate anonymity. No artist photos, no press shots, no social media presence. The collective dissolved in 2011 rather than become a brand. Shared studio space with Napalm Death, Godflesh, and Scorn produced a cross-pollination between metal, industrial noise, and techno that is audible in both the music and the sleeve design. From a design perspective, Birmingham proves that post-industrial trauma can produce visual restraint rather than visual excess. The city's graphic output communicates nothing it does not absolutely need to.",
    },
    sheffield: {
        title: "Sheffield",
        lead: "Sheffield's steel industry collapsed in the 1980s, and the post-industrial landscape directly shaped the city's electronic music. Warp Records launched in 1989 from the FON record shop. Forgemasters' \"Track With No Name\" and LFO defined bleep techno. The Designers Republic, founded by Ian Anderson, became the label's visual architect.",
        body: "Anderson and Nick Phillips made a proposal to Warp: choose a colour and make everything that colour. A single Pantone purple became the label's visual signature for a decade. Anderson drew the Warp globe logo from 1950s science fiction and Dan Dare comics. His reasoning: nothing dates so badly as the future, so he looked at futuristic imagery from the past. The Artificial Intelligence compilation in 1992 reframed electronic music as art for headphones. The Designers Republic also created the WipEout video games, carrying techno's graphic language into mainstream culture. Their 1994 Emigre issue remains that publication's best-selling edition and sits in MoMA's permanent collection. Sheffield's bleep techno moment lasted only from 1989 to 1991. But the design legacy endures. From a design perspective, Sheffield proves that post-industrial decline combined with art school infrastructure produces visual language that is simultaneously raw and sophisticated.",
    },
    glasgow: {
        title: "Glasgow",
        lead: "Glasgow's shipbuilding industry had been dying since the 1960s. By the late 1980s the Clydeside yards were mostly silent. The Sub Club opened in 1987 on Jamaica Street and is now the world's longest-running underground dance venue. Soma Quality Recordings launched in 1991. Slam's Pressure nights followed.",
        body: "The Sub Club's survival in a city with no prior electronic music infrastructure is itself a design story: persistence as identity. Soma's catalog, including Slam's \"Positive Education\" and early Daft Punk, developed a visual identity rooted in functional clarity. Clean typography, consistent formatting, a design system built for durability rather than spectacle. The Arches, a venue inside Victorian railway arches, provided the physical context: stone, iron, repetition. From a design perspective, Glasgow demonstrates what happens when post-industrial collapse meets a rock city with no electronic precedent. There was no existing visual language to inherit or reject. Everything had to be built from nothing, and the result was a pragmatic, enduring design system that prioritized catalog logic over individual cover statements. The constraint was cultural as much as economic.",
    },
    frankfurt: {
        title: "Frankfurt",
        lead: "Frankfurt was West Germany's financial capital, and its techno scene operated in deliberate opposition to that identity. The Omen club ran from 1988 to 1998. Sven V\u00e4th founded Eye Q and Harthouse in 1991 and 1992. Force Inc. and Mille Plateaux launched in the same period, fusing techno with theory.",
        body: "Mille Plateaux took its name from Deleuze and Guattari, and the visual output matched: conceptual, text-heavy, argumentative. Sleeve design functioned as intellectual position rather than brand identity. Cocoon Recordings, founded by V\u00e4th in 1999, brought a more polished but still Frankfurt-rooted aesthetic. The city's banking wealth created the political tension that drove the scene underground: techno as refusal of Frankfurt's corporate surface. From a design perspective, Frankfurt demonstrates that opposition to economic power produces a different visual language than absence of economic power. Detroit had nothing and built from zero. Frankfurt had everything around it and built against it. The graphic output is denser, more literate, self-conscious about its own positioning. The sleeves carry theory because the scene defined itself through intellectual resistance.",
    },
    cologne: {
        title: "Cologne",
        lead: "Cologne was West Germany's media capital, home to advertising agencies and design studios. Wolfgang Voigt began releasing experimental techno in the early 1990s under dozens of aliases. Kompakt launched formally in 1998 with Michael Mayer and J\u00fcrgen Paape, codifying minimal techno as both a sound and a visual system.",
        body: "Voigt conceived the dot-matrix aesthetic from Warhol's technique, and Bianca Strauch developed it into a complete corporate identity system. Veronika Unland's Pop Ambient covers, twenty-six editions of ethereal floral imagery since 2001, proved that warmth and systematic precision can coexist. Profan, Kompakt's harder sublabel, introduced darker palettes while maintaining the parent label's structural discipline. Unlike Detroit or Berlin, Cologne's techno labels did not emerge from economic collapse. They emerged from commercial design culture and applied that infrastructure to independent music. The result is the genre's clearest demonstration that a label identity is a design system, not a collection of individual covers. From a design perspective, Cologne is the control group. It shows what happens when techno's visual culture develops without poverty or political rupture as a forcing function. The output is polished, consistent, and professionally managed. Constraint, it turns out, is not just a limitation. It is a material that produces specific visual outcomes.",
    },
    tokyo: {
        title: "Tokyo",
        lead: "Detroit records reached Tokyo's shops in the early 1990s, and local producers responded with a specificity that had no Western equivalent. Ken Ishii signed to R&S and Plus 8 in 1993. Sublime Records launched in 1994. Liquidroom opened the same year, and Jeff Mills recorded there in 1995.",
        body: "But Japan's Fueiho law effectively criminalized dancing after midnight until 2015, pushing the scene underground and shaping a design culture built around discretion rather than spectacle. The sleeve design from Tokyo's labels carries a particular quality of negative space, typographic restraint, and material sensitivity. Far East Recording, connected to DJ Nori, treated the physical record as a craft object with packaging reflecting deep traditions of considered object design. From a design perspective, Tokyo demonstrates what happens when techno's visual language encounters a culture with its own history of reduction and emptiness. The austerity European labels arrived at through economic or political constraint, Japanese design already possessed as inherited tradition. Wabi-sabi, ma, the aesthetics of impermanence and interval. The post-industrial conditions are absent. The restraint comes from an entirely different philosophical framework.",
    },
    stockholm: {
        title: "Stockholm",
        lead: "Sweden's welfare state gave labels access to education, healthcare, and cultural funding that Detroit and Birmingham never had. Cari Lekebusch's Hybrid Productions launched in 1993. Adam Beyer founded Drumcode in 1996. By the 2000s, Drumcode had become arguably the largest techno label in the world. Northern Electronics arrived in 2013.",
        body: "Drumcode built its position through a functional, peak-time aesthetic. The visual identity matches: clean, systematic, designed for scale. The brand operates across vinyl, digital, festival, and merchandise with corporate-level consistency. Northern Electronics, founded by Abdulla Rashim and Varg, introduced a second register: deep, ambient, industrial, with sleeve design that draws on Scandinavian darkness and typographic minimalism. From a design perspective, Stockholm demonstrates that economic stability does not eliminate the possibility of severe visual language. The Scandinavian design tradition of functional austerity produces a different kind of constraint: not material poverty, but cultural expectation. The output is clean because Swedish design culture demands cleanliness, not because there was no money for color. Drumcode's visual system is as disciplined as Underground Resistance's, but the discipline comes from professional tradition rather than political refusal.",
    },
    rome: {
        title: "Rome",
        lead: "Italy's techno scene is one of the most underrecognized in the genre's history. Lory D and Leo Anibaldi began producing in Rome in 1990. ACV Records released material ranking alongside foundational Berlin and Detroit output. Between 1990 and 1993 Rome hosted warehouse raves of twenty thousand people before state suppression.",
        body: "Marco Passarani's Final Frontier label carried the thread through the mid-1990s. Donato Dozzy and Neel's Spazio Disponibile, founded in 2014, represents the contemporary continuation. The graphic language draws on Italy's surplus of design history: Futurism's typographic experiments, Studio Alchimia's radical design, the Memphis Group, automotive and fashion culture. Even underground labels carry a sense of material sophistication that is distinctly Italian. From a design perspective, Rome demonstrates what happens when techno enters a culture with an existing abundance of visual tradition rather than a deficit. The post-industrial conditions here were regional rather than total, and the cultural response was aesthetic density rather than austerity. Sleeve design treats the past as living material, not nostalgic reference.",
    },
    london: {
        title: "London",
        lead: "London never had one economic condition. It had all of them simultaneously. George Georgiou created the acid house smiley in January 1988 for Danny Rampling's Shoom night. Steve Bicknell's LOST parties began in 1992 as the country's first dedicated techno night. Blueprint Records followed in 1996. Fabric opened in 1999.",
        body: "Rave flyers were survival documents first: phone numbers, radio frequencies, hand-drawn maps to venues that would be raided by morning. Junior Tomlin, Dave Little, and Lawrence Manning created an airbrushed, fluorescent visual language born from urgency. Little's 1988 Spectrum flyer is in the V&A's permanent collection. Tomlin's work has sold at Bonhams. Blueprint, founded by James Ruskin, became London's defining techno imprint with a visual identity built on clean functional design. From a design perspective, London proves that a city without a unified political or economic condition produces a fragmented visual culture. There is no London design system for techno because there is no singular London condition to respond to. The city absorbed, refracted, and recombined everything. That fragmentation is itself a design position.",
    },
    amsterdam: {
        title: "Amsterdam",
        lead: "The Netherlands' techno infrastructure crystallized later than its neighbors. Delsin Records was founded in 1996. Rush Hour opened as both shop and label in 1997. Trouw opened in 2009 inside a former newspaper printing facility. De School followed in 2016. Dekmantel built the city's international gravity from 2007.",
        body: "The city's 24-hour club license framework, introduced in 2013, and ADE provided the institutional support. But the deeper story is the design tradition underneath. From a design perspective, Amsterdam demonstrates what happens when Dutch functionalism, De Stijl, and Rietveld meet independent music. The output is systematic before it is expressive. Form follows catalog. Delsin applied consistent typography and restrained color palettes emphasizing the catalog as a unified body of work. The contribution is less about individual visual statements and more about proving that long-term catalog management, the work of making five hundred records look like they belong together, is itself a design discipline shaped by a country where order is cultural infrastructure.",
    },
    munich: {
        title: "Munich",
        lead: "Munich is the wealthiest major city in Germany, and its techno history runs deeper than any single label. Ultraschall operated from 1994 to 2003 in a former airport canteen, rivaling Tresor in German techno mythology. Disko B launched in 1993. Gigolo Records followed in 1996. Ilian Tape arrived in 2007.",
        body: "Founded by Dario and Marco Zenker, Ilian Tape became the scene's defining visual statement. Since catalog number IT020, all artwork has been created by Bettina Zenker, the founders' mother. Original oil paintings on canvas for each release. No templates, no grid system, no typographic formula. Each cover is a unique physical object before it becomes a printed sleeve. When the label withdrew its entire catalog from Spotify to protest streaming royalty structures, the gesture was consistent: artwork belongs on a physical object, not a thumbnail. From a design perspective, Munich proves that economic comfort does not automatically produce corporate design. Ilian Tape chose handmade singularity in a genre dominated by systematic repetition. The commitment to one artist painting one canvas per release is a political position about labor, value, and what a record is worth.",
    },
    leipzig: {
        title: "Leipzig",
        lead: "Leipzig holds the title for East Germany's most durable techno infrastructure outside Berlin. Distillery opened in September 1992 inside a former Connewitz brewery. It hosted Jeff Mills, Carl Craig, Richie Hawtin, and Ricardo Villalobos across three decades. The city's post-reunification trajectory was harsher and slower than Berlin's.",
        body: "Property remained cheaper longer. The creative infrastructure was thinner. What survived did so through persistence rather than spectacle. Institut f\u00fcr Zukunft extends the contemporary scene. The graphic output reflects the conditions: functional, understated, built for longevity rather than attention. Leipzig never developed a label ecosystem to rival Berlin or Cologne, but its club culture produced a visual language of durability. Posters, flyers, and event branding accumulated over decades into a quiet archive of continuity. From a design perspective, Leipzig demonstrates that sustained operation under economic pressure, without major label or media infrastructure, produces a visual identity defined by endurance. The aesthetic is not austere by ideology or fashion. It is austere because the resources were never abundant enough to permit excess, and the scene lasted long enough for that austerity to become legible as commitment.",
    },
    madrid: {
        title: "Madrid",
        lead: "Spain's actual techno capital is not Barcelona. It is Madrid. Oscar Mulero began DJing in 1988. The Omen Club opened in 1994. The scene emerged from the post-Franco Movida Madrile\u00f1a cultural explosion of the 1980s, which incubated a transition from EBM, goth, and industrial music into techno.",
        body: "PoleGroup, founded in 2004 by Mulero with Reeko, Exium, and Christian W\u00fcnsch, codified the distinctive Spanish techno sound: dark, hypnotic, industrial. Warm Up Recordings, operating since 2000, and the Fabrik mega-club completed the infrastructure. The graphic language of PoleGroup and its orbit is severe: monochrome, tightly controlled typography, industrial imagery that references both the city's concrete periphery and the political weight of post-dictatorship cultural production. From a design perspective, Madrid demonstrates that political liberation produces visual severity rather than visual celebration. The Movida was exuberant. What came after, in techno, was disciplined. The graphic output of Spanish techno labels communicates control, precision, and a refusal of the decorative that echoes Detroit's original position. The constraint here is not economic. It is ideological, shaped by a generation that understood exactly what freedom cost and chose not to waste it on surfaces.",
    },
    tbilisi: {
        title: "Tbilisi",
        lead: "Tbilisi's techno scene is the most politically charged in the world. Bassiani opened in 2015 inside a disused swimming pool under Dinamo Arena stadium. Khidi provided the harder industrial counterpart. On 12 May 2018, Georgian special forces raided Bassiani and Caf\u00e9 Gallery. Thousands gathered at Parliament in response.",
        body: "DJs played to the crowd. The Prime Minister resigned that June. The graphic language of this scene is direct, urgent, and deliberately confrontational. High-contrast imagery, stark typography, design that communicates under pressure because the conditions surrounding production include state violence. The club bans Russian citizens and closed in protest of Georgia's 2024 anti-LGBTQ+ legislation. Nervmusic and Horoom Records document the sonic output with sleeve design reflecting the urgency of the context. From a design perspective, Tbilisi proves that techno's visual culture is never purely aesthetic. When the stakes of cultural production include physical safety, design choices carry weight beyond style. The stark contrasts, the refusal of decorative softness, the directness: these are not trend decisions. They are responses to a political reality where the act of gathering is itself contested, and the visual identity must function as both invitation and resistance.",
    },
    kyiv: {
        title: "Kyiv",
        lead: "Kyiv's techno scene emerged directly from revolution. Closer opened in 2013 inside a former ribbon factory in Podil. CXEMA raves launched in 2014 after Maidan, occupying post-industrial locations across the city. K41 opened in 2019 in a former brewery as a dedicated queer safe space. Then came February 2022.",
        body: "The scene did not stop. K41 reopened as a non-profit, raising over \u00a3700,000 for military and LGBTQ+-inclusive battalion supplies. Veterans attend. Raves occur during air-raid sirens. The graphic language of Kyiv's techno is shaped by wartime conditions that no other scene has faced. Visual identity must function in a context where the venue might not exist next month, where the audience might be called up, where the design must communicate both defiance and care. From a design perspective, Kyiv represents the most extreme case of political context determining visual output in the genre's entire history. The design is urgent not by choice but by necessity. Every poster, every flyer, every social media asset operates under the understanding that cultural production during active conflict is itself a political act. The visual language carries that pressure without decorating it.",
    },
    warsaw: {
        title: "Warsaw",
        lead: "Poland's techno scene is one of post-2015 Europe's most politically active. Bruta\u017c was founded in 2012 by Jacek Sienkiewicz. The Oramics collective centers women, queer, and non-binary artists. VTSS became the international export. Jasna 1, Smolna, and Pog\u0142os provide club infrastructure against the PiS-era right-wing government.",
        body: "Awareness Teams and feminist, trans, and non-binary safe-space programming were built into the operational fabric of venues and events. The graphic language reflects this political positioning: bold, direct, designed to communicate inclusion and resistance simultaneously. Warsaw's techno visual identity does not perform the industrial austerity of Berlin or the corporate discipline of Stockholm. It performs solidarity. From a design perspective, Warsaw demonstrates that contemporary techno scenes in politically contested environments produce visual language that functions as organizing tool as much as aesthetic object. The design must welcome specific communities while signaling opposition to specific political forces. This dual function, invitation and resistance in the same visual gesture, is a design challenge that scenes operating in stable democracies never face. The output is shaped by political necessity, not stylistic preference.",
    },
    saopaulo: {
        title: "S\u00e3o Paulo",
        lead: "Brazil's techno scene formed inside the contradictions of a rapidly urbanizing economy. D-Edge opened in 2003 in S\u00e3o Paulo. Renato Cohen scored the first worldwide Brazilian techno hit with Pontap\u00e9 in 2002. Mamba Negra, ODD, and Gop Tun now anchor a scene growing faster than any in South America.",
        body: "Mamba Negra built a label and party series centering Black, queer, and femme artists in a country where those identities carry real physical risk. ODD operates as both venue and curatorial platform, programming techno alongside experimental and bass music with a visual identity rooted in S\u00e3o Paulo's street-level graphic culture. Gop Tun functions as an underground hub where the harder, darker end of Brazilian techno finds its audience. The poverty here is different from Detroit's post-industrial decline. It is the poverty of a developing economy where informal networks, university spaces, and DIY collectives operate alongside commercial infrastructure. The graphic language carries that tension: international techno conventions colliding with tropic\u00e1lia, concrete poetry, and radical urban typography. From a design perspective, Brazil demonstrates what happens when techno develops without deference to European austerity. The identity is political before it is aesthetic, shaped by inequality rather than post-industrial nostalgia.",
    },
    copenhagen: {
        title: "Copenhagen",
        lead: "Copenhagen is a specialist. The city is the global capital of dub techno, the post-Basic Channel subgenre defined by delay, reverb, and reductive structure. Kenneth Christiansen founded the Echocord label in 2001 and Culture Box in 2005. Posh Isolation, operating since 2009, connects to Stockholm's Northern Electronics through shared artists.",
        body: "Echocord has released roughly 100 records from Mikkel Metal, Deadbeat, Fluxion, Quantec, and Rod Modell. Echocord Colour, launched in 2008, provides the harder dancefloor counterpart. The graphic language of Copenhagen's techno is muted, textural, and restrained. Echocord's sleeve design uses washed-out photography, subdued palettes, and minimal typography that mirrors the sonic qualities of the music: everything recedes, nothing demands attention. From a design perspective, Copenhagen demonstrates that extreme genre specialization produces extreme visual consistency. When a scene commits to one sonic register, the graphic output follows. The constraint here is self-imposed: dub techno's sonic reduction dictates visual reduction. The result is one of the most internally coherent design systems in the entire genre, achieved not through poverty or politics but through the discipline of a single aesthetic commitment maintained across two decades.",
    },
};

// City order + photos (ratios locked to each image's natural orientation).
// Folder is "Scenes_Photogrpahs" (preserving the original spelling on disk).
// Interleaved landscape / portrait so adjacent tiles always alternate
// orientation. We have 9 landscape and 11 portrait images; two extra
// portraits are inserted at evenly-spaced points to keep the L/P rhythm
// as close to perfect as possible.
// 9 landscapes + 11 portraits. Interleaved L/P as strictly as possible;
// the 2 surplus portraits are spread far apart so the rhythm reads as
// "one landscape, one portrait" throughout. The track loops seamlessly.
const SCENE_ORDER = [
    { key: 'detroit',    label: 'Detroit',          file: 'Detroit.png',    orient: 'l' },
    { key: 'belgium',    label: 'Belgium', file: 'Brussels.png',   orient: 'p' },
    { key: 'berlin',     label: 'Berlin',           file: 'Berlin.png',     orient: 'l' },
    { key: 'birmingham', label: 'Birmingham',       file: 'Birmingham.png', orient: 'p' },
    { key: 'cologne',    label: 'Cologne',          file: 'Cologne.png',    orient: 'l' },
    { key: 'sheffield',  label: 'Sheffield',        file: 'Sheffield.png',  orient: 'p' },
    { key: 'stockholm',  label: 'Stockholm',        file: 'Stockholm.png',  orient: 'l' },
    { key: 'glasgow',    label: 'Glasgow',          file: 'Glasgow.png',    orient: 'p' },
    { key: 'rome',       label: 'Rome',             file: 'Rome.png',       orient: 'l' },
    { key: 'frankfurt',  label: 'Frankfurt',        file: 'Frankfurt.png',  orient: 'p' },
    { key: 'amsterdam',  label: 'Amsterdam',        file: 'Amsterdam.png',  orient: 'l' },
    { key: 'tokyo',      label: 'Tokyo',            file: 'Tokyo.png',      orient: 'p' },
    { key: 'madrid',     label: 'Madrid',           file: 'Madrid.png',     orient: 'l' },
    { key: 'london',     label: 'London',           file: 'London.png',     orient: 'p' },
    { key: 'kyiv',       label: 'Kyiv',             file: 'Kyiv.png',       orient: 'l' },
    { key: 'tbilisi',    label: 'Tbilisi',          file: 'Tbilisi.png',    orient: 'p' },
    { key: 'warsaw',     label: 'Warsaw',           file: 'Warsaw.png',     orient: 'l' },
    { key: 'munich',     label: 'Munich',           file: 'Munich.png',     orient: 'p' },
    { key: 'saopaulo',   label: 'Sao Paulo',        file: 'Sao Paulo.png',  orient: 'l' },
    { key: 'leipzig',    label: 'Leipzig',          file: 'Leipzig.png',    orient: 'p' },
    { key: 'chicago',    label: 'Chicago',          file: 'Chicago.png',    orient: 'l', photoOnly: true },
    { key: 'copenhagen', label: 'Copenhagen',       file: 'Copenhagen.png', orient: 'p' },
];

(function () {
    function init() {
        var photoTrack = document.getElementById('scenes-photo-track');
        var nameTrack  = document.getElementById('scenes-name-track');
        var textEl     = document.getElementById('scene-text');
        if (!textEl) return;

        var titleEl = textEl.querySelector('.scene-title');
        var bodyEl  = textEl.querySelector('.scene-body');

        function render(key) {
            var s = SCENES[key];
            if (!s) return;
            textEl.classList.add('fading');
            textEl.classList.remove('expanded'); // collapse whenever scene changes
            var moreBtn = document.getElementById('scene-more');
            if (moreBtn) moreBtn.textContent = '+';
            setTimeout(function(){
                titleEl.textContent = s.title;
                // Clear body, rebuild with a lead + rest span so mobile can
                // weight them differently and toggle "read more" on the rest.
                while (bodyEl.firstChild) bodyEl.removeChild(bodyEl.firstChild);
                if (s.lead) {
                    var lead = document.createElement('span');
                    lead.className = 'scene-lead';
                    lead.textContent = s.lead;
                    bodyEl.appendChild(lead);
                    bodyEl.appendChild(document.createTextNode(' '));
                }
                var rest = document.createElement('span');
                rest.className = 'scene-rest';
                rest.textContent = s.body || '';
                bodyEl.appendChild(rest);
                textEl.classList.remove('fading');
            }, 180);
            // Highlight active name in both marquee halves.
            document.querySelectorAll('.scene-name-btn').forEach(function(b){
                b.classList.toggle('active', b.dataset.key === key);
            });
        }

        var moreBtn = document.getElementById('scene-more');
        if (moreBtn) {
            moreBtn.addEventListener('click', function(){
                var expanded = textEl.classList.toggle('expanded');
                moreBtn.textContent = expanded ? '−' : '+';
            });
        }

        // Initial content — first scene
        render(SCENE_ORDER[0].key);
        var currentKey = SCENE_ORDER[0].key;

        // Track the active scene so prev/next know where we are.
        var _render = render;
        render = function(key){ currentKey = key; _render(key); };

        function step(dir){
            var keys = SCENE_ORDER.filter(function(s){ return !s.photoOnly; }).map(function(s){ return s.key; });
            var i = keys.indexOf(currentKey);
            if (i < 0) i = 0;
            i = ((i + dir) % keys.length + keys.length) % keys.length;
            render(keys[i]);
        }
        var prevBtn = document.getElementById('scene-prev');
        var nextBtn = document.getElementById('scene-next');
        if (prevBtn) prevBtn.addEventListener('click', function(){ step(-1); });
        if (nextBtn) nextBtn.addEventListener('click', function(){ step(1); });

        // ---- photo marquee (scrolls left, slow) ------------------------
        if (photoTrack) {
            function buildPhoto(p){
                var wrap = document.createElement('div');
                wrap.className = 'marquee-item ' + (p.orient === 'l' ? 'is-landscape' : 'is-portrait');
                wrap.dataset.key = p.key;
                var img = document.createElement('img');
                img.src = 'Scenes_Photogrpahs/' + encodeURIComponent(p.file);
                img.alt = p.label;
                img.loading = 'lazy';
                img.draggable = false;
                wrap.appendChild(img);
                wrap.addEventListener('click', function(){ render(p.key); });
                return wrap;
            }
            [0,1].forEach(function(){
                SCENE_ORDER.forEach(function(p){ photoTrack.appendChild(buildPhoto(p)); });
            });
        }

        // ---- name marquee (scrolls right, faster) ----------------------
        if (nameTrack) {
            function buildName(p){
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'scene-name-btn';
                btn.dataset.key = p.key;
                btn.textContent = p.label;
                btn.addEventListener('click', function(){ render(p.key); });
                return btn;
            }
            [0,1].forEach(function(){
                SCENE_ORDER.filter(function(p){ return !p.photoOnly; }).forEach(function(p){
                    nameTrack.appendChild(buildName(p));
                    var sep = document.createElement('span');
                    sep.className = 'scene-name-sep';
                    sep.textContent = '/';
                    nameTrack.appendChild(sep);
                });
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
