<template>
  <div class="home">
    <!-- ─────── HERO ─────── -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-grid"></div>
      <div class="hero-inner">
        <div class="hero-text">
          <div class="hero-label">// marketplace · open hardware</div>
          <h1 class="hero-title">
            Costruisci il drone <em>che vuoi tu</em>.
          </h1>
          <p class="hero-sub">
            Progetti drone <strong>open source</strong> validati dalla community.
            Scegli un design, lo facciamo stampare e assemblare in Italia.
            Paghi solo i materiali + il lavoro reale.
          </p>
          <div class="hero-actions">
            <router-link to="/projects" class="btn-hero primary">
              <span>Esplora i droni</span>
              <span class="arr">→</span>
            </router-link>
            <router-link to="/register" class="btn-hero outline">Diventa creator</router-link>
          </div>
          <div class="hero-stats">
            <div class="stat">
              <div class="sn">{{ stats.projects }}</div>
              <div class="sl">progetti</div>
            </div>
            <div class="stat">
              <div class="sn">{{ stats.creators }}</div>
              <div class="sl">creator</div>
            </div>
            <div class="stat">
              <div class="sn accent2">−88%</div>
              <div class="sl">vs DJI</div>
            </div>
          </div>
        </div>

        <!-- visuale: drone FPV racer SVG (con easter egg: clicca i 4 motori in
             senso orario partendo da NO per un backflip) -->
        <div class="hero-visual">
          <svg
            viewBox="0 0 320 320"
            class="drone-svg"
            :class="{ flipping: isFlipping }"
            aria-label="Drone quadcopter FPV"
            role="img"
          >
            <defs>
              <radialGradient id="rg1" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#5dff9f" stop-opacity=".22"/>
                <stop offset="100%" stop-color="#5dff9f" stop-opacity="0"/>
              </radialGradient>
              <linearGradient id="armGrad" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0%" stop-color="#5dff9f" stop-opacity=".35"/>
                <stop offset="100%" stop-color="#5dff9f" stop-opacity=".75"/>
              </linearGradient>
              <!-- bagliore arancione battery (FPV vibe) -->
              <radialGradient id="batGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#ff6b35" stop-opacity=".7"/>
                <stop offset="100%" stop-color="#ff6b35" stop-opacity=".15"/>
              </radialGradient>
            </defs>

            <!-- glow di sfondo -->
            <circle cx="160" cy="160" r="150" fill="url(#rg1)"/>

            <!-- arms a X (più spessi e angolati come true frame X-quad) -->
            <g fill="url(#armGrad)" stroke="#5dff9f" stroke-width="1.4" stroke-linejoin="round">
              <!-- braccio NO -->
              <polygon points="148,148 172,172 78,82 64,68 56,76 70,90"/>
              <!-- braccio NE -->
              <polygon points="172,148 148,172 242,82 256,68 264,76 250,90"/>
              <!-- braccio SE -->
              <polygon points="172,172 148,148 242,238 256,252 264,244 250,230"/>
              <!-- braccio SO -->
              <polygon points="148,172 172,148 78,238 64,252 56,244 70,230"/>
            </g>

            <!-- battery sotto il body (FPV LiPo style) -->
            <rect x="138" y="178" width="44" height="22" rx="2" fill="url(#batGrad)" stroke="#ff6b35" stroke-width="1"/>
            <line x1="146" y1="186" x2="174" y2="186" stroke="#ff6b35" stroke-width=".8" opacity=".7"/>
            <line x1="146" y1="192" x2="174" y2="192" stroke="#ff6b35" stroke-width=".8" opacity=".7"/>

            <!-- body centrale: stack FC/ESC + top plate (rettangolare, basso, FPV style) -->
            <rect x="128" y="138" width="64" height="48" rx="4" fill="#0d0d14" stroke="#5dff9f" stroke-width="1.6"/>
            <!-- pattern top-plate (slot) -->
            <line x1="138" y1="148" x2="182" y2="148" stroke="#5dff9f" stroke-width=".7" opacity=".5"/>
            <line x1="138" y1="154" x2="182" y2="154" stroke="#5dff9f" stroke-width=".7" opacity=".5"/>
            <line x1="138" y1="160" x2="182" y2="160" stroke="#5dff9f" stroke-width=".7" opacity=".5"/>

            <!-- 4 viti M3 agli angoli del body -->
            <g fill="#5dff9f" opacity=".7">
              <circle cx="134" cy="144" r="1.4"/>
              <circle cx="186" cy="144" r="1.4"/>
              <circle cx="134" cy="180" r="1.4"/>
              <circle cx="186" cy="180" r="1.4"/>
            </g>

            <!-- FPV camera frontale tilted up -->
            <g transform="translate(160 132) rotate(-15)">
              <rect x="-8" y="-12" width="16" height="14" rx="1.5" fill="#0d0d14" stroke="#5dff9f" stroke-width="1.2"/>
              <circle cx="0" cy="-5" r="3.2" fill="#0d0d14" stroke="#5dff9f" stroke-width="1"/>
              <circle cx="0" cy="-5" r="1.4" fill="#5dff9f" opacity=".9"/>
            </g>

            <!-- VTX antenna posteriore -->
            <line x1="160" y1="186" x2="160" y2="206" stroke="#5dff9f" stroke-width="1.2"/>
            <circle cx="160" cy="208" r="2.2" fill="none" stroke="#5dff9f" stroke-width="1"/>

            <!-- LED strip frontali (verde sui motori frontali) -->
            <circle cx="60" cy="60" r="2" fill="#5dff9f" class="led-front led-no"/>
            <circle cx="260" cy="60" r="2" fill="#5dff9f" class="led-front led-ne"/>
            <!-- LED posteriori (rossi) -->
            <circle cx="60" cy="260" r="2" fill="#ff4f4f" class="led-rear"/>
            <circle cx="260" cy="260" r="2" fill="#ff4f4f" class="led-rear"/>

            <!-- motori (cerchi cliccabili dell'easter egg) -->
            <g fill="#0d0d14" stroke="#5dff9f" stroke-width="2">
              <!-- bell statore esterno + inner ring + click area -->
              <g class="motor-grp" data-pos="NO" @click="onMotorClick('NO')">
                <circle cx="60" cy="60" r="22" class="rotor"/>
                <circle cx="60" cy="60" r="14" fill="none" stroke-width="1" opacity=".5"/>
                <circle cx="60" cy="60" r="2.5" fill="#5dff9f"/>
              </g>
              <g class="motor-grp" data-pos="NE" @click="onMotorClick('NE')">
                <circle cx="260" cy="60" r="22" class="rotor"/>
                <circle cx="260" cy="60" r="14" fill="none" stroke-width="1" opacity=".5"/>
                <circle cx="260" cy="60" r="2.5" fill="#5dff9f"/>
              </g>
              <g class="motor-grp" data-pos="SE" @click="onMotorClick('SE')">
                <circle cx="260" cy="260" r="22" class="rotor"/>
                <circle cx="260" cy="260" r="14" fill="none" stroke-width="1" opacity=".5"/>
                <circle cx="260" cy="260" r="2.5" fill="#5dff9f"/>
              </g>
              <g class="motor-grp" data-pos="SO" @click="onMotorClick('SO')">
                <circle cx="60" cy="260" r="22" class="rotor"/>
                <circle cx="60" cy="260" r="14" fill="none" stroke-width="1" opacity=".5"/>
                <circle cx="60" cy="260" r="2.5" fill="#5dff9f"/>
              </g>
            </g>

            <!-- eliche FPV (2 lame curve per motore) animate -->
            <g stroke="#5dff9f" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".55">
              <g class="prop p1" style="transform-origin: 60px 60px">
                <path d="M 30 60 Q 60 50 90 60"/>
                <path d="M 90 60 Q 60 70 30 60"/>
              </g>
              <g class="prop p2" style="transform-origin: 260px 60px">
                <path d="M 230 60 Q 260 50 290 60"/>
                <path d="M 290 60 Q 260 70 230 60"/>
              </g>
              <g class="prop p3" style="transform-origin: 60px 260px">
                <path d="M 30 260 Q 60 250 90 260"/>
                <path d="M 90 260 Q 60 270 30 260"/>
              </g>
              <g class="prop p4" style="transform-origin: 260px 260px">
                <path d="M 230 260 Q 260 250 290 260"/>
                <path d="M 290 260 Q 260 270 230 260"/>
              </g>
            </g>
          </svg>
        </div>
      </div>
    </section>

    <!-- ─────── COME FUNZIONA ─────── -->
    <section class="how">
      <div class="section-inner">
        <div class="page-label">// come funziona</div>
        <h2 class="section-title">Dal disegno al volo, in quattro passaggi.</h2>
        <p class="section-sub">Il nostro network distribuito unisce designer, makerspace e centri di assemblaggio in tutta Italia.</p>

        <div class="how-steps">
          <div class="step-card" v-for="(s, i) in howSteps" :key="i">
            <div class="step-num">0{{ i + 1 }}</div>
            <div class="step-icon">{{ s.icon }}</div>
            <h3>{{ s.title }}</h3>
            <p>{{ s.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ─────── CATEGORIE ─────── -->
    <section class="cats" v-if="categories.length">
      <div class="section-inner">
        <div class="page-label">// scegli una missione</div>
        <h2 class="section-title">Per ogni esigenza, un drone.</h2>
        <p class="section-sub">Filtra per tipo di volo: dalle gare FPV alle ispezioni industriali.</p>

        <div class="cat-grid">
          <router-link v-for="c in categories.slice(0, 12)" :key="c.id"
            :to="`/projects?category=${c.id}`" class="cat-tile">
            <div class="ct-icon">{{ c.icon || '📦' }}</div>
            <div class="ct-name">{{ c.name }}</div>
          </router-link>
          <router-link to="/projects" class="cat-tile more">
            <div class="ct-icon">→</div>
            <div class="ct-name">Vedi tutto</div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ─────── CAROUSEL PROGETTI RECENTI ─────── -->
    <section class="carousel-sec" v-if="projects.length">
      <div class="section-inner">
        <div class="sec-hd">
          <div>
            <div class="page-label">// ultimi caricati</div>
            <h2 class="section-title">Progetti recenti</h2>
          </div>
          <div class="carousel-controls">
            <button class="circ-btn" @click="scrollCarousel(-1)" aria-label="Indietro">‹</button>
            <button class="circ-btn" @click="scrollCarousel(1)" aria-label="Avanti">›</button>
            <router-link to="/projects" class="btn outline" style="margin-left:8px">Vedi tutti</router-link>
          </div>
        </div>

        <div ref="carouselEl" class="carousel">
          <div v-for="p in projects" :key="p.id" class="carousel-item">
            <ProjectCard :project="p" />
          </div>
        </div>
      </div>
    </section>

    <!-- ─────── PERCHE' OPENDRONE ─────── -->
    <section class="why">
      <div class="section-inner">
        <div class="page-label">// perché opendrone</div>
        <h2 class="section-title">Niente lock-in. Niente sovrapprezzi.</h2>

        <div class="why-grid">
          <div class="why-card">
            <div class="why-icon"><span>⌬</span></div>
            <h3>100% Open Hardware</h3>
            <p>Tutti i progetti includono STL, BOM e schemi. Puoi stamparli, modificarli e forkarli.</p>
          </div>
          <div class="why-card">
            <div class="why-icon"><span>€</span></div>
            <h3>Prezzo onesto</h3>
            <p>Paghi solo i materiali + il lavoro reale di chi stampa e assembla. Nessun marketing premium.</p>
          </div>
          <div class="why-card">
            <div class="why-icon"><span>★</span></div>
            <h3>Community-driven</h3>
            <p>Designer indipendenti e makerspace italiani. Royalty trasparenti, recensioni reali.</p>
          </div>
          <div class="why-card">
            <div class="why-icon"><span>⚡</span></div>
            <h3>Validazione rapida</h3>
            <p>Ogni progetto pubblicato passa controllo tecnico e di conformità EASA prima di andare online.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ─────── CTA FINALE ─────── -->
    <section class="cta">
      <div class="cta-inner">
        <h2>Pronto a volare?</h2>
        <p>Registrati gratis. Ordina il tuo primo drone, oppure pubblica un progetto come designer.</p>
        <div class="cta-buttons">
          <router-link to="/register" class="btn-hero primary">Inizia ora →</router-link>
          <router-link to="/projects" class="btn-hero outline">Sfoglia il catalogo</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marketplaceApi } from '@/api/marketplace'
import ProjectCard from '@/components/ProjectCard.vue'

const projects = ref([])
const categories = ref([])
const stats = ref({ projects: 0, creators: 0 })
const carouselEl = ref(null)

// ─── Easter egg drone backflip ──────────────────────────────────────
// Sequenza segreta in senso orario: NO -> NE -> SE -> SO. Cliccare i 4
// motori in quest'ordine fa scattare un backflip animato. Click sbagliato
// resetta. Niente feedback visivo sul singolo click: easter egg puro.
const SEQUENCE = ['NO', 'NE', 'SE', 'SO']
const sequenceStep = ref(0)
const isFlipping = ref(false)

function onMotorClick(pos) {
  if (isFlipping.value) return // ignora click durante l'animazione
  if (pos === SEQUENCE[sequenceStep.value]) {
    sequenceStep.value++
    if (sequenceStep.value === SEQUENCE.length) {
      triggerBackflip()
    }
  } else {
    // sbagliato: reset, ma se hai cliccato il motore di start (NO) conta come 1
    sequenceStep.value = pos === SEQUENCE[0] ? 1 : 0
  }
}

function triggerBackflip() {
  isFlipping.value = true
  setTimeout(() => {
    isFlipping.value = false
    sequenceStep.value = 0
  }, 1100) // matcha la durata dell'animazione CSS
}

const howSteps = [
  { icon: '✎', title: 'Il designer pubblica', desc: 'Disegnatori indipendenti caricano il loro progetto open source: STL, BOM, schemi cablaggio.' },
  { icon: '⬢', title: 'I nodi locali stampano', desc: 'Makerspace e fab-lab in tutta Italia stampano i pezzi in 3D, vicini a te.' },
  { icon: '⚙', title: 'Centri assemblaggio', desc: 'Tecnici certificati assemblano elettronica, motori, software. Drone collaudato e pronto al volo.' },
  { icon: '✈', title: 'Decolli', desc: 'Ricevi il drone già pronto, oppure scegli il kit DIY se preferisci montarlo tu.' },
]

function scrollCarousel(dir) {
  const el = carouselEl.value
  if (!el) return
  const itemW = el.querySelector('.carousel-item')?.offsetWidth || 260
  el.scrollBy({ left: dir * (itemW + 14) * 2, behavior: 'smooth' })
}

onMounted(async () => {
  try {
    const [projRes, catRes] = await Promise.all([
      marketplaceApi.getProjects({ ordering: '-created_at', page_size: 12 }),
      marketplaceApi.getCategories(),
    ])
    projects.value = projRes.data.results || projRes.data
    stats.value.projects = projRes.data.count ?? projects.value.length
    const designers = new Set()
    projects.value.forEach(p => designers.add(p.designer_name))
    stats.value.creators = designers.size

    categories.value = catRes.data.results || catRes.data
  } catch (e) {
    console.error('[Home] errore caricamento dati:', e)
  }
})
</script>

<style scoped>
.home { display: flex; flex-direction: column; }

/* ───────── HERO ───────── */
.hero {
  position: relative;
  padding: 80px 24px 90px;
  overflow: hidden;
  border-bottom: 1px solid var(--border);
  isolation: isolate;
}
.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 30% 0%, rgba(93,255,159,.10) 0%, transparent 60%),
    radial-gradient(ellipse 60% 60% at 90% 90%, rgba(255,107,53,.06) 0%, transparent 60%);
  z-index: -2;
}
.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(93,255,159,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(93,255,159,.04) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse 60% 60% at 50% 40%, black 30%, transparent 80%);
  z-index: -1;
}
.hero-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 40px;
  align-items: center;
}
.hero-label {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 2.5px;
  text-transform: uppercase;
  margin-bottom: 18px;
}
.hero-title {
  font-family: var(--font-display);
  font-size: clamp(34px, 5.5vw, 60px);
  font-weight: 800;
  letter-spacing: -2px;
  line-height: 1.02;
  margin-bottom: 18px;
}
.hero-title em {
  font-style: normal;
  color: var(--accent);
  position: relative;
}
.hero-title em::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: -2px;
  height: 3px;
  background: var(--accent);
  opacity: .35;
}
.hero-sub {
  color: var(--muted);
  font-size: 16px;
  line-height: 1.7;
  max-width: 520px;
  margin-bottom: 28px;
}
.hero-sub strong { color: var(--text); font-weight: 600; }

.hero-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 36px; }
.btn-hero {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  border-radius: 10px;
  font-family: var(--font);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all .2s;
  text-decoration: none;
}
.btn-hero.primary {
  background: var(--accent);
  color: #060f0a;
  box-shadow: 0 8px 32px rgba(93,255,159,.18);
}
.btn-hero.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(93,255,159,.28);
}
.btn-hero.primary .arr { transition: transform .2s; }
.btn-hero.primary:hover .arr { transform: translateX(4px); }
.btn-hero.outline {
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
}
.btn-hero.outline:hover { border-color: var(--accent); color: var(--accent); }

.hero-stats { display: flex; gap: 44px; }
.stat .sn {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 800;
  color: var(--accent);
  letter-spacing: -1px;
  line-height: 1;
}
.stat .sn.accent2 { color: var(--accent2); }
.stat .sl {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
  margin-top: 6px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

/* drone SVG */
.hero-visual { display: flex; justify-content: center; perspective: 800px; }
.drone-svg {
  width: 100%;
  max-width: 360px;
  height: auto;
  transition: filter .3s;
  filter: drop-shadow(0 18px 30px rgba(93,255,159,.18));
}
.drone-svg.flipping { animation: backflip 1.1s cubic-bezier(.55,.08,.45,.98) forwards; }

/* I motori sono cliccabili (easter egg). Niente cursor: pointer per non
   tradire il segreto, ma diamo aria-label e li rendiamo non-selezionabili. */
.motor-grp {
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* LED frontali pulsano leggermente (vibe "armato") */
.led-front, .led-rear {
  animation: ledPulse 2.4s ease-in-out infinite;
}
.led-front.led-ne { animation-delay: .3s; }
.led-rear { animation-delay: .8s; }
@keyframes ledPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .35; }
}

/* Eliche: spin veloce (FPV racer = motori veloci) */
.prop {
  animation: spin .35s linear infinite;
  transform-box: fill-box;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Backflip: rotateX 360 + leggero "pop" verticale per far sentire il salto */
@keyframes backflip {
  0%   { transform: rotateX(0)    translateY(0); }
  20%  { transform: rotateX(0)    translateY(-12px); }
  80%  { transform: rotateX(360deg) translateY(-12px); }
  100% { transform: rotateX(360deg) translateY(0); }
}

/* ───────── SEZIONI COMUNI ───────── */
.section-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 80px 24px;
}
.section-title {
  font-family: var(--font-display);
  font-size: clamp(24px, 3.5vw, 36px);
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1.15;
  margin-bottom: 12px;
}
.section-sub {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.7;
  max-width: 560px;
  margin-bottom: 40px;
}

/* ───────── COME FUNZIONA ───────── */
.how { background: var(--surface); border-bottom: 1px solid var(--border); }
.how-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.step-card {
  position: relative;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px 22px;
  transition: border-color .2s, transform .2s;
}
.step-card:hover { border-color: rgba(93,255,159,.35); transform: translateY(-2px); }
.step-num {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 1.5px;
}
.step-icon { font-size: 28px; margin: 14px 0 10px; line-height: 1; }
.step-card h3 { font-size: 16px; font-weight: 800; letter-spacing: -.3px; margin-bottom: 8px; }
.step-card p { color: var(--muted); font-size: 13px; line-height: 1.55; }

/* ───────── CATEGORIE ───────── */
.cats { border-bottom: 1px solid var(--border); }
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}
.cat-tile {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 22px 14px;
  text-align: center;
  cursor: pointer;
  transition: all .15s;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.cat-tile:hover {
  border-color: var(--accent);
  background: rgba(93,255,159,.04);
  transform: translateY(-2px);
}
.cat-tile.more {
  background: none;
  border-style: dashed;
  color: var(--muted);
}
.cat-tile.more:hover { color: var(--accent); }
.ct-icon { font-size: 28px; line-height: 1; }
.ct-name {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: -.2px;
  line-height: 1.3;
}

/* ───────── CAROUSEL ───────── */
.carousel-sec { background: var(--surface); border-bottom: 1px solid var(--border); }
.sec-hd {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
  gap: 16px;
  flex-wrap: wrap;
}
.sec-hd .page-label { margin-bottom: 6px; }
.carousel-controls { display: flex; gap: 8px; align-items: center; }
.circ-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  font-size: 22px;
  cursor: pointer;
  transition: all .15s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono);
  line-height: 1;
}
.circ-btn:hover { border-color: var(--accent); color: var(--accent); }

.carousel {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding: 4px 4px 18px;
  margin: 0 -4px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
.carousel::-webkit-scrollbar { height: 6px; }
.carousel::-webkit-scrollbar-track { background: transparent; }
.carousel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
.carousel-item {
  flex: 0 0 280px;
  scroll-snap-align: start;
}

/* ───────── PERCHÉ ───────── */
.why { border-bottom: 1px solid var(--border); }
.why-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.why-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 26px 22px;
  transition: border-color .2s;
}
.why-card:hover { border-color: rgba(93,255,159,.35); }
.why-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(93,255,159,.08);
  border: 1px solid rgba(93,255,159,.25);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-family: var(--font-display);
  font-weight: 800;
  margin-bottom: 16px;
}
.why-card h3 {
  font-size: 16px;
  font-weight: 800;
  letter-spacing: -.3px;
  margin-bottom: 8px;
}
.why-card p { color: var(--muted); font-size: 13px; line-height: 1.6; }

/* ───────── CTA FINALE ───────── */
.cta {
  background: linear-gradient(180deg, transparent 0%, rgba(93,255,159,.04) 100%);
  padding: 100px 24px 120px;
  text-align: center;
}
.cta-inner { max-width: 640px; margin: 0 auto; }
.cta h2 {
  font-family: var(--font-display);
  font-size: clamp(28px, 4.5vw, 44px);
  font-weight: 800;
  letter-spacing: -1.2px;
  line-height: 1.1;
  margin-bottom: 16px;
}
.cta p {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.7;
  margin-bottom: 28px;
}
.cta-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* ───────── RESPONSIVE ───────── */
@media (max-width: 880px) {
  .hero-inner { grid-template-columns: 1fr; gap: 28px; }
  .hero-visual { order: -1; max-width: 280px; margin: 0 auto; }
  .drone-svg { max-width: 240px; }
  .hero { padding: 48px 24px 64px; }
  .how-steps { grid-template-columns: repeat(2, 1fr); }
  .hero-stats { gap: 28px; }
  .stat .sn { font-size: 24px; }
  .section-inner { padding: 56px 24px; }
}
@media (max-width: 480px) {
  .how-steps { grid-template-columns: 1fr; }
  .hero-stats { gap: 22px; }
  .carousel-item { flex: 0 0 240px; }
}
</style>
