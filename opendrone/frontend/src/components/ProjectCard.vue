<template>
  <router-link :to="`/projects/${project.slug}`" class="mcard">
    <div class="mthumb" :class="{ 'has-cover': !!project.cover_image }" :style="thumbStyle">
      <div class="tgrad"></div>
      <CategoryIcon v-if="!project.cover_image" :category="categorySlug" class="thumb-icon" />
      <span class="mbadge" :class="isFree ? 'free' : 'paid'">{{ isFree ? 'OPEN' : licenseLabel }}</span>
      <span v-if="project.category_name" class="mcat">{{ project.category_name }}</span>
    </div>
    <div class="mbody">
      <div class="mtitle">{{ project.title }}</div>
      <div class="mauthor">by {{ project.designer_name }}</div>
      <div class="mmeta">
        <span class="mprice" :class="{ paid: !isFree }">{{ priceLabel }}</span>
        <span class="mdl">↓ {{ project.order_count || 0 }}</span>
      </div>
      <div v-if="project.use_cases?.length" class="mtags">
        <span v-for="tag in project.use_cases.slice(0, 3)" :key="tag" class="mtag">{{ tag }}</span>
      </div>
      <div class="mcta-row">
        <span class="badge" :class="diffClass">{{ project.difficulty }}</span>
        <span v-if="project.rating" class="rating">★ {{ project.rating }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import CategoryIcon from './CategoryIcon.vue'

const props = defineProps({
  project: { type: Object, required: true }
})

const thumbStyle = computed(() => {
  const accent = props.project.license_type === 'open_source' ? 'rgba(93,255,159,.15)' : 'rgba(255,107,53,.15)'
  if (props.project.cover_image) {
    return { backgroundImage: `url(${props.project.cover_image})`, '--gc': accent }
  }
  return { '--gc': accent }
})

const isFree = computed(() => props.project.license_type === 'open_source')
const licenseLabel = computed(() => {
  const map = {
    open_source: 'OPEN',
    open_royalty: 'ROYALTY',
    commercial: 'PREMIUM',
    university: 'UNI',
  }
  return map[props.project.license_type] || 'OPEN'
})
const priceLabel = computed(() => {
  const min = props.project.estimated_total_cost_min || props.project.bom_total_cost
  if (min) return `da €${Number(min).toFixed(0)}`
  return isFree.value ? 'Gratuito' : 'Personalizzabile'
})
const categorySlug = computed(() => {
  const name = props.project.category_name?.toLowerCase().replace(/\s/g, '') || ''
  return name
})
const diffClass = computed(() => {
  const d = props.project.difficulty
  if (d === 'basic') return 'badge-success'
  if (d === 'intermediate') return 'badge-warning'
  if (d === 'advanced') return 'badge-danger'
  return 'badge-info'
})
</script>

<style scoped>
.mcard {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color .2s, transform .2s;
  display: flex;
  flex-direction: column;
  animation: fadeUp .25s ease both;
  text-decoration: none;
  color: inherit;
}
.mcard:hover { border-color: rgba(93,255,159,.3); transform: translateY(-2px); }
.mthumb {
  height: 150px;
  position: relative;
  background: var(--surface);
  display: flex;
  align-items: center;
  justify-content: center;
  background-size: cover;
  background-position: center;
}
.mthumb.has-cover .tgrad {
  background: linear-gradient(to top, rgba(10,10,15,.4) 0%, transparent 50%);
}
.thumb-icon { width: 70px; height: 70px; opacity: .85; position: relative; z-index: 2; }
.tgrad {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 80%, var(--gc, rgba(93,255,159,.12)) 0%, transparent 70%);
}
.mbadge {
  position: absolute;
  top: 9px;
  right: 9px;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  font-family: var(--mono);
  z-index: 3;
}
.mbadge.free { background: rgba(93,255,159,.08); color: var(--accent); border: 1px solid rgba(93,255,159,.25); }
.mbadge.paid { background: rgba(255,107,53,.1); color: #ff9060; border: 1px solid rgba(255,107,53,.25); }
.mcat {
  position: absolute;
  top: 9px;
  left: 9px;
  font-family: var(--mono);
  font-size: 10px;
  background: rgba(10,10,15,.75);
  color: var(--muted);
  border: 1px solid var(--border);
  padding: 3px 8px;
  border-radius: 4px;
  z-index: 3;
}
.mbody { padding: 12px 14px 14px; flex: 1; display: flex; flex-direction: column; gap: 5px; }
.mtitle { font-size: 13px; font-weight: 700; letter-spacing: -.2px; }
.mauthor { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.mmeta { display: flex; align-items: center; gap: 8px; margin-top: 3px; }
.mprice { font-size: 14px; font-weight: 800; color: var(--accent); }
.mprice.paid { color: #ff9060; }
.mdl { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-left: auto; }
.mtags { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 3px; }
.mtag { font-family: var(--mono); font-size: 10px; color: var(--muted); background: var(--surface); border: 1px solid var(--border); padding: 2px 7px; border-radius: 4px; }
.mcta-row { display: flex; gap: 6px; align-items: center; margin-top: 6px; }
.rating { font-family: var(--mono); font-size: 11px; color: var(--accent); margin-left: auto; }
</style>
