<template>
  <div class="wrap wide">
    <div class="page-label">// admin / ordini</div>
    <h1 class="page-title">Tutti gli ordini</h1>
    <p class="page-sub">Tutti gli ordini della piattaforma. Cambia stato manualmente per simulare il flusso (es. conferma pagamento se Stripe non è configurato).</p>

    <div class="filters">
      <button class="chip" :class="{ on: filter === '' }" @click="filter = ''">Tutti ({{ orders.length }})</button>
      <button class="chip" :class="{ on: filter === 'pending' }" @click="filter = 'pending'">Pending ({{ countBy('pending') }})</button>
      <button class="chip" :class="{ on: filter === 'payment_confirmed' }" @click="filter = 'payment_confirmed'">Pagati ({{ countBy('payment_confirmed') }})</button>
      <button class="chip" :class="{ on: filter === 'shipped' }" @click="filter = 'shipped'">Spediti ({{ countBy('shipped') }})</button>
      <button class="chip" :class="{ on: filter === 'delivered' }" @click="filter = 'delivered'">Consegnati ({{ countBy('delivered') }})</button>
      <button class="chip" :class="{ on: filter === 'disputed' }" @click="filter = 'disputed'">Dispute ({{ countBy('disputed') }})</button>
    </div>

    <p v-if="loading" class="empty">Caricamento...</p>
    <div v-else-if="!filtered.length" class="empty-card card">
      <p>Nessun ordine in questa vista.</p>
    </div>

    <div v-else class="order-list">
      <div v-for="o in filtered" :key="o.id" class="order-row card">
        <div class="o-top">
          <div class="o-id">#{{ o.id }}</div>
          <span class="status-pill" :class="`s-${statusClass(o.status)}`">{{ statusLabel(o.status) }}</span>
        </div>
        <div class="o-main">
          <div class="o-title">{{ o.project_data?.title || '—' }}</div>
          <div class="o-meta">
            <span>👤 customer #{{ o.customer }}</span>
            <span v-if="o.print_node">· nodo #{{ o.print_node }}</span>
            <span v-if="o.assembly_center">· asm #{{ o.assembly_center }}</span>
            <span>· {{ o.mode === 'kit' ? 'Kit' : 'Assemblato' }}</span>
            <span v-if="o.is_fast_track">· ⚡ FT</span>
            <span>· {{ new Date(o.created_at).toLocaleDateString('it-IT') }}</span>
          </div>
        </div>
        <div class="o-side">
          <div class="o-total">€{{ o.total_amount }}</div>
          <div class="o-cta">
            <router-link :to="`/orders/${o.id}`" class="btn outline">Vedi</router-link>
            <button v-if="o.status === 'pending'" class="btn primary" :disabled="busy[o.id]" @click="confirmPayment(o)">
              ✓ Conferma pagamento
            </button>
            <button v-if="o.status === 'payment_confirmed'" class="btn outline" :disabled="busy[o.id]" @click="changeStatus(o, 'assigned_print')">
              → Assegna stampa
            </button>
            <button v-if="o.status === 'print_done'" class="btn outline" :disabled="busy[o.id]" @click="changeStatus(o, 'shipped')">
              → Spedito
            </button>
            <button v-if="o.status === 'shipped'" class="btn primary" :disabled="busy[o.id]" @click="changeStatus(o, 'delivered')">
              → Consegnato
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const orders = ref([])
const loading = ref(true)
const filter = ref('')
const busy = reactive({})

const STATUS_LABELS = {
  pending: 'in attesa',
  payment_confirmed: 'pagato',
  assigned_print: 'assegnato',
  printing: 'in stampa',
  print_done: 'stampato',
  assigned_assembly: 'assemblaggio',
  assembling: 'assemblaggio',
  testing: 'test',
  shipped: 'spedito',
  delivered: 'consegnato',
  disputed: 'disputa',
  cancelled: 'annullato',
  refunded: 'rimborsato',
}
function statusClass(s) {
  if (['delivered'].includes(s)) return 'success'
  if (['disputed','cancelled','refunded'].includes(s)) return 'danger'
  if (s === 'pending') return 'warn'
  return 'info'
}
function statusLabel(s) { return STATUS_LABELS[s] || s }

const filtered = computed(() => {
  if (!filter.value) return orders.value
  return orders.value.filter(o => o.status === filter.value)
})
function countBy(s) { return orders.value.filter(o => o.status === s).length }

async function load() {
  loading.value = true
  try {
    const { data } = await ordersApi.getOrders()
    orders.value = data.results || data
  } finally {
    loading.value = false
  }
}

async function confirmPayment(o) {
  await changeStatus(o, 'payment_confirmed', 'Pagamento confermato manualmente')
}
async function changeStatus(o, newStatus, note = '') {
  busy[o.id] = true
  try {
    const { data } = await ordersApi.updateStatus(o.id, { status: newStatus, note })
    Object.assign(o, data)
    toast.show(`Ordine #${o.id} → ${statusLabel(newStatus)}`)
  } catch {
    toast.show('✗ Errore cambio stato')
  } finally {
    busy[o.id] = false
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

.order-list { display: flex; flex-direction: column; gap: 10px; }
.order-row { display: grid; grid-template-columns: auto 1fr auto; gap: 16px; align-items: center; padding: 14px 18px; margin-bottom: 0; }
.o-top { display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.o-id { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.o-main { min-width: 0; }
.o-title { font-size: 14px; font-weight: 700; }
.o-meta { display: flex; gap: 8px; font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 4px; flex-wrap: wrap; }

.o-side { display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }
.o-total { font-size: 18px; font-weight: 800; color: var(--accent); letter-spacing: -.5px; font-family: var(--font-display); }
.o-cta { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }

.status-pill { font-family: var(--mono); font-size: 10px; padding: 3px 10px; border-radius: 20px; border: 1px solid; text-transform: lowercase; }
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-warn { color: #ff9060; background: rgba(255,107,53,.06); border-color: rgba(255,107,53,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }
.s-info { color: var(--muted); background: var(--surface); border-color: var(--border); }

@media (max-width: 720px) { .order-row { grid-template-columns: 1fr; } .o-side { align-items: flex-start; } }
</style>
