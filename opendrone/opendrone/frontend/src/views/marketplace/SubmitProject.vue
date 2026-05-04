<template>
  <div class="wrap" style="max-width: 720px">
    <router-link to="/dashboard" class="back-link">← Torna alla dashboard</router-link>

    <div class="page-label">// carica progetto</div>
    <div class="page-title">Carica un progetto drone</div>
    <div class="page-sub">
      Tre step: dati base → componenti → file. La pubblicazione avverrà dopo l'approvazione dell'admin.
    </div>

    <!-- STEP BAR -->
    <div class="stepbar">
      <div class="step" :class="{ active: step === 1, done: step > 1 }">
        <span class="dot">{{ step > 1 ? '✓' : '1' }}</span> Base
      </div>
      <div class="step-line" :class="{ done: step > 1 }"></div>
      <div class="step" :class="{ active: step === 2, done: step > 2 }">
        <span class="dot">{{ step > 2 ? '✓' : '2' }}</span> Componenti
      </div>
      <div class="step-line" :class="{ done: step > 2 }"></div>
      <div class="step" :class="{ active: step === 3, done: step > 3 }">
        <span class="dot">3</span> File &amp; Invio
      </div>
    </div>

    <!-- REQUIREMENTS BOX (sempre visibile) -->
    <div class="req-box">
      <div class="req-title">⚠ Requisiti per la pubblicazione</div>
      <ul class="req-list">
        <li>File STL o STEP della struttura (frame stampabile in PA12 / PETG / ASA)</li>
        <li>Lista BOM completa con codici componente e prezzi indicativi in €</li>
        <li>Guida di assemblaggio in PDF (italiano o inglese)</li>
        <li>Specifiche tecniche: peso, autonomia, payload, raggio operativo</li>
        <li>Categoria EASA del drone (Open A1 / A2 / A3 o Specific)</li>
        <li class="warn">Il progetto non deve avere finalità militari o di sorveglianza non autorizzata</li>
        <li class="warn">Peso massimo struttura (senza batteria): 25 kg per categoria Open EASA</li>
      </ul>
    </div>

    <!-- ══ STEP 1: BASE ══════════════════════════════════════════ -->
    <div v-if="step === 1" class="card">
      <div class="page-label" style="margin-bottom: 6px">Step 1 / 3</div>
      <h3 style="font-size: 16px; margin-bottom: 16px">Informazioni base</h3>

      <div v-if="errors.length" class="alert danger" style="margin-bottom: 14px">
        <div v-for="e in errors" :key="e">{{ e }}</div>
      </div>

      <div class="field">
        <label>NOME PROGETTO *</label>
        <input class="input" v-model="form.title" placeholder="es. Quad FPV Racing 5'' v2" />
      </div>

      <div class="field">
        <label>DESCRIZIONE BREVE * <span class="hint">(max 300 caratteri)</span></label>
        <input class="input" v-model="form.short_description" maxlength="300" placeholder="In una frase, cosa fa questo drone?" />
      </div>

      <div class="field">
        <label>DESCRIZIONE COMPLETA *</label>
        <textarea class="textarea" v-model="form.description" rows="5"
          placeholder="Spiega il design, i casi d'uso, le note di stampa, le compatibilità..." />
      </div>

      <div class="field-row">
        <div class="field">
          <label>CATEGORIA *</label>
          <select class="select" v-model="form.category">
            <option value="">— scegli —</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>DIFFICOLTÀ</label>
          <select class="select" v-model="form.difficulty">
            <option value="basic">Base</option>
            <option value="intermediate">Intermedio</option>
            <option value="advanced">Avanzato</option>
          </select>
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>PESO STIMATO (g) *</label>
          <input class="input" type="number" v-model.number="form.estimated_weight_grams" placeholder="280" />
        </div>
        <div class="field">
          <label>AUTONOMIA (min) *</label>
          <input class="input" type="number" v-model.number="form.estimated_flight_time_minutes" placeholder="12" />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>PAYLOAD MAX (g)</label>
          <input class="input" type="number" v-model.number="form.max_payload_grams" placeholder="0" />
        </div>
        <div class="field">
          <label>RAGGIO OPERATIVO (km)</label>
          <input class="input" type="number" step="0.1" v-model.number="form.operating_range_km" placeholder="1.5" />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>CATEGORIA EASA</label>
          <select class="select" v-model="form.easa_category">
            <option value="">— non specificata —</option>
            <option value="open_a1">Open A1</option>
            <option value="open_a2">Open A2</option>
            <option value="open_a3">Open A3</option>
            <option value="specific">Specific</option>
          </select>
        </div>
        <div class="field">
          <label>LICENZA</label>
          <select class="select" v-model="form.license_type">
            <option value="open_source">Open Source (gratuito)</option>
            <option value="open_royalty">Open Royalty</option>
            <option value="commercial">Commerciale</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>USE CASES <span class="hint">(premi Invio per aggiungere)</span></label>
        <div class="tags-wrap" @click="$refs.tagInput.focus()">
          <span v-for="t in form.use_cases" :key="t" class="tag-pill">
            {{ t }}
            <button type="button" @click.stop="removeTag(t)">✕</button>
          </span>
          <input ref="tagInput" class="tag-input" v-model="tagDraft"
            @keydown="onTagKey" placeholder="es. fpv, fotografia, consegne..." />
        </div>
      </div>

      <div style="display: flex; justify-content: flex-end; margin-top: 8px">
        <button class="btn primary" @click="goToStep2">Avanti: Componenti →</button>
      </div>
    </div>

    <!-- ══ STEP 2: BOM ═══════════════════════════════════════════ -->
    <div v-else-if="step === 2" class="card">
      <div class="page-label" style="margin-bottom: 6px">Step 2 / 3</div>
      <h3 style="font-size: 16px; margin-bottom: 4px">Lista componenti (BOM)</h3>
      <p class="page-sub" style="margin-bottom: 16px">
        Aggiungi tutti i componenti necessari con modello e prezzo indicativo.
      </p>

      <div class="bom-header">
        <span>Componente</span><span>Modello / codice</span><span>Qtà</span><span>€/pz</span><span></span>
      </div>

      <div v-for="(item, i) in form.bom_items" :key="i" class="bom-row">
        <input class="input sm" v-model="item.component_name" placeholder="Motore brushless" />
        <input class="input sm" v-model="item.model_number" placeholder="BetaFPV 1404" />
        <input class="input sm" type="number" v-model.number="item.quantity" placeholder="4" @input="recalcBom" />
        <input class="input sm" type="number" step="0.01" v-model.number="item.unit_price_eur" placeholder="12.50" @input="recalcBom" />
        <button class="remove-btn" @click="removeBomRow(i)">✕</button>
      </div>

      <button class="btn outline" style="font-size: 12px; margin: 10px 0 16px" @click="addBomRow">
        + Aggiungi componente
      </button>

      <div class="bom-total-bar">
        <span>Costo totale stimato</span>
        <strong>€{{ bomTotal.toFixed(2) }}</strong>
      </div>

      <div style="display: flex; justify-content: space-between; margin-top: 16px">
        <button class="btn outline" @click="step = 1">← Indietro</button>
        <button class="btn primary" @click="step = 3">Avanti: File →</button>
      </div>
    </div>

    <!-- ══ STEP 3: FILE & INVIO ══════════════════════════════════ -->
    <div v-else-if="step === 3" class="card">
      <div class="page-label" style="margin-bottom: 6px">Step 3 / 3</div>
      <h3 style="font-size: 16px; margin-bottom: 4px">File del progetto</h3>
      <p class="page-sub" style="margin-bottom: 16px">
        Carica i file necessari per la revisione. Puoi aggiungerne altri dopo l'approvazione.
      </p>

      <div class="upload-zones">
        <label class="upload-zone" :class="{ uploaded: files.stl }">
          <input type="file" accept=".stl,.step,.stp" @change="onFile($event, 'stl')" style="display:none" />
          <div class="uz-icon">📁</div>
          <div class="uz-title">File STL / STEP *</div>
          <div class="uz-sub" v-if="!files.stl">Clicca o trascina · max 50 MB</div>
          <div class="uz-sub uploaded-name" v-else>✓ {{ files.stl.name }}</div>
        </label>

        <label class="upload-zone" :class="{ uploaded: files.pdf }">
          <input type="file" accept=".pdf" @change="onFile($event, 'pdf')" style="display:none" />
          <div class="uz-icon">📄</div>
          <div class="uz-title">Guida assemblaggio PDF *</div>
          <div class="uz-sub" v-if="!files.pdf">Clicca o trascina · max 20 MB</div>
          <div class="uz-sub uploaded-name" v-else>✓ {{ files.pdf.name }}</div>
        </label>

        <label class="upload-zone" :class="{ uploaded: files.img }">
          <input type="file" accept="image/*" @change="onFile($event, 'img')" style="display:none" />
          <div class="uz-icon">🖼️</div>
          <div class="uz-title">Immagini (copertina, render)</div>
          <div class="uz-sub" v-if="!files.img">Clicca o trascina · JPG/PNG · max 10 MB</div>
          <div class="uz-sub uploaded-name" v-else>✓ {{ files.img.name }}</div>
        </label>
      </div>

      <div class="field" style="margin-bottom: 16px">
        <label>NOTE PER L'ADMIN <span class="hint">(opzionale)</span></label>
        <textarea class="textarea" v-model="form.admin_notes" rows="3"
          placeholder="Eventuali note per il team di revisione..." />
      </div>

      <div class="alert info" style="margin-bottom: 16px">
        Dopo l'invio il progetto passerà in stato <strong>in validazione</strong>.
        Un admin lo esaminerà entro 48h e riceverai una notifica email.
      </div>

      <div style="display: flex; justify-content: space-between">
        <button class="btn outline" @click="step = 2">← Indietro</button>
        <button class="btn primary" :disabled="submitting" @click="doSubmit">
          {{ submitting ? 'Invio in corso...' : 'Invia per approvazione →' }}
        </button>
      </div>
    </div>

    <!-- ══ SUCCESS ═══════════════════════════════════════════════ -->
    <div v-else-if="step === 4" class="card success-card">
      <div class="success-icon">🎉</div>
      <h3>Progetto inviato!</h3>
      <p>
        Il tuo progetto è ora <strong class="status-pending">in validazione</strong>.
        Il team OpenDrone lo esaminerà entro 48 ore lavorative.
      </p>
      <div class="alert warn" style="margin: 16px 0; text-align: left">
        Puoi continuare a modificare il progetto mentre è in revisione accedendo alla sezione
        <em>I miei progetti</em>.
      </div>
      <router-link to="/my-projects" class="btn primary">Vai ai miei progetti →</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marketplaceApi } from '@/api/marketplace'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const step = ref(1)
const submitting = ref(false)
const errors = ref([])
const tagDraft = ref('')

const form = ref({
  title: '',
  short_description: '',
  description: '',
  category: '',
  difficulty: 'basic',
  estimated_weight_grams: null,
  estimated_flight_time_minutes: null,
  max_payload_grams: null,
  operating_range_km: null,
  easa_category: '',
  license_type: 'open_source',
  use_cases: [],
  bom_items: [{ component_name: '', model_number: '', quantity: 1, unit_price_eur: 0 }],
  admin_notes: '',
})

const files = ref({ stl: null, pdf: null, img: null })
const categories = ref([])

const bomTotal = computed(() =>
  form.value.bom_items.reduce((s, i) => s + (i.quantity || 0) * (i.unit_price_eur || 0), 0)
)

/* ── tag helpers ── */
function onTagKey(e) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    const v = tagDraft.value.trim().replace(/,$/, '')
    if (v && !form.value.use_cases.includes(v)) form.value.use_cases.push(v)
    tagDraft.value = ''
  }
  if (e.key === 'Backspace' && !tagDraft.value && form.value.use_cases.length) {
    form.value.use_cases.pop()
  }
}
function removeTag(t) { form.value.use_cases = form.value.use_cases.filter(x => x !== t) }

/* ── BOM helpers ── */
function addBomRow() { form.value.bom_items.push({ component_name: '', model_number: '', quantity: 1, unit_price_eur: 0 }) }
function removeBomRow(i) { form.value.bom_items.splice(i, 1) }
function recalcBom() { /* computed handles it */ }

/* ── file pick ── */
function onFile(e, key) { files.value[key] = e.target.files[0] || null }

/* ── step 1 → 2 validation ── */
function goToStep2() {
  errors.value = []
  if (!form.value.title.trim()) errors.value.push('Il nome del progetto è obbligatorio.')
  if (!form.value.short_description.trim()) errors.value.push('La descrizione breve è obbligatoria.')
  if (!form.value.description.trim()) errors.value.push('La descrizione completa è obbligatoria.')
  if (!form.value.category) errors.value.push('Seleziona una categoria.')
  if (!form.value.estimated_weight_grams) errors.value.push('Inserisci il peso stimato.')
  if (!form.value.estimated_flight_time_minutes) errors.value.push('Inserisci l\'autonomia stimata.')
  if (errors.value.length) return
  step.value = 2
}

/* ── final submit ── */
async function doSubmit() {
  submitting.value = true
  try {
    // 1. Crea il progetto come bozza
    const payload = { ...form.value, status: 'draft' }
    const { data: project } = await marketplaceApi.createProject(payload)

    // 2. Upload file (se presenti)
    for (const [key, file] of Object.entries(files.value)) {
      if (!file) continue
      const fd = new FormData()
      fd.append('file', file)
      fd.append('project', project.id)
      fd.append('file_type', key === 'img' ? 'image' : key === 'pdf' ? 'assembly_guide' : 'cad')
      fd.append('is_public', key === 'img' ? 'true' : 'false')
      await marketplaceApi.uploadFile(fd)
    }

    // 3. Pubblica (manda in pending_validation)
    await marketplaceApi.publishProject(project.slug)

    toast.show('✓ Progetto inviato per validazione!')
    step.value = 4
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore durante l\'invio. Riprova.')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await marketplaceApi.getCategories()
    categories.value = data.results || data
  } catch {}
})
</script>

<style scoped>
.back-link { font-family: var(--mono); font-size: 12px; color: var(--muted); display: block; margin-bottom: 16px; }
.back-link:hover { color: var(--accent); }

/* Stepbar */
.stepbar { display: flex; align-items: center; margin-bottom: 24px; }
.step { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); font-weight: 600; white-space: nowrap; }
.step.active { color: var(--accent); }
.step.done   { color: var(--muted); }
.step .dot {
  width: 24px; height: 24px; border-radius: 50%;
  border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.step.active .dot { border-color: var(--accent); color: var(--accent); }
.step.done .dot   { border-color: var(--accent); background: var(--accent); color: #060f0a; }
.step-line      { flex: 1; height: 1px; background: var(--border); margin: 0 10px; }
.step-line.done { background: var(--accent); }

/* Requirements */
.req-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent2);
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 20px;
}
.req-title { font-size: 12px; font-weight: 700; color: var(--accent2); margin-bottom: 10px; }
.req-list { list-style: none; display: flex; flex-direction: column; gap: 5px; }
.req-list li { font-size: 12px; color: var(--muted); display: flex; gap: 8px; line-height: 1.5; }
.req-list li::before { content: "✓"; color: var(--accent); font-family: var(--mono); font-size: 11px; flex-shrink: 0; }
.req-list li.warn::before { content: "⚠"; color: var(--accent2); }

/* Form fields */
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.field label { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.hint { font-size: 10px; color: var(--muted); font-weight: 400; }

/* Tags */
.tags-wrap {
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 10px; display: flex; flex-wrap: wrap; gap: 6px; cursor: text;
  min-height: 42px; transition: border-color .2s;
}
.tags-wrap:focus-within { border-color: var(--accent); }
.tag-pill {
  background: rgba(93,255,159,.08); border: 1px solid rgba(93,255,159,.2);
  color: var(--accent); font-family: var(--mono); font-size: 11px;
  padding: 2px 8px; border-radius: 20px; display: flex; align-items: center; gap: 5px;
}
.tag-pill button { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 10px; padding: 0; }
.tag-pill button:hover { color: var(--danger); }
.tag-input { background: none; border: none; outline: none; color: var(--text); font-family: var(--font); font-size: 13px; flex: 1; min-width: 100px; }
.tag-input::placeholder { color: var(--muted); }

/* BOM */
.bom-header {
  display: grid; grid-template-columns: 2fr 2fr 60px 80px 32px;
  gap: 8px; margin-bottom: 6px;
  font-family: var(--mono); font-size: 10px; color: var(--muted);
  text-transform: uppercase; letter-spacing: 1px;
}
.bom-row { display: grid; grid-template-columns: 2fr 2fr 60px 80px 32px; gap: 8px; margin-bottom: 8px; align-items: center; }
.input.sm { font-size: 12px; padding: 8px 10px; }
.remove-btn {
  background: none; border: 1px solid var(--border); color: var(--muted);
  border-radius: 6px; cursor: pointer; padding: 7px; font-size: 11px; transition: all .15s;
}
.remove-btn:hover { border-color: var(--danger); color: var(--danger); }
.bom-total-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px;
}
.bom-total-bar span { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.bom-total-bar strong { font-size: 18px; color: var(--accent); }

/* Upload zones */
.upload-zones { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.upload-zone {
  background: var(--surface); border: 2px dashed var(--border); border-radius: 10px;
  padding: 20px; text-align: center; cursor: pointer; transition: border-color .2s;
  display: block;
}
.upload-zone:hover { border-color: var(--accent); }
.upload-zone.uploaded { border-color: rgba(93,255,159,.4); border-style: solid; }
.uz-icon  { font-size: 28px; margin-bottom: 8px; }
.uz-title { font-size: 13px; font-weight: 700; margin-bottom: 4px; }
.uz-sub   { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.uploaded-name { color: var(--accent); }

/* Alerts */
.alert { border-radius: 8px; padding: 11px 14px; font-family: var(--mono); font-size: 12px; }
.alert.danger  { background: rgba(255,79,79,.08); border: 1px solid rgba(255,79,79,.25); color: #ff8080; }
.alert.info    { background: rgba(93,255,159,.04); border: 1px solid rgba(93,255,159,.15); color: var(--muted); }
.alert.warn    { background: rgba(255,107,53,.08); border: 1px solid rgba(255,107,53,.25); color: #ff9060; }

/* Success */
.success-card { text-align: center; padding: 40px 24px; border-color: rgba(93,255,159,.2); }
.success-icon { font-size: 52px; margin-bottom: 16px; }
.success-card h3 { font-size: 20px; font-weight: 800; margin-bottom: 8px; }
.success-card p  { font-size: 13px; color: var(--muted); line-height: 1.6; max-width: 380px; margin: 0 auto; }
.status-pending  { color: #ff9060; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 18px; border-radius: 9px; font-size: 13px; font-weight: 700; cursor: pointer; border: none; transition: all .15s; font-family: var(--font); text-decoration: none; }
.btn.primary { background: var(--accent); color: #060f0a; }
.btn.primary:hover { opacity: .88; }
.btn.primary:disabled { opacity: .4; cursor: not-allowed; }
.btn.outline { background: none; border: 1px solid var(--border); color: var(--muted); }
.btn.outline:hover { border-color: var(--muted); color: var(--text); }

@media (max-width: 600px) {
  .field-row { grid-template-columns: 1fr; }
  .bom-header, .bom-row { grid-template-columns: 1fr 1fr 48px 64px 28px; }
}
</style>
