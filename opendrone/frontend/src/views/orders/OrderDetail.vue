<template>
  <div class="wrap">
    <router-link to="/orders" class="back-link">← I miei ordini</router-link>

    <div v-if="order">
      <div class="card order-head">
        <div>
          <div class="page-label">Ordine #{{ order.id }}</div>
          <h1>{{ order.project_data?.title }}</h1>
          <p class="muted">Creato il {{ new Date(order.created_at).toLocaleString('it-IT') }}</p>
        </div>
        <span class="status-pill" :class="`s-${statusClass(order.status)}`">{{ statusLabel(order.status) }}</span>
      </div>

      <div class="grid">
        <div class="card">
          <div class="page-label">Dettagli</div>
          <div class="kv">
            <span>Modalità</span><strong>{{ order.mode === 'kit' ? 'Kit' : 'Assemblato' }}</strong>
          </div>
          <div class="kv">
            <span>Quantità</span><strong>{{ order.quantity }}</strong>
          </div>
          <div class="kv">
            <span>Fast Track</span><strong>{{ order.is_fast_track ? 'Sì ⚡' : 'No' }}</strong>
          </div>
          <div v-if="order.tracking_number" class="kv">
            <span>Tracking</span><strong class="mono">{{ order.tracking_number }}</strong>
          </div>
        </div>

        <div class="card">
          <div class="page-label">Riepilogo costi</div>
          <div class="kv"><span>Licenza design</span><strong>€{{ order.design_fee }}</strong></div>
          <div class="kv"><span>Stampa</span><strong>€{{ order.print_cost }}</strong></div>
          <div class="kv"><span>Componenti</span><strong>€{{ order.components_cost }}</strong></div>
          <div v-if="parseFloat(order.assembly_cost) > 0" class="kv"><span>Assemblaggio</span><strong>€{{ order.assembly_cost }}</strong></div>
          <div v-if="parseFloat(order.fast_track_fee) > 0" class="kv"><span>Fast Track</span><strong>€{{ order.fast_track_fee }}</strong></div>
          <div class="kv"><span>Commissione</span><strong>€{{ order.platform_commission }}</strong></div>
          <div class="kv total"><span>Totale</span><strong>€{{ order.total_amount }}</strong></div>
        </div>
      </div>

      <div class="card">
        <div class="page-label">Storico stati</div>
        <div v-if="!order.history?.length" class="empty">Nessun aggiornamento.</div>
        <div v-else class="timeline">
          <div v-for="h in order.history" :key="h.id" class="tl-item">
            <span class="tl-dot"></span>
            <div>
              <div class="tl-status">{{ statusLabel(h.status) }}</div>
              <div v-if="h.note" class="tl-note">{{ h.note }}</div>
              <div class="tl-time">{{ new Date(h.created_at).toLocaleString('it-IT') }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p v-else-if="loading" class="empty">Caricamento...</p>
    <p v-else class="empty">Ordine non trovato.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ordersApi } from '@/api/orders'

const route = useRoute()
const order = ref(null)
const loading = ref(true)

const STATUS_LABELS = {
  pending: 'in attesa pagamento',
  payment_confirmed: 'pagamento confermato',
  assigned_print: 'assegnato a nodo',
  printing: 'in stampa',
  print_done: 'stampa completata',
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
    const { data } = await ordersApi.getOrder(route.params.id)
    order.value = data
  } finally { loading.value = false }
})
</script>

<style scoped>
.back-link { font-family: var(--mono); font-size: 12px; color: var(--muted); margin-bottom: 16px; display: inline-block; }
.back-link:hover { color: var(--accent); }

.order-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.order-head h1 { font-size: 22px; font-weight: 800; letter-spacing: -.5px; margin-top: 4px; }
.muted { color: var(--muted); font-family: var(--mono); font-size: 12px; margin-top: 4px; }

.status-pill {
  font-family: var(--mono);
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid;
  text-transform: lowercase;
}
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-warn { color: #ff9060; background: rgba(255,107,53,.06); border-color: rgba(255,107,53,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }
.s-info { color: var(--muted); background: var(--surface); border-color: var(--border); }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }

.kv { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.kv:last-child { border-bottom: none; }
.kv span { color: var(--muted); font-family: var(--mono); font-size: 12px; }
.kv.total { padding-top: 14px; margin-top: 6px; border-top: 2px solid var(--border); border-bottom: none; }
.kv.total span { color: var(--text); font-family: var(--font); font-size: 14px; font-weight: 700; }
.kv.total strong { color: var(--accent); font-size: 18px; }
.mono { font-family: var(--mono); }

.timeline { display: flex; flex-direction: column; gap: 12px; margin-top: 8px; }
.tl-item { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.tl-item:last-child { border-bottom: none; }
.tl-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-top: 6px; flex-shrink: 0; }
.tl-status { font-size: 13px; font-weight: 700; text-transform: capitalize; }
.tl-note { font-size: 12px; color: var(--muted); margin-top: 2px; }
.tl-time { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 4px; }

.empty { color: var(--muted); font-family: var(--mono); padding: 40px 0; text-align: center; font-size: 13px; }
</style>
