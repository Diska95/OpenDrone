<template>
  <div class="wrap" style="max-width: 600px">
    <div class="page-label">// profilo</div>
    <div class="page-title">Account</div>
    <div class="page-sub">Gestisci dati personali e ruoli attivi.</div>

    <div class="card">
      <div class="profile-head">
        <div class="avatar">{{ initials }}</div>
        <div>
          <h3>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</h3>
          <p class="muted">{{ auth.user?.email }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="page-label">Dati personali</div>
      <form @submit.prevent="saveProfile">
        <div class="field-row">
          <div class="field">
            <label>Nome</label>
            <input class="input" v-model="form.first_name" />
          </div>
          <div class="field">
            <label>Cognome</label>
            <input class="input" v-model="form.last_name" />
          </div>
        </div>
        <div class="field">
          <label>Email</label>
          <input class="input" :value="auth.user?.email" disabled />
        </div>
        <div class="field">
          <label>Bio</label>
          <textarea class="textarea" v-model="form.bio" rows="3" placeholder="Raccontaci di te..."></textarea>
        </div>
        <button type="submit" class="btn primary">Salva modifiche</button>
      </form>
    </div>

    <div class="card">
      <div class="page-label">Ruoli attivi</div>
      <div class="roles-grid">
        <span v-for="role in auth.user?.roles || []" :key="role" class="role-pill" :class="roleClassFor(role)">
          {{ roleLabel(role) }}
        </span>
      </div>
      <p class="muted" style="margin-top: 12px; font-family: var(--mono); font-size: 11px">
        Per cambiare ruolo o aggiungere un nodo di stampa contatta il team admin.
      </p>
    </div>

    <button class="btn-full outline" @click="handleLogout">Esci dall'account</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { authApi } from '@/api/auth'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const form = ref({ first_name: '', last_name: '', bio: '' })

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  const f = u.first_name?.[0] || ''
  const l = u.last_name?.[0] || ''
  return (f + l) || u.email?.[0]?.toUpperCase() || '?'
})

const ROLE_LABELS = {
  customer: 'Cliente',
  designer: 'Designer',
  print_node: 'Nodo stampa',
  assembly_center: 'Centro assemblaggio',
  admin: 'Admin',
}
function roleLabel(r) { return ROLE_LABELS[r] || r }
function roleClassFor(r) {
  if (r === 'admin') return 'admin'
  if (['designer', 'print_node', 'assembly_center'].includes(r)) return 'creator'
  return 'user'
}

onMounted(() => {
  if (auth.user) {
    form.value.first_name = auth.user.first_name || ''
    form.value.last_name = auth.user.last_name || ''
    form.value.bio = auth.user.bio || ''
  }
})

async function saveProfile() {
  await authApi.updateMe(form.value)
  await auth.fetchMe()
  toast.show('✓ Profilo aggiornato')
}

async function handleLogout() {
  await auth.logout()
  toast.show('Disconnesso')
  router.push('/')
}
</script>

<style scoped>
.profile-head { display: flex; align-items: center; gap: 14px; }
.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--surface);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  color: var(--accent);
}
.profile-head h3 { font-size: 16px; font-weight: 700; }
.muted { color: var(--muted); font-size: 13px; margin-top: 2px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.roles-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.role-pill {
  font-family: var(--mono);
  font-size: 11px;
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid;
}
.role-pill.user { color: var(--muted); border-color: var(--border); background: var(--surface); }
.role-pill.creator { color: var(--accent); border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.role-pill.admin { color: var(--accent2); border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }
</style>
