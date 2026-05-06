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

    <div class="card privacy-card">
      <div class="page-label">Privacy e dati personali</div>
      <p class="muted" style="margin-bottom: 16px">
        I tuoi diritti GDPR (artt. 15-17, 20). Per il dettaglio vedi la
        <router-link to="/privacy" style="color: var(--accent)">Privacy Policy</router-link>.
      </p>

      <div class="privacy-actions">
        <button class="btn outline" :disabled="exporting" @click="handleExport">
          {{ exporting ? 'Generazione...' : '↓ Scarica i miei dati (JSON)' }}
        </button>
        <p class="hint">Riceverai un file JSON con tutti i dati personali che trattiamo.</p>
      </div>

      <hr class="sep" />

      <div class="privacy-actions">
        <button class="btn danger" @click="showDeleteModal = true">
          ⚠ Cancella il mio account
        </button>
        <p class="hint">
          Operazione irreversibile. I dati personali vengono rimossi o anonimizzati.
          Ordini storici e documenti contabili sono conservati per 10 anni in forma
          non attribuibile (obbligo fiscale).
        </p>
      </div>
    </div>

    <button class="btn-full outline" @click="handleLogout">Esci dall'account</button>

    <!-- Modal cancellazione account -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal">
        <h3>Cancella account</h3>
        <p class="muted">
          Stai per cancellare definitivamente il tuo account OpenDrone. Saranno rimossi:
        </p>
        <ul class="modal-list">
          <li>Profilo (nome, email, bio, avatar)</li>
          <li>Eventuale profilo Designer / Nodo stampa / Centro assemblaggio</li>
          <li>Contenuto delle tue recensioni</li>
          <li>Tutte le tue sessioni attive</li>
        </ul>
        <p class="muted">
          <strong>Saranno conservati per 10 anni</strong> in forma non attribuibile,
          per obbligo contabile/fiscale: ordini effettuati, fatture, royalty maturate.
        </p>

        <div v-if="deleteError" class="alert danger" style="margin: 12px 0">{{ deleteError }}</div>

        <div class="field" style="margin-top: 16px">
          <label>Password attuale</label>
          <input class="input" type="password" v-model="deleteForm.password" placeholder="••••••••" />
        </div>

        <div class="field">
          <label>Per confermare digita <code>ELIMINA</code></label>
          <input class="input" v-model="deleteForm.confirmation" placeholder="ELIMINA" />
        </div>

        <div class="modal-actions">
          <button class="btn outline" @click="closeDeleteModal">Annulla</button>
          <button class="btn danger" :disabled="deleting" @click="handleDelete">
            {{ deleting ? 'Cancellazione...' : 'Cancella definitivamente' }}
          </button>
        </div>
      </div>
    </div>
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

// ─── GDPR — diritti dell'interessato ───────────────────────────
const exporting = ref(false)
const showDeleteModal = ref(false)
const deleting = ref(false)
const deleteError = ref('')
const deleteForm = ref({ password: '', confirmation: '' })

async function handleExport() {
  exporting.value = true
  try {
    const { data } = await authApi.exportMyData()
    // Browser download del JSON
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `opendrone-data-export-${auth.user?.id || 'me'}.json`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    toast.show('✓ Dati scaricati')
  } catch (e) {
    toast.show('Errore durante l\'export. Riprova.')
  } finally {
    exporting.value = false
  }
}

function closeDeleteModal() {
  showDeleteModal.value = false
  deleteError.value = ''
  deleteForm.value = { password: '', confirmation: '' }
}

async function handleDelete() {
  deleteError.value = ''
  if (!deleteForm.value.password) {
    deleteError.value = 'Inserisci la password.'
    return
  }
  if (deleteForm.value.confirmation.trim().toUpperCase() !== 'ELIMINA') {
    deleteError.value = 'Per confermare digita esattamente "ELIMINA".'
    return
  }
  deleting.value = true
  try {
    await authApi.deleteAccount({
      password: deleteForm.value.password,
      confirmation: deleteForm.value.confirmation,
    })
    // Pulizia locale + redirect
    await auth.logout()
    toast.show('Account cancellato. Arrivederci.')
    router.push('/')
  } catch (e) {
    const errs = e.response?.data
    if (errs?.password) deleteError.value = errs.password
    else if (errs?.confirmation) deleteError.value = errs.confirmation
    else if (errs?.detail) deleteError.value = errs.detail
    else deleteError.value = 'Errore durante la cancellazione. Riprova.'
  } finally {
    deleting.value = false
  }
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

.privacy-card { border-color: rgba(255,79,79,.18); }
.privacy-actions { display: flex; flex-direction: column; gap: 6px; }
.privacy-actions .btn { align-self: flex-start; }
.privacy-actions .hint {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
  line-height: 1.5;
  margin-top: 2px;
}
.sep {
  border: none;
  border-top: 1px solid var(--border);
  margin: 18px 0;
}

.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 500;
  padding: 20px;
}
.modal {
  background: var(--card);
  border: 1px solid var(--danger);
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}
.modal h3 {
  font-family: var(--font-display);
  font-size: 20px;
  margin-bottom: 12px;
  color: var(--danger);
}
.modal-list {
  margin: 12px 0 12px 18px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.7;
}
.modal-list li { margin-bottom: 4px; }
.modal-actions {
  display: flex; gap: 12px; justify-content: flex-end;
  margin-top: 20px;
}
.modal code {
  background: var(--surface);
  padding: 1px 6px;
  border-radius: 3px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--accent2);
}
</style>
