<template>
  <div v-if="project">
    <section class="hero-band">
      <div class="hero-inner">
        <div class="back-link">
          <router-link to="/projects">← Torna al catalogo</router-link>
        </div>
        <div class="header-grid">
          <div class="header-main">
            <div class="badges">
              <span class="badge" :class="diffClass">{{ project.difficulty }}</span>
              <span class="badge badge-success">{{ project.license_type }}</span>
              <span v-if="project.is_university_project" class="badge badge-warning">Universitario</span>
              <span v-if="project.is_featured" class="badge badge-warning">Featured</span>
            </div>
            <h1>{{ project.title }}</h1>
            <p class="designer">by {{ project.designer?.first_name }} {{ project.designer?.last_name }} · ↓ {{ project.order_count }} ordini</p>
            <p class="description">{{ project.short_description || project.description?.slice(0, 200) }}</p>
            <div class="specs">
              <div class="spec"><span class="spec-lbl">Peso</span><span class="spec-val">{{ project.estimated_weight_grams }}g</span></div>
              <div class="spec"><span class="spec-lbl">Autonomia</span><span class="spec-val">{{ project.estimated_flight_time_minutes }} min</span></div>
              <div class="spec"><span class="spec-lbl">Payload</span><span class="spec-val">{{ project.max_payload_grams }}g</span></div>
              <div class="spec"><span class="spec-lbl">Raggio</span><span class="spec-val">{{ project.operating_range_km }} km</span></div>
            </div>
          </div>
          <div class="header-side">
            <div class="thumb" :class="{ 'has-cover': !!coverUrl }" :style="coverUrl ? { backgroundImage: `url(${coverUrl})` } : null">
              <CategoryIcon v-if="!coverUrl" :category="categorySlug" class="thumb-icon" />
            </div>
            <div class="price-box">
              <div class="price-lbl">Da</div>
              <div class="price">€{{ Number(bomTotal).toFixed(0) }}</div>
              <div class="price-sub">componenti minimi</div>
            </div>

            <!-- viewer = designer del progetto -->
            <template v-if="isOwner">
              <div v-if="project.status === 'draft'" class="own-status status-draft">
                <strong>Bozza</strong>
                <span>Continua la compilazione e pubblica per inviarla all'admin.</span>
                <router-link :to="`/projects/${project.slug}/edit`" class="btn outline" style="margin-top: 8px; width: 100%">✎ Continua a modificare</router-link>
                <button class="btn primary" :disabled="publishing" @click="publishNow" style="margin-top: 6px; width: 100%">
                  {{ publishing ? 'Invio...' : 'Pubblica adesso →' }}
                </button>
              </div>
              <div v-else-if="['pending_validation','pending_review'].includes(project.status)" class="own-status status-pending">
                <strong>⏳ In attesa di approvazione</strong>
                <span>Un admin lo esaminerà a breve. Puoi continuare a modificare nel frattempo.</span>
                <router-link :to="`/projects/${project.slug}/edit`" class="btn outline" style="margin-top: 8px; width: 100%">✎ Modifica</router-link>
              </div>
              <div v-else-if="project.status === 'published'" class="own-status status-pub">
                <strong>✓ Pubblicato</strong>
                <span>Visibile nel marketplace. Le modifiche sono live subito.</span>
                <router-link :to="`/projects/${project.slug}/edit`" class="btn outline" style="margin-top: 8px; width: 100%">✎ Modifica</router-link>
                <router-link to="/projects" class="btn outline" style="margin-top: 6px; width: 100%">Vedi nel catalogo</router-link>
              </div>
              <div v-else-if="project.status === 'rejected'" class="own-status status-rej">
                <strong>✕ Rifiutato</strong>
                <span>Controlla le note normative. Modifica e ripubblica.</span>
                <router-link :to="`/projects/${project.slug}/edit`" class="btn outline" style="margin-top: 8px; width: 100%">✎ Modifica</router-link>
                <button class="btn primary" :disabled="publishing" @click="publishNow" style="margin-top: 6px; width: 100%">
                  {{ publishing ? 'Invio...' : 'Ripubblica →' }}
                </button>
              </div>
              <div v-else-if="project.status === 'suspended'" class="own-status status-rej">
                <strong>⚠ Sospeso</strong>
                <span>Contatta l'admin per maggiori informazioni.</span>
                <router-link :to="`/projects/${project.slug}/edit`" class="btn outline" style="margin-top: 8px; width: 100%">✎ Modifica</router-link>
              </div>
            </template>

            <!-- viewer = admin (e non owner) e progetto pending -->
            <template v-else-if="auth.isAdmin && ['pending_validation','pending_review'].includes(project.status)">
              <div class="own-status status-pending">
                <strong>★ Azione admin richiesta</strong>
                <span>Approva il progetto per pubblicarlo o rifiutalo.</span>
              </div>
              <div style="display: flex; gap: 8px;">
                <button class="btn primary" :disabled="adminBusy" @click="doApprove" style="flex: 1">✓ Approva</button>
                <button class="btn danger" :disabled="adminBusy" @click="doReject" style="flex: 1">✕ Rifiuta</button>
              </div>
            </template>

            <!-- viewer = customer (o altro utente) e progetto pubblicato -->
            <template v-else-if="project.status === 'published'">
              <router-link :to="`/checkout/${project.slug}`" class="btn-full primary">Ordina questo drone →</router-link>
              <p class="modes-note">Disponibile come kit o pre-assemblato</p>
            </template>

            <!-- progetto non pubblicato e viewer non owner: solo info -->
            <template v-else>
              <div class="own-status status-pending">
                <strong>Non disponibile</strong>
                <span>Questo progetto non è ancora nel marketplace.</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </section>

    <div class="content-wrap">
      <div class="tabs">
        <button :class="{ active: tab === 'description' }" @click="tab = 'description'">Descrizione</button>
        <button :class="{ active: tab === 'bom' }" @click="tab = 'bom'">Componenti ({{ project.bom_items?.length || 0 }})</button>
        <button :class="{ active: tab === 'files' }" @click="tab = 'files'">File ({{ project.files?.length || 0 }})</button>
        <button :class="{ active: tab === 'reviews' }" @click="tab = 'reviews'">Recensioni ({{ project.total_reviews || 0 }})</button>
      </div>

      <div class="tab-content card">
        <div v-if="tab === 'description'">
          <p class="desc-body">{{ project.description }}</p>
          <div v-if="project.compliance_notes" class="compliance">
            <div class="page-label">// EASA</div>
            <h3>Note normative</h3>
            <p>Categoria: <strong>{{ project.easa_category || 'Non specificata' }}</strong></p>
            <p>{{ project.compliance_notes }}</p>
          </div>
        </div>

        <div v-else-if="tab === 'bom'">
          <div v-if="!project.bom_items?.length" class="empty">Nessun componente specificato.</div>
          <div v-else>
            <div class="bom-summary">
              <span>Costo totale componenti</span>
              <strong>€{{ Number(bomTotal).toFixed(2) }}</strong>
            </div>
            <table class="bom-table">
              <thead>
                <tr><th>Componente</th><th>Modello</th><th>Qtà</th><th>Prezzo</th><th>Totale</th></tr>
              </thead>
              <tbody>
                <tr v-for="item in project.bom_items" :key="item.id">
                  <td>{{ item.component_name }}</td>
                  <td class="mono">{{ item.model_number || '—' }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>€{{ item.unit_price_eur }}</td>
                  <td><strong>€{{ (item.unit_price_eur * item.quantity).toFixed(2) }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-else-if="tab === 'files'">
          <div v-if="!project.files?.length" class="empty">Nessun file pubblico ancora.</div>
          <div v-else class="file-list">
            <div v-for="file in project.files" :key="file.id" class="file-item">
              <span class="file-type">{{ file.file_type.toUpperCase() }}</span>
              <span class="file-name">{{ file.filename }}</span>
              <span class="file-size">{{ file.file_size_bytes ? (file.file_size_bytes / 1024).toFixed(0) + ' KB' : '' }}</span>
            </div>
          </div>
        </div>

        <div v-else-if="tab === 'reviews'">
          <div v-if="!project.reviews?.length" class="empty">Nessuna recensione ancora.</div>
          <div v-else class="reviews">
            <div v-for="r in project.reviews" :key="r.id" class="review">
              <div class="review-head">
                <strong>{{ r.reviewer_name }}</strong>
                <span class="review-rating">★ {{ ((r.rating_documentation + r.rating_difficulty_accuracy + r.rating_performance) / 3).toFixed(1) }}</span>
              </div>
              <p>{{ r.comment }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <p v-else-if="loading" class="loading">Caricamento...</p>
  <p v-else class="loading">Progetto non trovato.</p>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marketplaceApi } from '@/api/marketplace'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import CategoryIcon from '@/components/CategoryIcon.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const project = ref(null)
const loading = ref(true)
const tab = ref('description')
const adminBusy = ref(false)
const publishing = ref(false)

const isOwner = computed(() => {
  return auth.user && project.value?.designer && auth.user.id === project.value.designer.id
})

async function publishNow() {
  if (!project.value) return
  publishing.value = true
  try {
    await marketplaceApi.publishProject(project.value.slug)
    toast.show('✓ Progetto inviato per validazione')
    const { data } = await marketplaceApi.getProject(project.value.slug)
    project.value = data
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore pubblicazione')
  } finally {
    publishing.value = false
  }
}

async function doApprove() {
  if (!project.value) return
  adminBusy.value = true
  try {
    await marketplaceApi.approveProject(project.value.slug)
    toast.show(`✓ "${project.value.title}" pubblicato`)
    project.value.status = 'published'
  } catch (e) {
    toast.show('✗ Errore approvazione')
  } finally {
    adminBusy.value = false
  }
}
async function doReject() {
  if (!project.value) return
  const reason = prompt(`Motivo del rifiuto (opzionale):`)
  if (reason === null) return
  adminBusy.value = true
  try {
    await marketplaceApi.rejectProject(project.value.slug, reason || '')
    toast.show(`Rifiutato: ${project.value.title}`)
    project.value.status = 'rejected'
  } catch (e) {
    toast.show('✗ Errore rifiuto')
  } finally {
    adminBusy.value = false
  }
}

const bomTotal = computed(() => project.value?.bom_total_cost || 0)
const categorySlug = computed(() => {
  return project.value?.category_data?.slug || ''
})
const coverUrl = computed(() => {
  if (!project.value?.files) return null
  const img = project.value.files.find(f => f.file_type === 'image' && f.is_public && f.file)
  return img ? img.file : null
})
const diffClass = computed(() => {
  const d = project.value?.difficulty
  if (d === 'basic') return 'badge-success'
  if (d === 'intermediate') return 'badge-warning'
  if (d === 'advanced') return 'badge-danger'
  return 'badge-info'
})

onMounted(async () => {
  try {
    const { data } = await marketplaceApi.getProject(route.params.slug)
    project.value = data
  } finally { loading.value = false }
})
</script>

<style scoped>
.hero-band {
  padding: 28px 24px 32px;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(93,255,159,.06) 0%, transparent 70%);
  border-bottom: 1px solid var(--border);
}
.hero-inner { max-width: 900px; margin: 0 auto; }
.back-link { margin-bottom: 16px; }
.back-link a { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.back-link a:hover { color: var(--accent); }

.header-grid { display: grid; grid-template-columns: 1fr 280px; gap: 28px; align-items: start; }
.header-main {}
.badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
h1 { font-size: clamp(24px, 4vw, 36px); font-weight: 800; letter-spacing: -1.2px; line-height: 1.1; }
.designer { font-family: var(--mono); font-size: 12px; color: var(--muted); margin-top: 8px; }
.description { font-size: 14px; color: var(--text); margin-top: 14px; line-height: 1.6; }

.specs { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 18px; }
.spec { background: var(--surface); border: 1px solid var(--border); border-radius: 7px; padding: 10px 12px; display: flex; flex-direction: column; }
.spec-lbl { font-family: var(--mono); font-size: 10px; color: var(--muted); }
.spec-val { font-size: 14px; font-weight: 700; margin-top: 2px; }

.header-side { display: flex; flex-direction: column; gap: 10px; }
.thumb {
  height: 160px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: radial-gradient(ellipse at 50% 70%, rgba(93,255,159,.15) 0%, transparent 70%);
  background-size: cover;
  background-position: center;
}
.thumb.has-cover { background-image: var(--cover); }
.thumb-icon { width: 90px; height: 90px; }
.price-box { background: var(--card); border: 1px solid rgba(93,255,159,.2); border-radius: 12px; padding: 14px; text-align: center; }
.price-lbl { font-family: var(--mono); font-size: 10px; color: var(--muted); }
.price { font-size: 32px; font-weight: 800; color: var(--accent); letter-spacing: -1px; }
.price-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.modes-note { text-align: center; font-family: var(--mono); font-size: 11px; color: var(--muted); }

.own-status {
  border-radius: 9px;
  padding: 12px 14px;
  border: 1px solid;
  font-family: var(--mono);
  font-size: 11px;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.own-status strong { font-size: 13px; }
.own-status span { color: var(--muted); }
.own-status.status-draft { border-color: var(--border); background: var(--surface); }
.own-status.status-draft strong { color: var(--text); }
.own-status.status-pending { border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }
.own-status.status-pending strong { color: #ff9060; }
.own-status.status-pub { border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.own-status.status-pub strong { color: var(--accent); }
.own-status.status-rej { border-color: rgba(255,79,79,.3); background: rgba(255,79,79,.06); }
.own-status.status-rej strong { color: #ff8080; }

.content-wrap { max-width: 900px; margin: 0 auto; padding: 22px 24px 60px; width: 100%; }

.tabs { display: flex; gap: 0; border-bottom: 2px solid var(--border); margin-bottom: 18px; flex-wrap: wrap; }
.tabs button {
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-family: var(--font);
  font-size: 13px;
  color: var(--muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color .15s;
}
.tabs button.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 700; }

.tab-content { padding: 24px; }
.desc-body { white-space: pre-wrap; line-height: 1.7; color: var(--text); }
.compliance { margin-top: 24px; padding-top: 18px; border-top: 1px solid var(--border); }
.compliance h3 { font-size: 16px; margin: 8px 0; }
.compliance p { color: var(--muted); font-size: 13px; line-height: 1.5; margin-top: 4px; }

.empty { color: var(--muted); font-family: var(--mono); padding: 40px 0; text-align: center; font-size: 13px; }

.bom-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 16px;
}
.bom-summary span { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.bom-summary strong { font-size: 18px; color: var(--accent); }

.bom-table { width: 100%; border-collapse: collapse; }
.bom-table th, .bom-table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }
.bom-table th { font-family: var(--mono); font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
.bom-table .mono { font-family: var(--mono); color: var(--muted); font-size: 12px; }

.file-list { display: flex; flex-direction: column; gap: 0; }
.file-item { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.file-type { background: var(--surface); border: 1px solid var(--border); color: var(--accent); padding: 3px 10px; border-radius: 4px; font-family: var(--mono); font-size: 10px; font-weight: 700; }
.file-name { flex: 1; font-size: 13px; }
.file-size { font-family: var(--mono); font-size: 11px; color: var(--muted); }

.reviews { display: flex; flex-direction: column; gap: 16px; }
.review { padding: 12px 0; border-bottom: 1px solid var(--border); }
.review-head { display: flex; justify-content: space-between; margin-bottom: 6px; }
.review-rating { color: var(--accent); font-family: var(--mono); font-size: 12px; }

.loading { color: var(--muted); font-family: var(--mono); padding: 60px 0; text-align: center; }

@media (max-width: 768px) {
  .header-grid { grid-template-columns: 1fr; }
}
</style>
