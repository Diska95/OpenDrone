<template>
  <div class="wrap">
    <div class="dash-header">
      <div class="page-label">// dashboard</div>
      <h1>Ciao {{ greeting }} <span class="wave">👋</span></h1>
      <p class="role-text">Operi come <span class="role-tag" :class="primaryRoleClass">{{ primaryRole }}</span></p>
    </div>

    <!-- Designer -->
    <div v-if="auth.isDesigner">
      <div class="stat-grid">
        <div class="stat-card hi">
          <div class="snum">{{ stats?.projects_published || 0 }}</div>
          <div class="slbl2">Progetti pubblicati</div>
        </div>
        <div class="stat-card">
          <div class="snum">{{ stats?.projects_draft || 0 }}</div>
          <div class="slbl2">Bozze</div>
        </div>
        <div class="stat-card">
          <div class="snum">{{ stats?.total_orders || 0 }}</div>
          <div class="slbl2">Ordini totali</div>
        </div>
        <div class="stat-card hi">
          <div class="snum">€{{ Number(stats?.total_royalties_earned || 0).toFixed(0) }}</div>
          <div class="slbl2">Royalty maturate</div>
        </div>
        <div class="stat-card">
          <div class="snum">€{{ Number(stats?.pending_royalties || 0).toFixed(0) }}</div>
          <div class="slbl2">Royalty in attesa</div>
        </div>
        <div class="stat-card">
          <div class="snum">★ {{ Number(stats?.avg_rating || 0).toFixed(1) }}</div>
          <div class="slbl2">Rating medio</div>
        </div>
      </div>
    </div>

    <!-- Print Node -->
    <div v-else-if="auth.isPrintNode">
      <div class="stat-grid">
        <div class="stat-card hi">
          <div class="snum">{{ stats?.orders_active || 0 }}</div>
          <div class="slbl2">Ordini attivi</div>
        </div>
        <div class="stat-card">
          <div class="snum">{{ stats?.orders_completed || 0 }}</div>
          <div class="slbl2">Completati</div>
        </div>
        <div class="stat-card">
          <div class="snum">€{{ Number(stats?.total_revenue || 0).toFixed(0) }}</div>
          <div class="slbl2">Revenue totale</div>
        </div>
      </div>
    </div>

    <!-- Assembly Center -->
    <div v-else-if="auth.isAssemblyCenter">
      <div class="stat-grid">
        <div class="stat-card hi">
          <div class="snum">{{ stats?.orders_active || 0 }}</div>
          <div class="slbl2">In lavorazione</div>
        </div>
        <div class="stat-card">
          <div class="snum">{{ stats?.orders_completed || 0 }}</div>
          <div class="slbl2">Consegnati</div>
        </div>
        <div class="stat-card">
          <div class="snum">€{{ Number(stats?.total_revenue || 0).toFixed(0) }}</div>
          <div class="slbl2">Revenue totale</div>
        </div>
      </div>
    </div>

    <!-- Customer -->
    <div v-else>
      <div class="card welcome-card">
        <h3>Benvenuto su OpenDrone!</h3>
        <p>Esplora il catalogo, trova un progetto drone open e ordinalo come kit o pre-assemblato.</p>
        <router-link to="/projects" class="btn primary" style="margin-top: 14px">Esplora il catalogo →</router-link>
      </div>
    </div>

    <div class="actions-section">
      <div class="page-label">// azioni rapide</div>
      <div class="action-list">
        <router-link to="/projects" class="dash-action">
          <div class="da-icon">⬡</div>
          <div class="da-info">
            <div class="da-title">Esplora catalogo</div>
            <div class="da-sub">Tutti i progetti pubblicati</div>
          </div>
          <div class="da-arr">→</div>
        </router-link>
        <router-link to="/orders" class="dash-action">
          <div class="da-icon">📦</div>
          <div class="da-info">
            <div class="da-title">I miei ordini</div>
            <div class="da-sub">Stato e tracking</div>
          </div>
          <div class="da-arr">→</div>
        </router-link>
        <router-link v-if="auth.isDesigner" to="/my-projects" class="dash-action">
          <div class="da-icon">📂</div>
          <div class="da-info">
            <div class="da-title">I miei progetti</div>
            <div class="da-sub">Bozze, in revisione, pubblicati</div>
          </div>
          <div class="da-arr">→</div>
        </router-link>
        <router-link v-if="auth.isDesigner" to="/projects/new" class="dash-action">
          <div class="da-icon">⬆</div>
          <div class="da-info">
            <div class="da-title">Carica nuovo progetto</div>
            <div class="da-sub">STL + BOM + descrizione</div>
          </div>
          <div class="da-arr">→</div>
        </router-link>
        <router-link to="/profile" class="dash-action">
          <div class="da-icon">👤</div>
          <div class="da-info">
            <div class="da-title">Profilo</div>
            <div class="da-sub">Dati account e ruoli</div>
          </div>
          <div class="da-arr">→</div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'

const auth = useAuthStore()
const stats = ref(null)

const greeting = computed(() => auth.user?.first_name || auth.user?.email?.split('@')[0] || 'amico')

const primaryRole = computed(() => {
  if (!auth.user?.roles?.length) return 'utente'
  const order = ['admin', 'designer', 'print_node', 'assembly_center', 'customer']
  for (const r of order) if (auth.user.roles.includes(r)) {
    return { admin: 'admin', designer: 'designer', print_node: 'nodo stampa', assembly_center: 'centro assemblaggio', customer: 'cliente' }[r]
  }
  return auth.user.roles[0]
})
const primaryRoleClass = computed(() => {
  if (auth.user?.roles?.includes('admin')) return 'admin'
  if (auth.user?.roles?.some(r => ['designer', 'print_node', 'assembly_center'].includes(r))) return 'creator'
  return 'user'
})

onMounted(async () => {
  try {
    let endpoint = null
    if (auth.isDesigner) endpoint = '/dashboard/designer/'
    else if (auth.isPrintNode) endpoint = '/dashboard/print-node/'
    else if (auth.isAssemblyCenter) endpoint = '/dashboard/assembly/'
    if (endpoint) {
      const { data } = await client.get(endpoint)
      stats.value = data
    }
  } catch {}
})
</script>

<style scoped>
.dash-header { padding-bottom: 24px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; font-weight: 800; letter-spacing: -.5px; margin-top: 4px; }
.wave { display: inline-block; }
.role-text { font-family: var(--mono); font-size: 12px; color: var(--muted); margin-top: 6px; }
.role-tag {
  display: inline-block;
  font-family: var(--mono);
  font-size: 10px;
  padding: 2px 9px;
  border-radius: 20px;
  border: 1px solid;
  margin-left: 4px;
}
.role-tag.user { color: var(--muted); border-color: var(--border); }
.role-tag.creator { color: var(--accent); border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.role-tag.admin { color: var(--accent2); border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }

.stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-bottom: 32px; }
.stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
}
.stat-card.hi { border-color: rgba(93,255,159,.3); }
.snum { font-size: 26px; font-weight: 800; letter-spacing: -1px; }
.stat-card.hi .snum { color: var(--accent); }
.slbl2 { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }

.welcome-card { text-align: center; padding: 32px; margin-bottom: 32px; }
.welcome-card h3 { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.welcome-card p { color: var(--muted); font-size: 14px; }

.actions-section { margin-top: 8px; }
.action-list { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
.dash-action {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color .15s;
  color: inherit;
}
.dash-action:hover { border-color: var(--accent); }
.da-icon { font-size: 22px; line-height: 1; }
.da-info { flex: 1; }
.da-title { font-size: 14px; font-weight: 700; }
.da-sub { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-top: 2px; }
.da-arr { color: var(--muted); }
</style>
