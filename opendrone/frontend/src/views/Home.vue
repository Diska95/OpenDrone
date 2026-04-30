<template>
  <div>
    <section class="hero-band">
      <div class="hero-inner">
        <div class="hero-label">// marketplace open hardware</div>
        <h1>Stampa il tuo<br>drone <em>ideale</em></h1>
        <p>Progetti drone open source validati dalla community. Acquista come kit o pre-assemblato, paga il giusto, supporta i designer.</p>
        <div class="hero-actions">
          <router-link to="/projects" class="btn primary">Esplora il catalogo →</router-link>
          <router-link to="/register" class="btn outline">Diventa creator</router-link>
        </div>
        <div class="hero-stats">
          <div><div class="hs-num">{{ stats.projects }}</div><div class="hs-lbl">progetti</div></div>
          <div><div class="hs-num">{{ stats.creators }}</div><div class="hs-lbl">creator</div></div>
          <div><div class="hs-num">-88%</div><div class="hs-lbl">vs DJI</div></div>
        </div>
      </div>
    </section>

    <section class="latest">
      <div class="sec-hd">
        <div>
          <div class="page-label">// ultimi progetti</div>
          <h2>Recentemente pubblicati</h2>
        </div>
        <router-link to="/projects" class="btn outline">Vedi tutti →</router-link>
      </div>
      <p v-if="!projects.length" class="empty">Nessun progetto pubblicato ancora — sii il primo a caricare!</p>
      <div v-else class="grid">
        <ProjectCard v-for="p in projects" :key="p.id" :project="p" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marketplaceApi } from '@/api/marketplace'
import ProjectCard from '@/components/ProjectCard.vue'

const projects = ref([])
const stats = ref({ projects: 0, creators: 0 })

onMounted(async () => {
  try {
    const { data } = await marketplaceApi.getProjects({ ordering: '-created_at', page_size: 6 })
    projects.value = data.results || data
    stats.value.projects = data.count ?? projects.value.length
    const designers = new Set()
    projects.value.forEach(p => designers.add(p.designer_name))
    stats.value.creators = designers.size
  } catch {}
})
</script>

<style scoped>
.hero-band {
  padding: 56px 24px 40px;
  background: radial-gradient(ellipse 60% 50% at 50% 0%, rgba(93,255,159,.07) 0%, transparent 70%);
  border-bottom: 1px solid var(--border);
}
.hero-inner { max-width: 900px; margin: 0 auto; }
.hero-label {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 14px;
}
h1 {
  font-size: clamp(28px, 5vw, 46px);
  font-weight: 800;
  letter-spacing: -1.5px;
  line-height: 1.05;
  max-width: 520px;
}
h1 em { font-style: normal; color: var(--accent); }
.hero-band p {
  color: var(--muted);
  margin-top: 14px;
  font-size: 14px;
  max-width: 440px;
  line-height: 1.6;
}
.hero-actions { display: flex; gap: 10px; margin-top: 22px; flex-wrap: wrap; }
.hero-stats { display: flex; gap: 36px; margin-top: 28px; }
.hs-num { font-size: 24px; font-weight: 800; color: var(--accent); letter-spacing: -1px; }
.hs-lbl { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 2px; }

.latest { max-width: 900px; margin: 0 auto; padding: 40px 24px 60px; width: 100%; }
.sec-hd { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 22px; gap: 16px; flex-wrap: wrap; }
.sec-hd h2 { font-size: 22px; font-weight: 800; letter-spacing: -.5px; }
.empty { color: var(--muted); font-family: var(--mono); font-size: 13px; padding: 24px 0; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
</style>
