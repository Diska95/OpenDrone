<template>
  <div class="wrap wide">
    <div class="page-label">// admin / progetti</div>
    <h1 class="page-title">Moderazione progetti</h1>
    <p class="page-sub">Approva, rifiuta o rivedi tutti i progetti caricati dai designer.</p>

    <div class="filters">
      <button class="chip" :class="{ on: filter === 'pending' }" @click="setFilter('pending')">In attesa ({{ counts.pending }})</button>
      <button class="chip" :class="{ on: filter === '' }" @click="setFilter('')">Tutti ({{ counts.all }})</button>
      <button class="chip" :class="{ on: filter === 'published' }" @click="setFilter('published')">Pubblicati</button>
      <button class="chip" :class="{ on: filter === 'rejected' }" @click="setFilter('rejected')">Rifiutati</button>
      <button class="chip" :class="{ on: filter === 'draft' }" @click="setFilter('draft')">Bozze</button>
      <button class="chip" :class="{ on: filter === 'suspended' }" @click="setFilter('suspended')">Sospesi</button>
    </div>

    <p v-if="loading" class="empty">Caricamento...</p>
    <div v-else-if="!projects.length" class="empty-card card">
      <p>Nessun progetto in questa vista.</p>
    </div>

    <div v-else class="approval-list">
      <div v-for="p in projects" :key="p.id" class="approval-row card">
        <div class="row-thumb" :style="p.cover_image ? { backgroundImage: `url(${p.cover_image})` } : null">
          <CategoryIcon v-if="!p.cover_image" :category="categorySlugFor(p)" class="row-icon" />
        </div>
        <div class="row-main">
          <div class="row-head">
            <h3>{{ p.title }}</h3>
            <span class="status-pill" :class="`s-${statusClass(p.status)}`">{{ statusLabel(p.status) }}</span>
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
          <button v-if="canApprove(p.status)" class="btn primary" :disabled="busy[p.slug]" @click="approve(p)">✓ Approva</button>
          <button v-if="canReject(p.status)" class="btn danger" :disabled="busy[p.slug]" @click="reject(p)">✕ Rifiuta</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { adminApi } from '@/api/admin'
import { useToastStore } from '@/stores/toast'
import CategoryIcon from '@/components/CategoryIcon.vue'

const toast = useToastStore()
const allProjects = ref([])
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

async function load() {
  loading.value = true
  try {
    const { data } = await adminApi.getAllProjects()
    allProjects.value = data.results || data
  } finally {
    loading.value = false
  }
}

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

onMounted(load)
</script>

<style scoped>
.filters { display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap; }
.chip { background: none; border: 1px solid var(--border); color: var(--muted); padding: 5px 13px; border-radius: 20px; font-family: var(--font); font-size: 12px; cursor: pointer; transition: all .15s; }
.chip:hover, .chip.on { border-color: var(--accent); color: var(--accent); background: rgba(93,255,159,.06); }

.empty { color: var(--muted); font-family: var(--mono); padding: 60px 0; text-align: center; }
.empty-card { text-align: center; padding: 40px; }

.approval-list { display: flex; flex-direction: column; gap: 12px; }
.approval-row { display: grid; grid-template-columns: 80px 1fr auto; gap: 18px; align-items: center; padding: 16px; margin-bottom: 0; }
.row-thumb { width: 80px; height: 80px; flex-shrink: 0; background: var(--surface); border-radius: 10px; background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; }
.row-icon { width: 100%; height: 100%; }
.row-main { min-width: 0; }
.row-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.row-head h3 { font-size: 16px; font-weight: 700; }
.row-desc { color: var(--muted); font-size: 13px; line-height: 1.4; }
.row-meta { display: flex; gap: 10px; font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 8px; flex-wrap: wrap; }
.row-actions { display: flex; gap: 8px; flex-shrink: 0; flex-wrap: wrap; }

.status-pill { font-family: var(--mono); font-size: 10px; padding: 3px 10px; border-radius: 20px; border: 1px solid; text-transform: lowercase; }
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-warn { color: #ff9060; background: rgba(255,107,53,.06); border-color: rgba(255,107,53,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }
.s-info { color: var(--muted); background: var(--surface); border-color: var(--border); }

@media (max-width: 720px) { .approval-row { grid-template-columns: 1fr; } }
</style>
