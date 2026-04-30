<template>
  <div class="wrap">
    <div class="head-row">
      <div>
        <div class="page-label">// area designer</div>
        <h1>I miei progetti</h1>
        <p class="page-sub">Tutti i progetti che hai creato, con il loro stato corrente.</p>
      </div>
      <router-link to="/projects/new" class="btn primary">+ Nuovo progetto</router-link>
    </div>

    <div class="filters">
      <button class="chip" :class="{ on: filter === '' }" @click="filter = ''">Tutti ({{ projects.length }})</button>
      <button class="chip" :class="{ on: filter === 'draft' }" @click="filter = 'draft'">Bozze ({{ countBy('draft') }})</button>
      <button class="chip" :class="{ on: filter === 'pending_validation' }" @click="filter = 'pending_validation'">In validazione ({{ countBy('pending_validation') }})</button>
      <button class="chip" :class="{ on: filter === 'pending_review' }" @click="filter = 'pending_review'">In revisione ({{ countBy('pending_review') }})</button>
      <button class="chip" :class="{ on: filter === 'published' }" @click="filter = 'published'">Pubblicati ({{ countBy('published') }})</button>
      <button class="chip" :class="{ on: filter === 'rejected' }" @click="filter = 'rejected'">Rifiutati ({{ countBy('rejected') }})</button>
    </div>

    <p v-if="loading" class="empty">Caricamento...</p>
    <div v-else-if="!filtered.length" class="empty-card card">
      <p>{{ filter ? 'Nessun progetto in questo stato.' : 'Non hai ancora caricato nessun progetto.' }}</p>
      <router-link to="/projects/new" class="btn primary" style="margin-top: 14px">+ Carica il tuo primo progetto</router-link>
    </div>

    <div v-else class="project-list">
      <router-link v-for="p in filtered" :key="p.id" :to="rowLink(p)" class="project-row">
        <div class="row-thumb" :style="p.cover_image ? { backgroundImage: `url(${p.cover_image})` } : null">
          <CategoryIcon v-if="!p.cover_image" :category="categorySlugFor(p)" class="row-icon" />
        </div>
        <div class="row-main">
          <div class="row-title">{{ p.title }}</div>
          <div class="row-meta">
            <span v-if="p.short_description">{{ p.short_description }}</span>
          </div>
          <div class="row-meta-line">
            <span v-if="p.category_name">{{ p.category_name }}</span>
            <span>· {{ p.difficulty }}</span>
            <span>· creato il {{ new Date(p.created_at).toLocaleDateString('it-IT') }}</span>
            <span v-if="p.bom_total_cost">· BOM €{{ Number(p.bom_total_cost).toFixed(0) }}</span>
            <span v-if="p.order_count">· {{ p.order_count }} ordini</span>
          </div>
        </div>
        <div class="row-side">
          <span class="status-pill" :class="`s-${statusClass(p.status)}`">{{ statusLabel(p.status) }}</span>
          <span class="row-arr">→</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marketplaceApi } from '@/api/marketplace'
import CategoryIcon from '@/components/CategoryIcon.vue'

const projects = ref([])
const loading = ref(true)
const filter = ref('')

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
  if (s === 'rejected' || s === 'suspended') return 'danger'
  if (s === 'draft') return 'info'
  return 'warn'   // pending_*
}
function statusLabel(s) { return STATUS_LABELS[s] || s }

function categorySlugFor(p) {
  return (p.category_name || '').toLowerCase().replace(/\s/g, '')
}

function rowLink(p) {
  // tutti i miei progetti → wizard di modifica (è la mia area di lavoro)
  return `/projects/${p.slug}/edit`
}

const filtered = computed(() => {
  if (!filter.value) return projects.value
  return projects.value.filter(p => p.status === filter.value)
})

function countBy(status) {
  return projects.value.filter(p => p.status === status).length
}

onMounted(async () => {
  try {
    const { data } = await marketplaceApi.getMyProjects()
    projects.value = data.results || data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.head-row { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 22px; flex-wrap: wrap; }
.head-row h1 { font-size: 26px; font-weight: 800; letter-spacing: -1px; margin-top: 4px; }

.filters { display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap; }
.chip {
  background: none;
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 5px 13px;
  border-radius: 20px;
  font-family: var(--font);
  font-size: 12px;
  cursor: pointer;
  transition: all .15s;
}
.chip:hover, .chip.on { border-color: var(--accent); color: var(--accent); background: rgba(93,255,159,.06); }

.empty { color: var(--muted); font-family: var(--mono); padding: 60px 0; text-align: center; }
.empty-card { text-align: center; padding: 40px; }

.project-list { display: flex; flex-direction: column; gap: 8px; }
.project-row {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 18px;
  display: grid;
  grid-template-columns: 56px 1fr auto;
  gap: 16px;
  align-items: center;
  transition: border-color .15s;
  color: inherit;
}
.project-row:hover { border-color: rgba(93,255,159,.3); }

.row-thumb {
  width: 56px; height: 56px; flex-shrink: 0;
  background: var(--surface);
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  display: flex; align-items: center; justify-content: center;
}
.row-icon { width: 100%; height: 100%; }

.row-main { min-width: 0; }
.row-title { font-size: 15px; font-weight: 700; }
.row-meta { color: var(--muted); font-size: 13px; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-meta-line { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 4px; display: flex; gap: 6px; flex-wrap: wrap; }

.row-side { display: flex; align-items: center; gap: 12px; }
.status-pill {
  font-family: var(--mono);
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid;
  text-transform: lowercase;
}
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-warn { color: #ff9060; background: rgba(255,107,53,.06); border-color: rgba(255,107,53,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }
.s-info { color: var(--muted); background: var(--surface); border-color: var(--border); }

.row-arr { color: var(--muted); }
</style>
