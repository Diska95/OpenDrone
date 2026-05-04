<template>
  <div class="wrap">
    <div class="page-label">// ordini</div>
    <div class="page-title">I miei ordini</div>
    <div class="page-sub">Tutti gli ordini effettuati con il loro stato corrente.</div>

    <p v-if="loading" class="empty">Caricamento...</p>
    <div v-else-if="!orders.length" class="empty">
      Nessun ordine ancora.
      <router-link to="/projects" class="btn primary" style="margin-top: 14px">Esplora il catalogo →</router-link>
    </div>

    <div v-else class="order-list">
      <router-link v-for="order in orders" :key="order.id" :to="`/orders/${order.id}`" class="order-row">
        <div class="o-left">
          <div class="o-id">#{{ order.id }}</div>
          <span class="status-pill" :class="`s-${statusClass(order.status)}`">{{ statusLabel(order.status) }}</span>
        </div>
        <div class="o-main">
          <div class="o-title">{{ order.project_data?.title }}</div>
          <div class="o-meta">
            <span>{{ order.mode === 'kit' ? '🔧 Kit' : '✓ Assemblato' }}</span>
            <span v-if="order.is_fast_track">⚡ Fast Track</span>
            <span>{{ new Date(order.created_at).toLocaleDateString('it-IT') }}</span>
          </div>
        </div>
        <div class="o-price">
          <div class="op-num">€{{ order.total_amount }}</div>
          <div class="op-arr">→</div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ordersApi } from '@/api/orders'

const orders = ref([])
const loading = ref(true)

const STATUS_LABELS = {
  pending: 'in attesa',
  payment_confirmed: 'pagato',
  assigned_print: 'in stampa',
  printing: 'in stampa',
  print_done: 'stampato',
  assigned_assembly: 'in assemblaggio',
  assembling: 'in assemblaggio',
  testing: 'in test',
  shipped: 'spedito',
  delivered: 'consegnato',
  disputed: 'in disputa',
  cancelled: 'annullato',
  refunded: 'rimborsato',
}

function statusClass(s) {
  if (['delivered', 'shipped'].includes(s)) return 'success'
  if (['disputed', 'cancelled', 'refunded'].includes(s)) return 'danger'
  if (['pending'].includes(s)) return 'warn'
  return 'info'
}
function statusLabel(s) { return STATUS_LABELS[s] || s }

onMounted(async () => {
  try {
    const { data } = await ordersApi.getOrders()
    orders.value = data.results || data
  } finally { loading.value = false }
})
</script>

<style scoped>
.order-list { display: flex; flex-direction: column; gap: 8px; }
.order-row {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 18px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  transition: border-color .15s;
}
.order-row:hover { border-color: rgba(93,255,159,.3); }

.o-left { display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.o-id { font-family: var(--mono); font-size: 12px; color: var(--muted); }
.status-pill {
  font-family: var(--mono);
  font-size: 10px;
  padding: 3px 9px;
  border-radius: 20px;
  border: 1px solid;
  text-transform: lowercase;
}
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-warn { color: #ff9060; background: rgba(255,107,53,.06); border-color: rgba(255,107,53,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }
.s-info { color: var(--muted); background: var(--surface); border-color: var(--border); }

.o-title { font-size: 14px; font-weight: 700; }
.o-meta { display: flex; gap: 14px; font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 4px; }

.o-price { display: flex; align-items: center; gap: 10px; }
.op-num { font-size: 18px; font-weight: 800; color: var(--accent); letter-spacing: -.5px; }
.op-arr { color: var(--muted); }

.empty { color: var(--muted); font-family: var(--mono); padding: 60px 0; text-align: center; font-size: 13px; }
</style>
