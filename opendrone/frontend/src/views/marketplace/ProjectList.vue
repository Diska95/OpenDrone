<template>
  <div>
    <section class="hero-band">
      <div class="hero-inner">
        <div class="page-label">// catalogo</div>
        <h1>Trova il drone <em>giusto</em><br>per la tua missione</h1>
        <p>{{ totalCount }} {{ totalCount === 1 ? 'progetto disponibile' : 'progetti disponibili' }} dalla community.</p>
      </div>
    </section>

    <div class="filters">
      <span class="flbl">Categoria /</span>
      <button class="chip" :class="{ on: filters.category === '' }" @click="setCategory('')">Tutte</button>
      <button v-for="c in categories" :key="c.id" class="chip" :class="{ on: filters.category === c.id }" @click="setCategory(c.id)">
        {{ c.name }}
      </button>
      <span class="flbl" style="margin-left:8px">Difficoltà /</span>
      <button class="chip" :class="{ on: filters.difficulty === 'basic' }" @click="toggle('difficulty', 'basic')">Base</button>
      <button class="chip" :class="{ on: filters.difficulty === 'intermediate' }" @click="toggle('difficulty', 'intermediate')">Intermedio</button>
      <button class="chip" :class="{ on: filters.difficulty === 'advanced' }" @click="toggle('difficulty', 'advanced')">Avanzato</button>
      <div class="search-wrap">
        <input class="search" placeholder="Cerca..." v-model="search" @input="debouncedSearch" />
      </div>
    </div>

    <div class="grid-wrap">
      <div class="grid-hd">
        <span class="grid-count">{{ resultCount }} {{ resultCount === 1 ? 'progetto' : 'progetti' }}</span>
        <select class="select sort" v-model="filters.ordering" @change="loadProjects">
          <option value="-created_at">Più recenti</option>
          <option value="-rating">Meglio valutati</option>
          <option value="-order_count">Più ordinati</option>
          <option value="estimated_total_cost_min">Prezzo crescente</option>
        </select>
      </div>

      <p v-if="loading" class="loading">Caricamento...</p>
      <p v-else-if="!projects.length" class="empty">Nessun progetto trovato con questi filtri.</p>

      <div v-else class="grid">
        <ProjectCard v-for="p in projects" :key="p.id" :project="p" />
      </div>

      <div v-if="nextPage || prevPage" class="pagination">
        <button v-if="prevPage" class="btn outline" @click="loadPage(prevPage)">← Precedente</button>
        <button v-if="nextPage" class="btn outline" @click="loadPage(nextPage)">Successiva →</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marketplaceApi } from '@/api/marketplace'
import client from '@/api/client'
import ProjectCard from '@/components/ProjectCard.vue'

const projects = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const nextPage = ref(null)
const prevPage = ref(null)
const totalCount = ref(0)
const resultCount = ref(0)
const filters = ref({ category: '', difficulty: '', license_type: '', ordering: '-created_at' })

let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadProjects, 400)
}

function setCategory(id) {
  filters.value.category = id
  loadProjects()
}
function toggle(key, value) {
  filters.value[key] = filters.value[key] === value ? '' : value
  loadProjects()
}

async function loadProjects() {
  loading.value = true
  try {
    const params = {}
    Object.entries(filters.value).forEach(([k, v]) => { if (v) params[k] = v })
    if (search.value) params.search = search.value
    const { data } = await marketplaceApi.getProjects(params)
    projects.value = data.results || data
    nextPage.value = data.next
    prevPage.value = data.previous
    resultCount.value = data.count ?? projects.value.length
  } catch {} finally { loading.value = false }
}

async function loadPage(url) {
  loading.value = true
  try {
    const { data } = await client.get(url)
    projects.value = data.results || data
    nextPage.value = data.next
    prevPage.value = data.previous
  } finally { loading.value = false }
}

onMounted(async () => {
  try {
    const { data } = await marketplaceApi.getCategories()
    categories.value = data.results || data
  } catch {}
  await loadProjects()
  totalCount.value = resultCount.value
})
</script>

<style scoped>
.hero-band {
  padding: 40px 24px 32px;
  background: radial-gradient(ellipse 60% 50% at 50% 0%, rgba(93,255,159,.07) 0%, transparent 70%);
  border-bottom: 1px solid var(--border);
}
.hero-inner { max-width: 900px; margin: 0 auto; }
h1 {
  font-size: clamp(24px, 4vw, 38px);
  font-weight: 800;
  letter-spacing: -1.2px;
  line-height: 1.1;
  max-width: 560px;
}
h1 em { font-style: normal; color: var(--accent); }
.hero-band p { color: var(--muted); margin-top: 10px; font-size: 13px; }

.filters {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}
.flbl { font-family: var(--mono); font-size: 10px; color: var(--muted); white-space: nowrap; margin-right: 2px; }
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
  white-space: nowrap;
}
.chip:hover, .chip.on { border-color: var(--accent); color: var(--accent); background: rgba(93,255,159,.06); }
.chip.on { font-weight: 600; }
.search-wrap { margin-left: auto; }
.search {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 7px 13px;
  border-radius: 6px;
  font-family: var(--mono);
  font-size: 12px;
  width: 180px;
  outline: none;
  transition: border-color .2s;
}
.search:focus { border-color: var(--accent); }
.search::placeholder { color: var(--muted); }

.grid-wrap { padding: 22px 24px 60px; max-width: 900px; margin: 0 auto; width: 100%; }
.grid-hd { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; gap: 12px; }
.grid-count { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.sort { width: auto; padding: 6px 32px 6px 12px; font-size: 12px; font-family: var(--mono); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }

.loading, .empty { color: var(--muted); font-family: var(--mono); padding: 40px 0; text-align: center; }
.pagination { display: flex; gap: 10px; margin-top: 32px; justify-content: center; }
</style>
