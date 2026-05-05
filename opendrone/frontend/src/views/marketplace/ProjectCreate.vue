<template>
  <div class="wrap" style="max-width:720px">
    <div class="page-label">// {{ editSlug ? 'modifica' : 'nuovo' }} progetto</div>
    <div class="page-title">{{ editSlug ? `Modifica ${form.title || '...'}` : 'Carica un progetto drone' }}</div>
    <div class="page-sub">Tre step: dati base → componenti → file. Pubblicazione dopo l'approvazione admin.</div>

    <div v-if="loadingProject" class="alert info">⏳ Carico progetto...</div>

    <!-- step bar -->
    <div class="stepbar">
      <div class="step" :class="{ done: stepIndex > 0, active: step === 'basic' }"><span class="dot">1</span> Base</div>
      <div class="step-line" :class="{ done: stepIndex > 0 }"></div>
      <div class="step" :class="{ done: stepIndex > 1, active: step === 'bom' }"><span class="dot">2</span> Componenti</div>
      <div class="step-line" :class="{ done: stepIndex > 1 }"></div>
      <div class="step" :class="{ done: stepIndex > 2, active: step === 'files' }"><span class="dot">3</span> File</div>
    </div>

    <!-- ── STEP 1: BASIC ────────────────────────────────────────── -->
    <div v-if="step === 'basic'" class="card">
      <div class="page-label" style="margin-bottom: 6px">Step 1 / 3</div>
      <h3 style="margin-bottom: 14px">Informazioni base</h3>

      <div class="field">
        <label>Nome progetto *</label>
        <input class="input" v-model="form.title" placeholder="es. Quad FPV Racing 5'' v2" />
      </div>

      <div class="field">
        <label>Descrizione breve *</label>
        <input class="input" maxlength="300" v-model="form.short_description" placeholder="In una frase, cosa fa questo drone?" />
      </div>

      <div class="field">
        <label>Descrizione completa *</label>
        <textarea class="textarea" v-model="form.description" rows="6" placeholder="Spiega il design, i casi d'uso, le note di stampa, le compatibilità…"></textarea>
      </div>

      <div class="field-row">
        <div class="field">
          <label>Categoria *</label>
          <select class="select" v-model="form.category">
            <option :value="null">— scegli —</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
          </select>
          <button v-if="!showNewCat" type="button" class="link-btn" @click="showNewCat = true">+ Nuova categoria</button>
          <div v-else class="new-cat-form">
            <div class="ncf-row">
              <input class="input ncf-icon" v-model="newCat.icon" placeholder="📦" maxlength="4" />
              <input class="input ncf-name" v-model="newCat.name" placeholder="Nome categoria" maxlength="100" @keydown.enter.prevent="createCategory" />
            </div>
            <div v-if="newCatError" class="alert danger" style="margin-top:6px; font-size:11px; padding:4px 8px">{{ newCatError }}</div>
            <div class="ncf-actions">
              <button type="button" class="btn-tiny" @click="cancelNewCat">Annulla</button>
              <button type="button" class="btn-tiny primary" :disabled="creatingCat" @click="createCategory">
                {{ creatingCat ? '…' : 'Crea' }}
              </button>
            </div>
          </div>
        </div>
        <div class="field">
          <label>Difficoltà</label>
          <select class="select" v-model="form.difficulty">
            <option value="basic">Base</option>
            <option value="intermediate">Intermedio</option>
            <option value="advanced">Avanzato</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>Use cases (premi Invio)</label>
        <div class="tags-wrap" @click="$refs.tagInput.focus()">
          <span v-for="t in form.use_cases" :key="t" class="tag-pill">
            {{ t }}
            <button type="button" @click.stop="removeTag(t)">✕</button>
          </span>
          <input ref="tagInput" class="tag-input" v-model="tagDraft" @keydown="onTagKey" placeholder="es. fotografia aerea, ispezione…" />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>Peso stimato (g)</label>
          <input class="input" type="number" v-model.number="form.estimated_weight_grams" />
        </div>
        <div class="field">
          <label>Autonomia (min)</label>
          <input class="input" type="number" v-model.number="form.estimated_flight_time_minutes" />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>Payload max (g)</label>
          <input class="input" type="number" v-model.number="form.max_payload_grams" />
        </div>
        <div class="field">
          <label>Raggio operativo (km)</label>
          <input class="input" type="number" step="0.1" v-model.number="form.operating_range_km" />
        </div>
      </div>

      <div class="field">
        <label>Distribuzione</label>
        <div class="price-row">
          <div class="price-opt" :class="{ sel: form.license_type === 'open_source' }" @click="form.license_type = 'open_source'">
            <div class="pn">Open Source</div>
            <div class="pd">Gratuito, libero</div>
          </div>
          <div class="price-opt" :class="{ sel: form.license_type === 'open_royalty' }" @click="form.license_type = 'open_royalty'">
            <div class="pn">Open + Royalty</div>
            <div class="pd">% su ogni ordine</div>
          </div>
          <div class="price-opt" :class="{ sel: form.license_type === 'commercial' }" @click="form.license_type = 'commercial'">
            <div class="pn">Premium</div>
            <div class="pd">Solo a pagamento</div>
          </div>
        </div>
        <div v-if="form.license_type !== 'open_source'" class="royalty-input">
          <span class="royalty-pre">Royalty %</span>
          <input class="input royalty-field" type="number" step="0.5" min="0" max="20" v-model.number="form.royalty_percentage" />
        </div>
      </div>

      <div v-if="error" class="alert danger">{{ error }}</div>

      <div class="submit-row">
        <button class="btn-full primary" :disabled="loading" @click="saveBasic">
          {{ loading ? 'Salvataggio...' : 'Salva e continua →' }}
        </button>
      </div>
    </div>

    <!-- ── STEP 2: BOM ──────────────────────────────────────────── -->
    <div v-else-if="step === 'bom'">
      <div class="card bom-head">
        <div>
          <div class="page-label" style="margin-bottom: 6px">Step 2 / 3</div>
          <h3>Componenti del drone</h3>
          <p class="sub">Aggiungi i componenti per categoria. Le categorie marcate <em class="ess">essenziale</em> sono raccomandate per un drone funzionante.</p>
        </div>
        <div class="bom-totals">
          <div class="tot-line"><span>Totale BOM</span><strong>€{{ bomTotal.toFixed(2) }}</strong></div>
          <div class="progress">
            <div class="progress-bar" :style="{ width: essentialCoverage * 100 + '%' }"></div>
          </div>
          <div class="prog-text">{{ essentialFilled }}/{{ essentialTotal }} categorie essenziali</div>
        </div>
      </div>

      <!-- accordion categorie -->
      <div class="cat-list">
        <div v-for="cat in CATEGORIES" :key="cat.key" class="cat-section" :class="{ open: expandedCat === cat.key, empty: itemsByCat(cat.key).length === 0 }">
          <button class="cat-header" @click="toggleCat(cat.key)">
            <span class="cat-icon">{{ cat.icon }}</span>
            <span class="cat-name">{{ cat.label }}</span>
            <span v-if="cat.essential" class="cat-tag essential">essenziale</span>
            <span class="cat-summary">
              <template v-if="itemsByCat(cat.key).length">
                {{ itemsByCat(cat.key).length }} elem. · €{{ catTotal(cat.key).toFixed(0) }}
              </template>
              <template v-else-if="cat.essential">
                ⚠ vuoto
              </template>
              <template v-else>
                opzionale
              </template>
            </span>
            <span class="cat-arr">{{ expandedCat === cat.key ? '−' : '+' }}</span>
          </button>

          <div v-if="expandedCat === cat.key" class="cat-body">
            <p class="cat-hint">{{ cat.hint }}</p>

            <!-- elementi esistenti -->
            <div v-for="(item, idx) in itemsByCat(cat.key)" :key="`${cat.key}-${idx}`" class="cat-item">
              <div class="ci-main">
                <div class="ci-name">{{ item.component_name }}</div>
                <div class="ci-meta">
                  <span v-if="item.manufacturer">{{ item.manufacturer }}</span>
                  <span v-if="item.model_number">· {{ item.model_number }}</span>
                  <span v-if="item.notes">· {{ item.notes }}</span>
                </div>
              </div>
              <div class="ci-qty">x{{ item.quantity }}</div>
              <div class="ci-price">€{{ item.unit_price_eur }}</div>
              <div class="ci-tot">€{{ (item.unit_price_eur * item.quantity).toFixed(2) }}</div>
              <button class="btn-tiny danger" @click="removeBom(item)">✕</button>
            </div>

            <!-- form aggiunta inline -->
            <div v-if="addingFor === cat.key" class="add-form">
              <div class="field">
                <label>Nome componente *</label>
                <input class="input" v-model="draft.component_name" :placeholder="cat.placeholder" autofocus />
              </div>
              <div class="field">
                <label>Marca</label>
                <div v-if="brandsForCat(cat.key).length" class="brand-grid">
                  <button v-for="b in brandsForCat(cat.key)" :key="b.id"
                          type="button"
                          class="brand-chip"
                          :class="{ sel: draft.brand_id === b.id, partner: b.is_partner }"
                          @click="selectBrand(b)">
                    <span v-if="b.is_partner" class="star">★</span>
                    {{ b.name }}
                  </button>
                  <button type="button" class="brand-chip other" :class="{ sel: !draft.brand_id }" @click="clearBrand">
                    + Altro
                  </button>
                </div>
                <input class="input" v-model="draft.manufacturer"
                       :placeholder="draft.brand_id ? '' : 'Tipa la marca (se non in elenco)…'"
                       :disabled="!!draft.brand_id"
                       :style="{ marginTop: brandsForCat(cat.key).length ? '8px' : '0' }" />
                <p v-if="selectedBrandObj?.is_partner" class="brand-note">
                  ★ Brand partner — link fornitore precompilato.
                </p>
              </div>
              <div class="field">
                <label>Modello</label>
                <input class="input" v-model="draft.model_number" placeholder="RS2207, F40 Pro, Predator V5…" />
              </div>
              <div v-if="cat.spec_fields?.length" class="field-row" :style="{ gridTemplateColumns: `repeat(${cat.spec_fields.length}, 1fr)` }">
                <div v-for="sf in cat.spec_fields" :key="sf.key" class="field">
                  <label>{{ sf.label }}</label>
                  <input class="input" v-model="draft.specs[sf.key]" :placeholder="sf.placeholder" />
                </div>
              </div>
              <div class="field-row">
                <div class="field">
                  <label>Quantità *</label>
                  <input class="input" type="number" min="1" v-model.number="draft.quantity" />
                </div>
                <div class="field">
                  <label>Prezzo unit. (€) *</label>
                  <input class="input" type="number" step="0.01" min="0" v-model.number="draft.unit_price_eur" />
                </div>
              </div>
              <div class="field">
                <label>Link fornitore (opzionale)</label>
                <input class="input" type="url" v-model="draft.supplier_url" placeholder="https://…" />
              </div>

              <div v-if="formError" class="alert danger">{{ formError }}</div>

              <div class="add-form-actions">
                <button class="btn outline" @click="cancelAdd">Annulla</button>
                <button class="btn primary" :disabled="savingItem" @click="confirmAdd(cat)">
                  {{ savingItem ? 'Salvataggio…' : 'Salva componente' }}
                </button>
              </div>
            </div>

            <button v-else class="btn-add" @click="startAdd(cat)">+ Aggiungi {{ cat.label.toLowerCase() }}</button>
          </div>
        </div>
      </div>

      <div v-if="missingEssentials.length && !ignoredMissing" class="alert warn" style="margin-top: 16px">
        ⚠ Mancano componenti essenziali: <strong>{{ missingEssentials.map(c => c.label).join(', ') }}</strong>.
        Puoi pubblicare lo stesso, ma il customer potrebbe non riuscire a costruire il drone.
      </div>

      <div class="submit-row">
        <button class="btn-full outline" @click="step = 'basic'">← Indietro</button>
        <button class="btn-full primary" @click="goFiles">
          {{ missingEssentials.length && !ignoredMissing ? 'Continua comunque →' : 'Continua →' }}
        </button>
      </div>
    </div>

    <!-- ── STEP 3: FILES ────────────────────────────────────────── -->
    <div v-else-if="step === 'files'" class="card">
      <div class="page-label" style="margin-bottom: 6px">Step 3 / 3</div>
      <h3 style="margin-bottom: 14px">Copertina e file</h3>

      <!-- Cover image -->
      <div class="page-label" style="margin: 16px 0 6px">Immagine di copertina</div>
      <p class="sub" style="margin-bottom: 12px">Una bella foto del drone (anche un render). Sarà la prima cosa che vede il customer.</p>

      <div v-if="coverImage" class="cover-preview">
        <img :src="coverImage.file" alt="cover" />
        <div class="cover-actions">
          <button class="btn outline" @click="removeCover">Rimuovi</button>
        </div>
      </div>

      <div v-else
            class="dropzone cover-drop"
            :class="{ drag: dragOverCover, has: stagedCover }"
            @dragover.prevent="dragOverCover = true"
            @dragleave="dragOverCover = false"
            @drop.prevent="onCoverDrop"
            @click="$refs.coverIn.click()">
        <input ref="coverIn" type="file" accept="image/*" style="display:none" @change="onCoverSel" />
        <div class="drop-icon">📷</div>
        <div class="drop-title">Carica copertina</div>
        <div class="drop-sub">Trascina o clicca per selezionare</div>
        <div class="drop-fmts">
          <span class="fmt">JPG</span>
          <span class="fmt">PNG</span>
          <span class="fmt">WEBP</span>
        </div>
      </div>

      <div v-if="uploadingCover" class="alert info" style="margin-top: 8px">
        ⏳ Caricamento copertina in corso...
      </div>

      <!-- File 3D / altri -->
      <div class="page-label" style="margin: 24px 0 6px">File 3D e documenti</div>
      <p class="sub" style="margin-bottom: 12px">STL, OBJ, 3MF e altri allegati. La validazione STL parte automaticamente alla pubblicazione.</p>

      <div class="dropzone"
            :class="{ drag: dragOver, has: stagedFile }"
            @dragover.prevent="dragOver = true"
            @dragleave="dragOver = false"
            @drop.prevent="onDrop"
            @click="$refs.fileIn.click()">
        <input ref="fileIn" type="file" accept=".stl,.obj,.step,.3mf,.zip" style="display:none" @change="onFileSel" />
        <div class="drop-icon">⬡</div>
        <div class="drop-title">Trascina il file qui</div>
        <div class="drop-sub">oppure clicca per selezionare</div>
        <div class="drop-fmts">
          <span class="fmt">STL</span>
          <span class="fmt">OBJ</span>
          <span class="fmt">3MF</span>
          <span class="fmt">STEP</span>
          <span class="fmt">ZIP</span>
        </div>
      </div>

      <div v-if="uploading" class="alert info" style="margin-top: 8px">
        ⏳ Caricamento file in corso...
      </div>

      <div v-if="nonCoverFiles.length" style="margin-top: 18px">
        <div class="page-label" style="margin-bottom: 8px">File caricati ({{ nonCoverFiles.length }})</div>
        <div v-for="f in nonCoverFiles" :key="f.id" class="uploaded-row">
          <span class="file-type">{{ f.file_type.toUpperCase() }}</span>
          <span class="file-name">{{ f.filename }}</span>
          <span class="file-size">{{ f.file_size_bytes ? (f.file_size_bytes / 1024).toFixed(0) + ' KB' : '' }}</span>
        </div>
      </div>

      <div v-if="publishError" class="alert danger" style="margin-top: 14px">{{ publishError }}</div>

      <div v-if="published" class="success-box">
        <div class="si">✓</div>
        <div class="st">Progetto inviato per validazione</div>
        <div class="ss">Sarà visibile nel marketplace dopo l'approvazione admin (max 24h).</div>
        <router-link :to="`/projects/${createdProject.slug}`" class="btn primary" style="margin-top: 14px">Apri il progetto</router-link>
      </div>

      <div v-else class="submit-row">
        <button class="btn-full outline" @click="step = 'bom'">← Indietro</button>
        <!-- bottone contestuale in base allo stato corrente -->
        <button v-if="isPublishable" class="btn-full primary" :disabled="publishing" @click="publish">
          {{ publishing ? 'Pubblicazione...' : (createdProject?.status === 'rejected' ? 'Ripubblica →' : 'Pubblica progetto →') }}
        </button>
        <router-link v-else-if="createdProject?.status === 'published'" :to="`/projects/${createdProject.slug}`" class="btn-full primary">
          ✓ Vai al progetto live →
        </router-link>
        <div v-else-if="['pending_validation','pending_review'].includes(createdProject?.status)" class="alert info" style="flex:1; margin: 0; text-align: center">
          ⏳ In attesa di approvazione. Le modifiche sono salvate.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marketplaceApi } from '@/api/marketplace'
import { useToastStore } from '@/stores/toast'

const route = useRoute()
const toast = useToastStore()
const editSlug = computed(() => route.params.slug || null)
const loadingProject = ref(false)
const step = ref('basic')
const stepIndex = computed(() => ({ basic: 0, bom: 1, files: 2 }[step.value]))
// Pubblicabile solo se draft o rejected (o nuovo progetto senza createdProject)
const isPublishable = computed(() => {
  if (!createdProject.value) return true  // nuovo progetto
  return ['draft', 'rejected'].includes(createdProject.value.status)
})

// ─── component category taxonomy ───
const CATEGORIES = [
  { key: 'frame', label: 'Telaio', icon: '🔩', essential: true,
    placeholder: 'es. Frame 5" stampato in PETG',
    hint: 'Il telaio principale del drone, di solito stampato 3D.',
    default_qty: 1, spec_fields: [] },
  { key: 'motor', label: 'Motori', icon: '⚡', essential: true,
    placeholder: 'es. Motore brushless 2207 1750KV',
    hint: 'Motori brushless. Per un quadricottero servono 4. Indica KV e size.',
    default_qty: 4,
    spec_fields: [
      { key: 'kv', label: 'KV', placeholder: '1750' },
      { key: 'size', label: 'Size', placeholder: '2207' },
    ] },
  { key: 'esc', label: 'ESC', icon: '🔌', essential: true,
    placeholder: 'es. ESC 45A 4-in-1 BLHeli_32',
    hint: 'Electronic Speed Controller: 4-in-1 (1 unità) o 4 separati.',
    default_qty: 1,
    spec_fields: [
      { key: 'amps', label: 'Ampere', placeholder: '45' },
      { key: 'type', label: 'Tipo', placeholder: '4-in-1' },
    ] },
  { key: 'fc', label: 'Flight Controller', icon: '🎮', essential: true,
    placeholder: 'es. SpeedyBee F7 V3',
    hint: 'Il "cervello" del drone. Indica MCU e dimensione di mounting.',
    default_qty: 1,
    spec_fields: [
      { key: 'mcu', label: 'MCU', placeholder: 'F7' },
      { key: 'mount', label: 'Mounting', placeholder: '30.5x30.5' },
    ] },
  { key: 'rx', label: 'Ricevitore (RX)', icon: '📡', essential: true,
    placeholder: 'es. RadioMaster RP3 ELRS',
    hint: 'Compatibile col radiocomando del cliente. Indica il protocollo.',
    default_qty: 1,
    spec_fields: [
      { key: 'protocol', label: 'Protocollo', placeholder: 'ELRS 2.4GHz' },
    ] },
  { key: 'battery', label: 'Batteria (LiPo)', icon: '🔋', essential: true,
    placeholder: 'es. CNHL 1500mAh 6S 100C',
    hint: 'Specifica celle in serie (S) e capacità in mAh.',
    default_qty: 1,
    spec_fields: [
      { key: 'cells', label: 'Celle (S)', placeholder: '6S' },
      { key: 'mah', label: 'mAh', placeholder: '1500' },
    ] },
  { key: 'prop', label: 'Eliche', icon: '🌀', essential: true,
    placeholder: 'es. HQProp 5.1x5.1x3 (set 4)',
    hint: 'Set di eliche (4 per quad). Indica size, pitch e numero di pale.',
    default_qty: 4,
    spec_fields: [
      { key: 'size', label: 'Size/pitch', placeholder: '5.1x5.1' },
      { key: 'blades', label: 'Pale', placeholder: '3' },
    ] },
  { key: 'vtx', label: 'VTX (Video TX)', icon: '📺', essential: false,
    placeholder: 'es. RushTank Mini 1.6W',
    hint: 'Per droni FPV. Analog 5.8GHz, DJI O3, HDZero o Walksnail.',
    default_qty: 1,
    spec_fields: [
      { key: 'type', label: 'Tipo', placeholder: 'Analog' },
      { key: 'power', label: 'Potenza', placeholder: '1.6W' },
    ] },
  { key: 'camera', label: 'Camera', icon: '📷', essential: false,
    placeholder: 'es. Foxeer Predator V5',
    hint: 'Camera FPV o HD action cam.',
    default_qty: 1, spec_fields: [] },
  { key: 'antenna', label: 'Antenne', icon: '📶', essential: false,
    placeholder: 'es. TrueRC OCP 5.8GHz',
    hint: 'Antenne VTX e/o RX.',
    default_qty: 2, spec_fields: [] },
  { key: 'gps', label: 'GPS / Compass', icon: '🧭', essential: false,
    placeholder: 'es. Matek M10-5883 GPS+Mag',
    hint: 'Per long range, autonomous, telemetria.',
    default_qty: 1, spec_fields: [] },
  { key: 'hardware', label: 'Hardware', icon: '🔧', essential: false,
    placeholder: 'es. Set viti M3 + capacitor 1000uF',
    hint: 'Minuteria: viti, prop nuts, capacitor, cavi, foam, zip ties.',
    default_qty: 1, spec_fields: [] },
  { key: 'other', label: 'Altro', icon: '📦', essential: false,
    placeholder: 'es. Buzzer, LED, mount accessori',
    hint: 'Tutto ciò che non rientra nelle altre categorie.',
    default_qty: 1, spec_fields: [] },
]

const categories = ref([])  // categorie progetto (uso del drone)
const showNewCat = ref(false)
const creatingCat = ref(false)
const newCatError = ref('')
const newCat = ref({ name: '', icon: '' })
const error = ref('')
const formError = ref('')
const publishError = ref('')
const loading = ref(false)
const savingItem = ref(false)
const uploading = ref(false)
const publishing = ref(false)
const published = ref(false)
const dragOver = ref(false)
const dragOverCover = ref(false)
const stagedFile = ref(null)
const stagedCover = ref(null)
const uploadingCover = ref(false)
const uploadedFiles = ref([])
const coverImage = computed(() => uploadedFiles.value.find(f => f.file_type === 'image' && f.is_public) || null)
const nonCoverFiles = computed(() => uploadedFiles.value.filter(f => f.id !== coverImage.value?.id))
const tagDraft = ref('')
const createdProject = ref(null)

// BOM state
const bomItems = ref([])  // tutti gli items aggiunti
const expandedCat = ref(null)
const addingFor = ref(null)
const ignoredMissing = ref(false)
const draft = ref(blankDraft())

const form = ref({
  title: '',
  short_description: '',
  description: '',
  category: null,
  difficulty: 'basic',
  license_type: 'open_royalty',
  royalty_percentage: 5,
  estimated_weight_grams: 0,
  estimated_flight_time_minutes: 0,
  max_payload_grams: 0,
  operating_range_km: 0,
  use_cases: [],
})

const bomTotal = computed(() =>
  bomItems.value.reduce((s, i) => s + (Number(i.unit_price_eur) || 0) * (Number(i.quantity) || 0), 0)
)
const essentialTotal = computed(() => CATEGORIES.filter(c => c.essential).length)
const essentialFilled = computed(() =>
  CATEGORIES.filter(c => c.essential && itemsByCat(c.key).length > 0).length
)
const essentialCoverage = computed(() =>
  essentialTotal.value ? essentialFilled.value / essentialTotal.value : 0
)
const missingEssentials = computed(() =>
  CATEGORIES.filter(c => c.essential && itemsByCat(c.key).length === 0)
)

function blankDraft() {
  return {
    component_name: '',
    manufacturer: '',
    brand_id: null,
    model_number: '',
    quantity: 1,
    unit_price_eur: 0,
    supplier_url: '',
    specs: {},
  }
}

// brand cache per categoria
const brandsCache = ref({})  // { motor: [...], esc: [...], ... }
function brandsForCat(catKey) {
  return brandsCache.value[catKey] || []
}
const selectedBrandObj = computed(() => {
  if (!draft.value.brand_id) return null
  for (const list of Object.values(brandsCache.value)) {
    const b = list.find(x => x.id === draft.value.brand_id)
    if (b) return b
  }
  return null
})

function selectBrand(b) {
  draft.value.brand_id = b.id
  draft.value.manufacturer = b.name
  if (b.default_supplier_url && !draft.value.supplier_url) {
    draft.value.supplier_url = b.default_supplier_url
  }
}
function clearBrand() {
  draft.value.brand_id = null
  if (selectedBrandObj.value && draft.value.manufacturer === selectedBrandObj.value.name) {
    draft.value.manufacturer = ''
  }
  if (selectedBrandObj.value && draft.value.supplier_url === selectedBrandObj.value.default_supplier_url) {
    draft.value.supplier_url = ''
  }
}

function itemsByCat(key) {
  return bomItems.value.filter(i => i.category === key)
}
function catTotal(key) {
  return itemsByCat(key).reduce((s, i) => s + (Number(i.unit_price_eur) || 0) * (Number(i.quantity) || 0), 0)
}

async function toggleCat(key) {
  if (expandedCat.value === key) {
    expandedCat.value = null
    cancelAdd()
  } else {
    expandedCat.value = key
    cancelAdd()
    if (!brandsCache.value[key]) {
      try {
        const { data } = await marketplaceApi.getBrands(key)
        brandsCache.value[key] = data || []
      } catch {
        brandsCache.value[key] = []
      }
    }
  }
}

function startAdd(cat) {
  addingFor.value = cat.key
  draft.value = { ...blankDraft(), quantity: cat.default_qty || 1 }
  formError.value = ''
}
function cancelAdd() {
  addingFor.value = null
  formError.value = ''
}

async function confirmAdd(cat) {
  if (!draft.value.component_name?.trim()) {
    formError.value = 'Inserisci il nome del componente.'
    return
  }
  if (!(draft.value.unit_price_eur >= 0)) {
    formError.value = 'Prezzo non valido.'
    return
  }
  if (!(draft.value.quantity > 0)) {
    formError.value = 'Quantità deve essere almeno 1.'
    return
  }
  formError.value = ''
  savingItem.value = true

  // formatta specs in note leggibili
  const specsText = cat.spec_fields
    .map(sf => draft.value.specs[sf.key]?.trim())
    .filter(Boolean)
    .map((v, i) => `${cat.spec_fields[i].label}: ${v}`)
    .join(' · ')

  const payload = {
    component_name: draft.value.component_name.trim(),
    manufacturer: draft.value.manufacturer || '',
    brand: draft.value.brand_id || null,
    model_number: draft.value.model_number || '',
    quantity: draft.value.quantity,
    unit_price_eur: draft.value.unit_price_eur,
    supplier_url: draft.value.supplier_url || '',
    notes: specsText,
    category: cat.key,
  }

  try {
    const { data } = await marketplaceApi.addBOMItem(createdProject.value.slug, payload)
    bomItems.value.push(data)
    cancelAdd()
    toast.show(`✓ ${data.component_name} aggiunto`)
  } catch (e) {
    formError.value = formatErr(e) || 'Errore salvataggio.'
  } finally {
    savingItem.value = false
  }
}

async function removeBom(item) {
  if (!confirm(`Rimuovere "${item.component_name}"?`)) return
  // Per semplicità: chiamata HTTP DELETE a /projects/{slug}/bom/{id}/
  try {
    const client = (await import('@/api/client')).default
    await client.delete(`/projects/${createdProject.value.slug}/bom/${item.id}/`)
    bomItems.value = bomItems.value.filter(i => i.id !== item.id)
    toast.show('Rimosso')
  } catch (e) {
    toast.show('✗ Errore rimozione')
  }
}

function goFiles() {
  if (missingEssentials.value.length && !ignoredMissing.value) {
    ignoredMissing.value = true
    return  // un click conferma, prossimo click prosegue
  }
  step.value = 'files'
}

// ─── tag helpers ───
function onTagKey(e) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    const v = tagDraft.value.trim().replace(/,/g, '')
    if (v && !form.value.use_cases.includes(v)) form.value.use_cases.push(v)
    tagDraft.value = ''
  } else if (e.key === 'Backspace' && !tagDraft.value && form.value.use_cases.length) {
    form.value.use_cases.pop()
  }
}
function removeTag(t) {
  form.value.use_cases = form.value.use_cases.filter(x => x !== t)
}

// ─── step 1: save basic ───
async function saveBasic() {
  if (!form.value.title || !form.value.description || !form.value.short_description) {
    error.value = 'Compila titolo, descrizione breve e descrizione completa.'
    return
  }
  if (!form.value.category) {
    error.value = 'Seleziona una categoria.'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      short_description: form.value.short_description,
      category: form.value.category,
      difficulty: form.value.difficulty,
      license_type: form.value.license_type,
      royalty_percentage: form.value.royalty_percentage,
      estimated_weight_grams: form.value.estimated_weight_grams,
      estimated_flight_time_minutes: form.value.estimated_flight_time_minutes,
      max_payload_grams: form.value.max_payload_grams,
      operating_range_km: form.value.operating_range_km,
      use_cases: form.value.use_cases,
    }
    if (createdProject.value) {
      await marketplaceApi.updateProject(createdProject.value.slug, payload)
    } else {
      const { data } = await marketplaceApi.createProject(payload)
      createdProject.value = data
    }
    toast.show('✓ Bozza salvata')
    step.value = 'bom'
  } catch (e) {
    error.value = formatErr(e) || 'Errore nel salvataggio.'
  } finally {
    loading.value = false
  }
}

// ─── step 3: files ───
function onFileSel(e) {
  if (e.target.files[0]) {
    stagedFile.value = e.target.files[0]
    uploadFile()
  }
}
function onDrop(e) {
  dragOver.value = false
  if (e.dataTransfer.files[0]) {
    stagedFile.value = e.dataTransfer.files[0]
    uploadFile()
  }
}
function onCoverSel(e) {
  if (e.target.files[0]) {
    stagedCover.value = e.target.files[0]
    uploadCover()
  }
}
function onCoverDrop(e) {
  dragOverCover.value = false
  if (e.dataTransfer.files[0]) {
    stagedCover.value = e.dataTransfer.files[0]
    uploadCover()
  }
}

async function uploadCover() {
  if (!stagedCover.value || !createdProject.value) return
  uploadingCover.value = true
  try {
    const fd = new FormData()
    fd.append('file', stagedCover.value)
    fd.append('filename', stagedCover.value.name)
    fd.append('file_type', 'image')
    fd.append('is_public', 'true')
    const { data } = await marketplaceApi.uploadFile(createdProject.value.slug, fd)
    uploadedFiles.value.push(data)
    stagedCover.value = null
    toast.show('✓ Copertina caricata')
  } catch (e) {
    console.error('[uploadCover] errore:', e.response?.data || e)
    const msg = e.response?.data?.detail
        || JSON.stringify(e.response?.data || {})
        || e.message
    toast.show('✗ Errore copertina: ' + msg)
  } finally {
    uploadingCover.value = false
  }
}

async function removeCover() {
  if (!coverImage.value) return
  if (!confirm('Rimuovere la copertina?')) return
  try {
    const client = (await import('@/api/client')).default
    await client.delete(`/projects/${createdProject.value.slug}/files/${coverImage.value.id}/`)
    uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== coverImage.value.id)
    toast.show('Copertina rimossa')
  } catch (e) {
    toast.show('✗ Errore rimozione (endpoint DELETE file non ancora disponibile, rimuovi via admin)')
  }
}

async function uploadFile() {
  if (!stagedFile.value || !createdProject.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', stagedFile.value)
    fd.append('filename', stagedFile.value.name)
    const ext = stagedFile.value.name.split('.').pop().toLowerCase()
    const isImg = stagedFile.value.type.startsWith('image/')
    const isStl = ['stl', 'obj', '3mf'].includes(ext)
    fd.append('file_type', isImg ? 'image' : (isStl ? 'stl' : 'other'))
    fd.append('is_public', isImg ? 'true' : 'false')
    const { data } = await marketplaceApi.uploadFile(createdProject.value.slug, fd)
    uploadedFiles.value.push(data)
    stagedFile.value = null
    toast.show(`✓ ${data.filename} caricato`)
  } catch (e) {
    console.error('[uploadFile] errore:', e.response?.data || e)
    const msg = e.response?.data?.detail
        || JSON.stringify(e.response?.data || {})
        || e.message
    toast.show('✗ Errore file: ' + msg)
  } finally {
    uploading.value = false
  }
}

async function publish() {
  if (!createdProject.value) return
  publishing.value = true
  publishError.value = ''
  try {
    await marketplaceApi.publishProject(createdProject.value.slug)
    published.value = true
    toast.show('✓ Progetto inviato per revisione')
  } catch (e) {
    publishError.value = formatErr(e) || 'Errore in pubblicazione.'
  } finally {
    publishing.value = false
  }
}

function formatErr(e) {
  if (e.response?.data?.detail) return e.response.data.detail
  if (e.response?.data) {
    const flat = []
    for (const [k, v] of Object.entries(e.response.data)) {
      flat.push(`${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    }
    return flat.join(' · ')
  }
  return ''
}

async function loadCategories() {
  try {
    const { data } = await marketplaceApi.getCategories()
    categories.value = data.results || data
  } catch (e) {
    console.error('[ProjectCreate] errore caricamento categorie:', e)
  }
}

function cancelNewCat() {
  showNewCat.value = false
  newCat.value = { name: '', icon: '' }
  newCatError.value = ''
}

async function createCategory() {
  const name = newCat.value.name.trim()
  if (name.length < 2) {
    newCatError.value = 'Nome troppo corto'
    return
  }
  if (categories.value.some(c => c.name.toLowerCase() === name.toLowerCase())) {
    newCatError.value = 'Categoria già esistente'
    return
  }
  newCatError.value = ''
  creatingCat.value = true
  try {
    const { data } = await marketplaceApi.createCategory({
      name,
      icon: newCat.value.icon.trim() || '📦',
    })
    categories.value.push(data)
    categories.value.sort((a, b) => a.name.localeCompare(b.name))
    form.value.category = data.id
    cancelNewCat()
    toast.show(`✓ Categoria "${data.name}" creata`)
  } catch (e) {
    newCatError.value = formatErr(e) || 'Errore creazione categoria'
  } finally {
    creatingCat.value = false
  }
}

async function loadProjectForEdit(slug) {
  if (!slug) return
  loadingProject.value = true
  try {
    const { data } = await marketplaceApi.getProject(slug)
    console.info('[ProjectCreate] edit mode — progetto caricato:', data.title, 'status:', data.status)
    createdProject.value = data
    // Mutiamo i campi del form senza sostituire l'oggetto (preserva reattività v-model)
    form.value.title = data.title || ''
    form.value.short_description = data.short_description || ''
    form.value.description = data.description || ''
    form.value.category = data.category || null
    form.value.difficulty = data.difficulty || 'basic'
    form.value.license_type = data.license_type || 'open_royalty'
    form.value.royalty_percentage = Number(data.royalty_percentage) || 5
    form.value.estimated_weight_grams = data.estimated_weight_grams || 0
    form.value.estimated_flight_time_minutes = data.estimated_flight_time_minutes || 0
    form.value.max_payload_grams = data.max_payload_grams || 0
    form.value.operating_range_km = Number(data.operating_range_km) || 0
    form.value.use_cases = Array.isArray(data.use_cases) ? data.use_cases : []
    bomItems.value = Array.isArray(data.bom_items) ? data.bom_items : []
    uploadedFiles.value = Array.isArray(data.files) ? data.files : []
    if (uploadedFiles.value.length || bomItems.value.length) {
      step.value = bomItems.value.length ? 'files' : 'bom'
    }
    toast.show(`✎ Modifica "${data.title}"`)
  } catch (e) {
    console.error('[ProjectCreate] errore caricamento progetto:', e)
    toast.show('✗ Progetto non trovato o errore di caricamento')
  } finally {
    loadingProject.value = false
  }
}

onMounted(async () => {
  await loadCategories()
  if (editSlug.value) {
    await loadProjectForEdit(editSlug.value)
  }
})
</script>

<style scoped>
.sub { font-size: 13px; color: var(--muted); line-height: 1.5; }

.link-btn {
  background: none;
  border: none;
  color: var(--accent);
  font-family: var(--mono);
  font-size: 11px;
  margin-top: 6px;
  cursor: pointer;
  padding: 0;
}
.link-btn:hover { text-decoration: underline; }

.new-cat-form {
  margin-top: 8px;
  padding: 10px;
  background: var(--surface);
  border: 1px solid rgba(93,255,159,.2);
  border-radius: 8px;
}
.ncf-row { display: grid; grid-template-columns: 60px 1fr; gap: 6px; }
.ncf-icon { text-align: center; font-size: 16px; }
.ncf-actions { display: flex; gap: 6px; justify-content: flex-end; margin-top: 8px; }
.btn-tiny.primary { background: var(--accent); color: #060f0a; border-color: var(--accent); font-weight: 700; }
.btn-tiny.primary:hover { opacity: .9; }
.btn-tiny.primary:disabled { opacity: .5; cursor: not-allowed; }

/* ── stepbar ── */
.stepbar { display: flex; align-items: center; gap: 8px; margin-bottom: 22px; }
.step { display: flex; align-items: center; gap: 8px; font-family: var(--mono); font-size: 12px; color: var(--muted); }
.step .dot { width: 24px; height: 24px; border-radius: 50%; border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-weight: 700; }
.step.active .dot { border-color: var(--accent); color: var(--accent); }
.step.done .dot { background: var(--accent); border-color: var(--accent); color: #060f0a; }
.step.active { color: var(--text); }
.step-line { flex: 1; height: 1px; background: var(--border); }
.step-line.done { background: var(--accent); }

/* ── form base ── */
.tags-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  cursor: text;
  transition: border-color .2s;
  min-height: 42px;
}
.tags-wrap:focus-within { border-color: var(--accent); }
.tag-pill {
  background: rgba(93,255,159,.1);
  border: 1px solid rgba(93,255,159,.25);
  color: var(--accent);
  font-family: var(--mono);
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.tag-pill button { background: none; border: none; color: var(--accent); cursor: pointer; font-size: 12px; padding: 0; opacity: .7; }
.tag-pill button:hover { opacity: 1; }
.tag-input { background: none; border: none; color: var(--text); font-family: var(--mono); font-size: 12px; outline: none; min-width: 100px; flex: 1; }
.tag-input::placeholder { color: var(--muted); }

.price-row { display: flex; gap: 8px; }
.price-opt {
  flex: 1;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all .15s;
  text-align: center;
  background: var(--surface);
}
.price-opt.sel { border-color: var(--accent); background: rgba(93,255,159,.06); }
.price-opt .pn { font-size: 13px; font-weight: 700; }
.price-opt.sel .pn { color: var(--accent); }
.price-opt .pd { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 2px; }
.royalty-input { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
.royalty-pre { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.royalty-field { max-width: 100px; }

.submit-row { display: flex; gap: 10px; margin-top: 22px; }
.submit-row .btn-full { flex: 1; }

/* ── BOM step ── */
.bom-head { display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: start; }
.bom-head h3 { font-size: 18px; font-weight: 800; }
.bom-head .ess { font-style: normal; color: var(--accent); font-family: var(--mono); font-size: 11px; }
.bom-totals { text-align: right; min-width: 180px; }
.tot-line { font-family: var(--mono); font-size: 12px; color: var(--muted); margin-bottom: 6px; }
.tot-line strong { color: var(--accent); font-size: 18px; margin-left: 8px; font-family: var(--font); letter-spacing: -.5px; }
.progress { height: 4px; background: var(--surface); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; margin: 4px 0; }
.progress-bar { height: 100%; background: var(--accent); transition: width .3s; }
.prog-text { font-family: var(--mono); font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

.cat-list { display: flex; flex-direction: column; gap: 8px; }
.cat-section {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color .15s;
}
.cat-section.open { border-color: rgba(93,255,159,.3); }
.cat-section.empty:not(.open) { opacity: .85; }

.cat-header {
  width: 100%;
  background: none;
  border: none;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  color: var(--text);
  font-family: var(--font);
  text-align: left;
}
.cat-icon { font-size: 18px; line-height: 1; }
.cat-name { font-size: 14px; font-weight: 700; }
.cat-tag {
  font-family: var(--mono);
  font-size: 9px;
  padding: 2px 7px;
  border-radius: 10px;
  border: 1px solid;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.cat-tag.essential { color: var(--accent); border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.cat-summary { margin-left: auto; font-family: var(--mono); font-size: 12px; color: var(--muted); }
.cat-arr { color: var(--muted); font-size: 18px; font-family: var(--mono); width: 16px; text-align: center; }

.cat-body { padding: 0 18px 16px; border-top: 1px solid var(--border); }
.cat-hint { font-family: var(--mono); font-size: 11px; color: var(--muted); padding: 12px 0; line-height: 1.5; }

.cat-item {
  display: grid;
  grid-template-columns: 1fr auto auto auto auto;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  align-items: center;
}
.cat-item:last-child { border-bottom: none; }
.ci-name { font-size: 13px; font-weight: 700; }
.ci-meta { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 2px; }
.ci-qty { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.ci-price { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.ci-tot { font-weight: 700; font-size: 13px; color: var(--accent); }

.btn-tiny {
  background: none;
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 3px 9px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 11px;
  font-family: var(--font);
}
.btn-tiny.danger:hover { border-color: var(--danger); color: var(--danger); }

/* ── brand picker ── */
.brand-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.brand-chip {
  font-family: var(--font);
  font-size: 12px;
  padding: 5px 11px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 18px;
  cursor: pointer;
  transition: all .15s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.brand-chip:hover { border-color: var(--muted); }
.brand-chip.partner { border-color: rgba(93,255,159,.2); }
.brand-chip.sel { border-color: var(--accent); background: rgba(93,255,159,.06); color: var(--accent); font-weight: 700; }
.brand-chip.partner.sel { background: rgba(93,255,159,.1); }
.brand-chip .star { color: var(--accent); font-size: 11px; }
.brand-chip.other { border-style: dashed; color: var(--muted); }
.brand-chip.other.sel { border-style: solid; }
.brand-note {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--accent);
  margin-top: 6px;
}

.add-form {
  background: var(--surface);
  border: 1px solid rgba(93,255,159,.2);
  border-radius: 9px;
  padding: 14px;
  margin-top: 12px;
}
.add-form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 6px; }

.btn-add {
  width: 100%;
  margin-top: 10px;
  padding: 10px;
  border-radius: 8px;
  background: none;
  border: 1px dashed var(--border);
  color: var(--muted);
  cursor: pointer;
  font-family: var(--font);
  font-size: 13px;
  transition: all .15s;
}
.btn-add:hover { border-color: var(--accent); color: var(--accent); }

/* ── files step ── */
.cover-preview {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: var(--surface);
  margin-bottom: 14px;
  aspect-ratio: 16 / 9;
}
.cover-preview img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cover-actions {
  position: absolute;
  bottom: 10px;
  right: 10px;
}
.cover-drop {
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.dropzone {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 36px 20px;
  text-align: center;
  cursor: pointer;
  transition: all .2s;
  background: var(--surface);
  position: relative;
  margin-bottom: 14px;
}
.dropzone.drag { border-color: var(--accent); background: rgba(93,255,159,.04); }
.dropzone.has { border-color: rgba(93,255,159,.4); border-style: solid; }
.drop-icon { font-size: 32px; margin-bottom: 10px; opacity: .6; }
.drop-title { font-size: 14px; font-weight: 700; margin-bottom: 5px; }
.drop-sub { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.drop-fmts { display: flex; gap: 6px; justify-content: center; margin-top: 12px; flex-wrap: wrap; }
.fmt { font-family: var(--mono); font-size: 10px; color: var(--muted); background: var(--card); border: 1px solid var(--border); padding: 3px 9px; border-radius: 4px; }

.file-prev {
  display: none;
  align-items: center;
  gap: 12px;
  background: var(--card);
  border: 1px solid rgba(93,255,159,.25);
  border-radius: 9px;
  padding: 12px 16px;
  margin-bottom: 6px;
}
.file-prev.show { display: flex; }
.fi-icon { font-size: 24px; }
.fi-info { flex: 1; }
.fi-name { font-weight: 700; font-size: 13px; }
.fi-size { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 2px; }
.fi-rm { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 16px; }
.fi-rm:hover { color: var(--danger); }

.uploaded-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); }
.file-type { background: var(--surface); border: 1px solid var(--border); color: var(--accent); padding: 3px 10px; border-radius: 4px; font-family: var(--mono); font-size: 10px; font-weight: 700; }
.file-name { flex: 1; font-size: 13px; }
.file-size { font-family: var(--mono); font-size: 11px; color: var(--muted); }

.success-box {
  background: rgba(93,255,159,.06);
  border: 1px solid rgba(93,255,159,.25);
  border-radius: 10px;
  padding: 24px;
  text-align: center;
  margin-top: 20px;
}
.success-box .si { font-size: 36px; margin-bottom: 10px; }
.success-box .st { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.success-box .ss { font-family: var(--mono); font-size: 12px; color: var(--muted); line-height: 1.6; margin-bottom: 14px; }
</style>
