<template>
  <div class="wrap wide">
    <div class="page-label">// admin / progetti</div>
    <h1 class="page-title">Moderazione progetti</h1>
    <p class="page-sub">Approva, rifiuta, archivia o elimina i progetti caricati dai designer.</p>

    <div class="filters">
      <button class="chip" :class="{ on: filter === 'pending' }" @click="setFilter('pending')">In attesa ({{ counts.pending }})</button>
      <button class="chip" :class="{ on: filter === '' }" @click="setFilter('')">Tutti ({{ counts.all }})</button>
      <button class="chip" :class="{ on: filter === 'published' }" @click="setFilter('published')">Pubblicati</button>
      <button class="chip" :class="{ on: filter === 'rejected' }" @click="setFilter('rejected')">Rifiutati</button>
      <button class="chip" :class="{ on: filter === 'draft' }" @click="setFilter('draft')">Bozze</button>
      <button class="chip" :class="{ on: filter === 'suspended' }" @click="setFilter('suspended')">Sospesi</button>
      <button v-if="auth.isSuperuser" class="chip archive-chip" :class="{ on: filter === 'archived' }" @click="setFilter('archived')">
        📦 Archivio ({{ archivedCount }})
      </button>
    </div>

    <p v-if="loading" class="empty">Caricamento...</p>
    <div v-else-if="!projects.length" class="empty-card card">
      <p v-if="filter === 'archived'">Archivio vuoto. I progetti archiviati appariranno qui.</p>
      <p v-else>Nessun progetto in questa vista.</p>
    </div>

    <div v-else class="approval-list">
      <div v-for="p in projects" :key="p.id" class="approval-row card" :class="{ archived: p.archived_at }">
        <div class="row-thumb" :style="p.cover_image ? { backgroundImage: `url(${p.cover_image})` } : null">
          <CategoryIcon v-if="!p.cover_image" :category="categorySlugFor(p)" class="row-icon" />
        </div>
        <div class="row-main">
          <div class="row-head">
            <h3>{{ p.title }}</h3>
            <span v-if="p.archived_at" class="status-pill s-archive">📦 archiviato</span>
            <span v-else class="status-pill" :class="`s-${statusClass(p.status)}`">{{ statusLabel(p.status) }}</span>
          </div>
          <p class="row-desc">{{ p.short_description }}</p>
          <div class="row-meta">
            <span>👤 {{ p.designer_name }}</span>
            <span>· {{ p.category_name || 'no cat.' }}</span>
            <span>· {{ p.difficulty }}</span>
            <span>· BOM €{{ Number(p.bom_total_cost || 0).toFixed(0) }}</span>
            <span>· {{ new Date(p.created_at).toLocaleDateString('it-IT') }}</span>
          </div>
        </div>
        <div class="row-actions">
          <router-link :to="`/projects/${p.slug}`" class="btn outline">Vedi</router-link>

          <!-- Vista normale -->
          <template v-if="!p.archived_at">
            <button v-if="canApprove(p.status)" class="btn primary" :disabled="busy[p.slug]" @click="approve(p)">✓ Approva</button>
            <button v-if="canReject(p.status)" class="btn warn" :disabled="busy[p.slug]" @click="reject(p)">✕ Rifiuta</button>
            <button class="btn outline" :disabled="busy[p.slug]" @click="archive(p)" title="Archivia (soft-delete)">📦 Archivia</button>
            <button v-if="auth.isSuperuser" class="btn danger" :disabled="busy[p.slug]" @click="hardDelete(p)" title="Elimina definitivamente (solo superuser)">🗑 Elimina</button>
          </template>

          <!-- Vista archivio -->
          <template v-else>
            <button class="btn primary" :disabled="busy[p.slug]" @click="unarchive(p)" title="Ripristina dall'archivio">↩ Ripristina</button>
            <button v-if="auth.isSuperuser" class="btn danger" :disabled="busy[p.slug]" @click="hardDelete(p)" title="Elimina definitivamente (solo superuser)">🗑 Elimina</button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { adminApi } from '@/api/admin'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'
import CategoryIcon from '@/components/CategoryIcon.vue'

const toast = useToastStore()
const auth = useAuthStore()
const allProjects = ref([])
const archivedProjects = ref([])
const archivedCount = ref(0)
const loading = ref(true)
const filter = ref('pending')
const busy = reactive({})

const STATUS_LABELS = {
  draft: 'bozza',
  pending_validation: 'in validazione',
  pending_review: 'in revisione',
  published: 'pubblicato',
  suspended: 'sospeso',
  rejected: 'rifiutato',
}
function statusClass(s) {
  if (s === 'published') return 'success'
  if (['rejected','suspended'].includes(s)) return 'danger'
  if (s === 'draft') return 'info'
  return 'warn'
}
function statusLabel(s) { return STATUS_LABELS[s] || s }
function categorySlugFor(p) { return (p.category_name || '').toLowerCase().replace(/\s/g, '') }

function canApprove(s) { return ['pending_validation','pending_review','rejected'].includes(s) }
function canReject(s) { return ['pending_validation','pending_review','published','draft'].includes(s) }

const projects = computed(() => {
  if (filter.value === 'archived') return archivedProjects.value
  if (filter.value === 'pending') {
    return allProjects.value.filter(p => ['pending_validation','pending_review'].includes(p.status))
  }
  if (!filter.value) return allProjects.value
  return allProjects.value.filter(p => p.status === filter.value)
})

const counts = computed(() => ({
  all: allProjects.value.length,
  pending: allProjects.value.filter(p => ['pending_validation','pending_review'].includes(p.status)).length,
  published: allProjects.value.filter(p => p.status === 'published').length,
  rejected: allProjects.value.filter(p => p.status === 'rejected').length,
  draft: allProjects.value.filter(p => p.status === 'draft').length,
}))

async function loadAll() {
  loading.value = true
  try {
    const { data } = await adminApi.getAllProjects()
    allProjects.value = data.results || data
  } finally {
    loading.value = false
  }
}

async function loadArchived() {
  if (!auth.isSuperuser) return
  try {
    const { data } = await adminApi.getArchivedProjects()
    archivedProjects.value = data.results || data
    archivedCount.value = archivedProjects.value.length
  } catch (e) {
    console.error('[AdminProjects] errore caricamento archivio:', e)
  }
}

async function load() {
  await Promise.all([loadAll(), loadArchived()])
}

watch(filter, async (f) => {
  if (f === 'archived') {
    loading.value = true
    await loadArchived()
    loading.value = false
  }
})

function setFilter(f) { filter.value = f }

async function approve(p) {
  busy[p.slug] = true
  try {
    await adminApi.approveProject(p.slug)
    toast.show(`✓ "${p.title}" pubblicato`)
    p.status = 'published'
  } catch {
    toast.show('✗ Errore approvazione')
  } finally {
    busy[p.slug] = false
  }
}

async function reject(p) {
  const reason = prompt(`Motivo rifiuto per "${p.title}":`)
  if (reason === null) return
  busy[p.slug] = true
  try {
    await adminApi.rejectProject(p.slug, reason || '')
    toast.show(`Rifiutato: ${p.title}`)
    p.status = 'rejected'
  } catch {
    toast.show('✗ Errore')
  } finally {
    busy[p.slug] = false
  }
}

async function archive(p) {
  if (!confirm(`Archiviare "${p.title}"?\n\nIl progetto sara' nascosto dal catalogo pubblico ma potra' essere ripristinato dal superuser.`)) return
  busy[p.slug] = true
  try {
    await adminApi.archiveProject(p.slug)
    toast.show(`📦 "${p.title}" archiviato`)
    // rimuove dalla lista normale
    allProjects.value = allProjects.value.filter(x => x.slug !== p.slug)
    // ricarica archivio
    if (auth.isSuperuser) await loadArchived()
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore archiviazione')
  } finally {
    busy[p.slug] = false
  }
}

async function unarchive(p) {
  busy[p.slug] = true
  try {
    await adminApi.unarchiveProject(p.slug)
    toast.show(`↩ "${p.title}" ripristinato`)
    archivedProjects.value = archivedProjects.value.filter(x => x.slug !== p.slug)
    archivedCount.value = archivedProjects.value.length
    // ricarica lista normale per riprendere il progetto
    await loadAll()
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore ripristino')
  } finally {
    busy[p.slug] = false
  }
}

async function hardDelete(p) {
  const sureMsg = p.archived_at
    ? `ELIMINARE DEFINITIVAMENTE "${p.title}" dall'archivio?\n\nQuesta operazione e' IRREVERSIBILE: tutti i dati del progetto (BOM, file, recensioni) verranno cancellati per sempre.`
    : `ELIMINARE DEFINITIVAMENTE "${p.title}"?\n\nQuesta operazione e' IRREVERSIBILE. Considera "Archivia" se vuoi solo nasconderlo dal catalogo.`
  if (!confirm(sureMsg)) return
  // doppia conferma per sicurezza
  if (!confirm(`Sicuro al 100%? Digita OK nel prossimo prompt per confermare.`)) return
  const typed = prompt('Digita OK per confermare l\'eliminazione definitiva:')
  if (typed?.trim().toUpperCase() !== 'OK') {
    toast.show('Eliminazione annullata')
    return
  }
  busy[p.slug] = true
  try {
    await adminApi.hardDeleteProject(p.slug)
    toast.show(`🗑 "${p.title}" eliminato definitivamente`)
    allProjects.value = allProjects.value.filter(x => x.slug !== p.slug)
    archivedProjects.value = archivedProjects.value.filter(x => x.slug !== p.slug)
    archivedCount.value = archivedProjects.value.length
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore eliminazione')
  } finally {
    busy[p.slug] = false
  }
}

onMounted(load)
</script>

<style scoped>
.filters { display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap; }
.chip { background: none; border: 1px solid var(--border); color: var(--muted); padding: 5px 13px; border-radius: 20px; font-family: var(--font); font-size: 12px; cursor: pointer; transition: all .15s; }
.chip:hover, .chip.on { border-color: var(--accent); color: var(--accent); background: rgba(93,255,159,.06); }
.chip.archive-chip { border-color: rgba(255,107,53,.3); color: #ff9060; }
.chip.archive-chip:hover, .chip.archive-chip.on { border-color: var(--accent2); color: var(--accent2); background: rgba(255,107,53,.08); }

.empty { color: var(--muted); font-family: var(--mono); padding: 60px 0; text-align: center; }
.empty-card { text-align: center; padding: 40px; }

.approval-list { display: flex; flex-direction: column; gap: 12px; }
.approval-row { display: grid; grid-template-columns: 80px 1fr auto; gap: 18px; align-items: center; padding: 16px; margin-bottom: 0; }
.approval-row.archived { opacity: .85; border-style: dashed; }
.row-thumb { width: 80px; height: 80px; flex-shrink: 0; background: var(--surface); border-radius: 10px; background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; }
.row-icon { width: 100%; height: 100%; }
.row-main { min-width: 0; }
.row-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }
.row-head h3 { font-size: 16px; font-weight: 700; }
.row-desc { color: var(--muted); font-size: 13px; line-height: 1.4; }
.row-meta { display: flex; gap: 10px; font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 8px; flex-wrap: wrap; }
.row-actions { display: flex; gap: 8px; flex-shrink: 0; flex-wrap: wrap; align-items: center; }

.status-pill { font-family: var(--mono); font-size: 10px; padding: 3px 10px; border-radius: 20px; border: 1px solid; text-transform: lowercase; }
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-warn { color: #ff9060; background: rgba(255,107,53,.06); border-color: rgba(255,107,53,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }
.s-info { color: var(--muted); background: var(--surface); border-color: var(--border); }
.s-archive { color: #ff9060; background: rgba(255,107,53,.08); border-color: rgba(255,107,53,.3); }

.btn.warn { background: none; border: 1px solid rgba(255,107,53,.4); color: #ff9060; }
.btn.warn:hover { border-color: #ff9060; background: rgba(255,107,53,.06); }

@media (max-width: 720px) { .approval-row { grid-template-columns: 1fr; } }
</style>
