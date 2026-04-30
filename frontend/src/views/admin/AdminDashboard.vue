<template>
  <div class="wrap wide">
    <div class="page-label">// pannello admin</div>
    <h1 class="page-title">Operatore di piattaforma</h1>
    <p class="page-sub">Stato generale di PolyDrone e azioni rapide.</p>

    <!-- Stats grid -->
    <div class="stat-grid">
      <div class="stat-card hi">
        <div class="snum">{{ stats?.orders_total || 0 }}</div>
        <div class="slbl">Ordini totali</div>
      </div>
      <div class="stat-card warn">
        <div class="snum">{{ stats?.orders_pending_payment || 0 }}</div>
        <div class="slbl">In attesa pagamento</div>
      </div>
      <div class="stat-card">
        <div class="snum">{{ stats?.orders_active || 0 }}</div>
        <div class="slbl">Ordini attivi</div>
      </div>
      <div class="stat-card">
        <div class="snum">{{ stats?.orders_delivered || 0 }}</div>
        <div class="slbl">Consegnati</div>
      </div>
      <div class="stat-card danger" v-if="stats?.orders_disputed > 0">
        <div class="snum">{{ stats.orders_disputed }}</div>
        <div class="slbl">Dispute aperte</div>
      </div>
      <div class="stat-card hi">
        <div class="snum">€{{ Number(stats?.total_gmv || 0).toFixed(0) }}</div>
        <div class="slbl">GMV totale</div>
      </div>
      <div class="stat-card hi">
        <div class="snum">€{{ Number(stats?.total_commission || 0).toFixed(0) }}</div>
        <div class="slbl">Commissioni</div>
      </div>
      <div class="stat-card warn" v-if="stats?.projects_pending > 0">
        <div class="snum">{{ stats.projects_pending }}</div>
        <div class="slbl">Progetti in attesa</div>
      </div>
      <div class="stat-card">
        <div class="snum">{{ stats?.projects_published || 0 }}</div>
        <div class="slbl">Progetti pubblicati</div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="page-label" style="margin-top: 32px">// azioni rapide</div>
    <div class="actions-grid">
      <router-link to="/admin/projects" class="action-card">
        <div class="ai">📂</div>
        <div class="ah">Modera progetti</div>
        <div class="as">Approva o rifiuta i progetti caricati dai designer.</div>
        <div v-if="stats?.projects_pending" class="badge-warn">{{ stats.projects_pending }} in attesa</div>
      </router-link>
      <router-link to="/admin/users" class="action-card">
        <div class="ai">👥</div>
        <div class="ah">Gestisci utenti</div>
        <div class="as">Attiva/disattiva account, certifica nodi e centri.</div>
      </router-link>
      <router-link to="/admin/orders" class="action-card">
        <div class="ai">📦</div>
        <div class="ah">Gestisci ordini</div>
        <div class="as">Tutti gli ordini, cambio stato manuale, dispute.</div>
        <div v-if="stats?.orders_disputed" class="badge-danger">{{ stats.orders_disputed }} dispute</div>
      </router-link>
      <a href="http://localhost:8001/admin/marketplace/brand/" target="_blank" class="action-card">
        <div class="ai">🏷</div>
        <div class="ah">Brand catalog</div>
        <div class="as">Gestisci brand partner e link affiliate.</div>
        <div class="badge-info">Django admin</div>
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'

const stats = ref(null)

onMounted(async () => {
  try {
    const { data } = await adminApi.getStats()
    stats.value = data
  } catch {}
})
</script>

<style scoped>
.stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px; }
.stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
}
.stat-card.hi { border-color: rgba(93,255,159,.3); }
.stat-card.warn { border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.04); }
.stat-card.danger { border-color: rgba(255,79,79,.3); background: rgba(255,79,79,.04); }

.snum { font-size: 26px; font-weight: 800; letter-spacing: -1px; line-height: 1.1; font-family: var(--font-display); }
.stat-card.hi .snum { color: var(--accent); }
.stat-card.warn .snum { color: #ff9060; }
.stat-card.danger .snum { color: #ff8080; }
.slbl { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }

.actions-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-top: 12px; }
.action-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  display: block;
  text-decoration: none;
  color: inherit;
  transition: border-color .15s, transform .15s;
  position: relative;
}
.action-card:hover { border-color: rgba(93,255,159,.3); transform: translateY(-2px); }
.ai { font-size: 28px; margin-bottom: 10px; }
.ah { font-size: 15px; font-weight: 700; font-family: var(--font-display); }
.as { font-size: 13px; color: var(--muted); margin-top: 4px; line-height: 1.5; }

.badge-warn, .badge-danger, .badge-info {
  position: absolute; top: 12px; right: 12px;
  font-family: var(--mono); font-size: 10px;
  padding: 3px 9px; border-radius: 20px; border: 1px solid;
  text-transform: lowercase;
}
.badge-warn { color: #ff9060; border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }
.badge-danger { color: #ff8080; border-color: rgba(255,79,79,.3); background: rgba(255,79,79,.06); }
.badge-info { color: var(--muted); border-color: var(--border); background: var(--surface); }
</style>
