<template>
  <div class="wrap wide">
    <div class="page-label">// admin / utenti</div>
    <h1 class="page-title">Gestione utenti</h1>
    <p class="page-sub">Tutti gli iscritti alla piattaforma. Attiva/disattiva account, certifica nodi stampa e centri di assemblaggio.</p>

    <div class="filters">
      <button class="chip" :class="{ on: roleFilter === '' }" @click="setRole('')">Tutti ({{ users.length }})</button>
      <button class="chip" :class="{ on: roleFilter === 'designer' }" @click="setRole('designer')">Designer ({{ countByRole('designer') }})</button>
      <button class="chip" :class="{ on: roleFilter === 'print_node' }" @click="setRole('print_node')">Nodi stampa ({{ countByRole('print_node') }})</button>
      <button class="chip" :class="{ on: roleFilter === 'assembly_center' }" @click="setRole('assembly_center')">Assemblaggio ({{ countByRole('assembly_center') }})</button>
      <button class="chip" :class="{ on: roleFilter === 'customer' }" @click="setRole('customer')">Clienti ({{ countByRole('customer') }})</button>
      <button class="chip" :class="{ on: roleFilter === 'admin' }" @click="setRole('admin')">Admin ({{ countByRole('admin') }})</button>
    </div>

    <div class="search-bar">
      <div class="search-input-wrap">
        <input class="input search-input" type="search" v-model="search" placeholder="Cerca per nome, cognome o email…" />
        <button v-if="search" class="search-clear" type="button" @click="search = ''" aria-label="Pulisci">✕</button>
      </div>
      <span v-if="search" class="search-meta">{{ filtered.length }} {{ filtered.length === 1 ? 'risultato' : 'risultati' }}</span>
    </div>

    <p v-if="loading" class="empty">Caricamento...</p>
    <div v-else-if="!filtered.length" class="empty-card card">
      <p>Nessun utente in questa vista.</p>
    </div>

    <div v-else class="user-list">
      <div v-for="u in filtered" :key="u.id" class="user-row card">
        <div class="avatar">{{ initials(u) }}</div>
        <div class="info">
          <div class="info-head">
            <strong>{{ fullName(u) }}</strong>
            <span class="status-pill" :class="u.is_active ? 's-success' : 's-danger'">{{ u.is_active ? 'attivo' : 'disattivo' }}</span>
            <span v-if="hasCertifiedProfile(u)" class="status-pill s-success">★ certificato</span>
          </div>
          <div class="email">{{ u.email }}</div>
          <div class="roles">
            <label class="role-edit">
              <span class="re-label">Ruolo:</span>
              <select class="re-select"
                      :value="primaryRole(u)"
                      :disabled="busy[u.id] || (u.id === auth.user?.id && primaryRole(u) === 'admin')"
                      :title="u.id === auth.user?.id && primaryRole(u) === 'admin' ? 'Non puoi togliere admin a te stesso' : ''"
                      @change="changeRole(u, $event.target.value)">
                <option value="customer">Cliente</option>
                <option value="designer">Designer</option>
                <option value="print_node">Nodo stampa</option>
                <option value="assembly_center">Centro assemblaggio</option>
                <option value="admin">Admin</option>
              </select>
            </label>
          </div>
        </div>
        <div class="actions">
          <button v-if="canCertify(u)" class="btn outline" :disabled="busy[u.id]" @click="certify(u)">
            {{ hasCertifiedProfile(u) ? 'Annulla certifica' : '★ Certifica' }}
          </button>
          <button class="btn"
                  :class="u.is_active ? 'danger' : 'primary'"
                  :disabled="busy[u.id] || (u.id === auth.user?.id && u.is_active)"
                  :title="u.id === auth.user?.id && u.is_active ? 'Non puoi disattivare te stesso' : ''"
                  @click="toggleActive(u)">
            {{ u.is_active ? 'Disattiva' : 'Attiva' }}<span v-if="u.id === auth.user?.id"> (tu)</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'

const toast = useToastStore()
const auth = useAuthStore()
const users = ref([])
const loading = ref(true)
const roleFilter = ref('')
const search = ref('')
const busy = reactive({})

const ROLE_LABELS = {
  customer: 'cliente',
  designer: 'designer',
  print_node: 'nodo stampa',
  assembly_center: 'assemblaggio',
  admin: 'admin',
}
function roleLabel(r) { return ROLE_LABELS[r] || r }
function roleClassFor(r) {
  if (r === 'admin') return 'admin'
  if (['designer','print_node','assembly_center'].includes(r)) return 'creator'
  return 'user'
}

function fullName(u) { return `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.email.split('@')[0] }
function initials(u) {
  const f = u.first_name?.[0] || ''
  const l = u.last_name?.[0] || ''
  return (f + l) || u.email[0].toUpperCase()
}
function hasCertifiedProfile(u) {
  // I designer non si certificano per persona ma per singolo progetto
  // (workflow di approvazione progetti in /admin/projects).
  return u.print_node_profile?.is_certified || u.assembly_profile?.is_certified
}
function canCertify(u) {
  return u.print_node_profile || u.assembly_profile
}

const filtered = computed(() => {
  let list = users.value
  if (roleFilter.value) {
    list = list.filter(u => u.roles?.includes(roleFilter.value))
  }
  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter(u => {
      const haystack = [
        u.email,
        u.first_name,
        u.last_name,
        `${u.first_name || ''} ${u.last_name || ''}`,
      ].filter(Boolean).join(' ').toLowerCase()
      return haystack.includes(q)
    })
  }
  return list
})

function countByRole(r) { return users.value.filter(u => u.roles?.includes(r)).length }

function setRole(r) { roleFilter.value = r }

async function load() {
  loading.value = true
  try {
    const { data } = await adminApi.getUsers()
    users.value = data.results || data
  } finally {
    loading.value = false
  }
}

async function toggleActive(u) {
  if (u.id === auth.user?.id && u.is_active) {
    toast.show('⚠ Non puoi disattivare il tuo stesso account')
    return
  }
  busy[u.id] = true
  try {
    const { data } = await adminApi.updateUser(u.id, { is_active: !u.is_active })
    Object.assign(u, data)
    toast.show(`${u.email}: ${u.is_active ? 'attivato' : 'disattivato'}`)
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore')
  } finally {
    busy[u.id] = false
  }
}

function primaryRole(u) {
  // Ogni utente dovrebbe avere un solo ruolo. Se ne ha piu' (utenti pre-migration),
  // usa la priorita' admin > designer > print_node > assembly_center > customer.
  const order = ['admin', 'designer', 'print_node', 'assembly_center', 'customer']
  for (const r of order) if (u.roles?.includes(r)) return r
  return 'customer'
}

async function changeRole(u, newRole) {
  if (newRole === primaryRole(u)) return // nessuna modifica
  if (!confirm(`Confermi cambio ruolo per ${u.email}?\n${roleLabel(primaryRole(u))} → ${roleLabel(newRole)}`)) {
    return
  }
  busy[u.id] = true
  try {
    const { data } = await adminApi.updateUser(u.id, { role: newRole })
    Object.assign(u, data)
    toast.show(`✓ ${u.email}: ruolo aggiornato a ${roleLabel(newRole)}`)
  } catch (e) {
    toast.show(e.response?.data?.detail || '✗ Errore cambio ruolo')
  } finally {
    busy[u.id] = false
  }
}

async function certify(u) {
  let profile = null
  if (u.print_node_profile) profile = 'print_node'
  else if (u.assembly_profile) profile = 'assembly_center'
  else if (u.designer_profile) profile = 'designer'
  if (!profile) return
  const newCertified = !hasCertifiedProfile(u)
  busy[u.id] = true
  try {
    const { data } = await adminApi.updateUser(u.id, { certify_profile: profile, is_certified: newCertified })
    Object.assign(u, data)
    toast.show(newCertified ? `★ ${u.email} certificato` : `Certificazione rimossa`)
  } catch {
    toast.show('✗ Errore')
  } finally {
    busy[u.id] = false
  }
}

onMounted(load)
</script>

<style scoped>
.filters { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
}
.search-input-wrap {
  position: relative;
  flex: 1;
  max-width: 420px;
}
.search-input { width: 100%; padding-right: 36px; }
.search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--muted);
  font-size: 14px;
  cursor: pointer;
  padding: 4px 6px;
}
.search-clear:hover { color: var(--text); }
.search-meta {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
}
@media (max-width: 480px) {
  .search-input-wrap { max-width: 100%; }
}
.chip { background: none; border: 1px solid var(--border); color: var(--muted); padding: 5px 13px; border-radius: 20px; font-family: var(--font); font-size: 12px; cursor: pointer; transition: all .15s; }
.chip:hover, .chip.on { border-color: var(--accent); color: var(--accent); background: rgba(93,255,159,.06); }

.empty { color: var(--muted); font-family: var(--mono); padding: 60px 0; text-align: center; }
.empty-card { text-align: center; padding: 40px; }

.user-list { display: flex; flex-direction: column; gap: 10px; }
.user-row { display: grid; grid-template-columns: 56px 1fr auto; gap: 16px; align-items: center; padding: 14px 18px; margin-bottom: 0; }

.avatar { width: 56px; height: 56px; border-radius: 50%; background: var(--surface); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: var(--accent); font-family: var(--font-display); }

.info { min-width: 0; }
.info-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.info-head strong { font-size: 14px; font-weight: 700; }
.email { font-family: var(--mono); font-size: 12px; color: var(--muted); margin-top: 2px; }
.roles { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }

.role-pill { font-family: var(--mono); font-size: 10px; padding: 2px 8px; border-radius: 20px; border: 1px solid; text-transform: lowercase; }
.role-pill.user { color: var(--muted); border-color: var(--border); background: var(--surface); }
.role-pill.creator { color: var(--accent); border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.role-pill.admin { color: var(--accent2); border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }

.role-edit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.re-label {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .5px;
}
.re-select {
  font-family: var(--font);
  font-size: 12px;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 24px 4px 10px;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%237a7a90' stroke-width='1.4' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  transition: border-color .15s, color .15s;
}
.re-select:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.re-select:disabled { opacity: .5; cursor: not-allowed; }
.re-select option { background: var(--card); color: var(--text); }

.actions { display: flex; gap: 6px; flex-shrink: 0; flex-wrap: wrap; }

.status-pill { font-family: var(--mono); font-size: 10px; padding: 3px 9px; border-radius: 20px; border: 1px solid; text-transform: lowercase; }
.s-success { color: var(--accent); background: rgba(93,255,159,.06); border-color: rgba(93,255,159,.3); }
.s-danger { color: #ff8080; background: rgba(255,79,79,.06); border-color: rgba(255,79,79,.3); }

@media (max-width: 720px) { .user-row { grid-template-columns: 1fr; } }
</style>
