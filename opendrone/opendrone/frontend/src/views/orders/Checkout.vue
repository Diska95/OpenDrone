<template>
  <div class="wrap" style="max-width:680px">
    <div class="page-label">// checkout</div>
    <div class="page-title">Conferma il tuo ordine</div>

    <div v-if="project" class="card project-summary">
      <CategoryIcon :category="categorySlug" class="thumb" />
      <div>
        <h3>{{ project.title }}</h3>
        <p class="muted">{{ project.short_description }}</p>
      </div>
    </div>

    <div class="card">
      <div class="page-label">Modalità</div>
      <div class="mode-grid">
        <label class="mode-opt" :class="{ sel: form.mode === 'kit' }">
          <input type="radio" v-model="form.mode" value="kit" />
          <div class="mi">🔧</div>
          <div class="mn">Kit da assemblare</div>
          <div class="md">Frame stampato + componenti, monti tu</div>
        </label>
        <label class="mode-opt" :class="{ sel: form.mode === 'assembled' }">
          <input type="radio" v-model="form.mode" value="assembled" />
          <div class="mi">✓</div>
          <div class="mn">Pre-assemblato</div>
          <div class="md">Drone montato, testato, pronto</div>
        </label>
      </div>
    </div>

    <div class="card">
      <div class="page-label">Indirizzo di consegna</div>
      <div class="field">
        <label>Via e numero</label>
        <input class="input" v-model="form.shipping_address.street" placeholder="Via Roma 1" />
      </div>
      <div class="field-row">
        <div class="field">
          <label>Città</label>
          <input class="input" v-model="form.shipping_address.city" placeholder="Bologna" />
        </div>
        <div class="field">
          <label>CAP</label>
          <input class="input" v-model="form.shipping_address.zip" placeholder="40100" />
        </div>
      </div>
      <div class="field">
        <label>Paese</label>
        <input class="input" v-model="form.shipping_address.country" placeholder="IT" />
      </div>
    </div>

    <div class="card">
      <label class="ft-row" :class="{ sel: form.is_fast_track }">
        <input type="checkbox" v-model="form.is_fast_track" />
        <div>
          <div class="ft-title">⚡ Fast Track <span class="ft-badge">+30%</span></div>
          <div class="ft-sub">Produzione prioritaria garantita entro 48h</div>
        </div>
      </label>
    </div>

    <div v-if="error" class="alert danger">{{ error }}</div>

    <button class="btn-full primary" :disabled="loading" @click="placeOrder" style="font-size: 15px">
      {{ loading ? 'Elaborazione...' : 'Conferma ordine →' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marketplaceApi } from '@/api/marketplace'
import { ordersApi } from '@/api/orders'
import { useToastStore } from '@/stores/toast'
import CategoryIcon from '@/components/CategoryIcon.vue'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()
const project = ref(null)
const error = ref('')
const loading = ref(false)

const categorySlug = computed(() => project.value?.category_data?.slug || '')

const form = ref({
  mode: 'kit',
  is_fast_track: false,
  quantity: 1,
  shipping_address: { street: '', city: '', zip: '', country: 'IT', latitude: 44.4, longitude: 11.3 }
})

onMounted(async () => {
  try {
    const { data } = await marketplaceApi.getProject(route.params.projectSlug)
    project.value = data
  } catch {
    error.value = 'Progetto non trovato.'
  }
})

async function placeOrder() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await ordersApi.createOrder({
      project_id: project.value.id,
      ...form.value,
    })
    toast.show(`✓ Ordine #${data.order.id} creato`)
    router.push(`/orders/${data.order.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore durante la creazione dell\'ordine.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.project-summary { display: flex; align-items: center; gap: 16px; }
.project-summary h3 { font-size: 16px; font-weight: 700; }
.muted { color: var(--muted); font-size: 13px; margin-top: 2px; }
.thumb { width: 60px; height: 60px; flex-shrink: 0; }

.mode-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
.mode-opt {
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 14px;
  cursor: pointer;
  transition: all .15s;
  background: var(--surface);
  text-align: center;
}
.mode-opt input { display: none; }
.mode-opt.sel { border-color: var(--accent); background: rgba(93,255,159,.06); }
.mi { font-size: 24px; margin-bottom: 6px; }
.mn { font-size: 13px; font-weight: 700; }
.mode-opt.sel .mn { color: var(--accent); }
.md { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 4px; }

.ft-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  cursor: pointer;
  padding: 4px;
}
.ft-row input { margin-top: 4px; accent-color: var(--accent); width: 16px; height: 16px; }
.ft-title { font-size: 14px; font-weight: 700; }
.ft-badge { background: rgba(255,107,53,.15); color: #ff9060; font-family: var(--mono); font-size: 10px; padding: 2px 8px; border-radius: 4px; margin-left: 6px; }
.ft-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 4px; }

.field { margin-bottom: 12px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
</style>
