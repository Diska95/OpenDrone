<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-top">
        <div class="page-label">// nuovo account</div>
        <div class="auth-title">Crea il tuo account</div>
        <div class="auth-sub">Scegli come vuoi usare OpenDrone</div>
      </div>
      <div class="auth-body">
        <div v-if="error" class="alert danger">{{ error }}</div>

        <div class="field">
          <label>Tipo di account</label>
          <div class="role-grid">
            <button v-for="r in roles" :key="r.value"
              type="button"
              class="role-opt"
              :class="{ sel: form.role === r.value }"
              @click="form.role = r.value">
              <div class="ri">{{ r.icon }}</div>
              <div class="rn">{{ r.name }}</div>
              <div class="rd">{{ r.desc }}</div>
            </button>
          </div>
        </div>

        <div class="field-row">
          <div class="field">
            <label>Nome</label>
            <input class="input" v-model="form.first_name" placeholder="Mario" />
          </div>
          <div class="field">
            <label>Cognome</label>
            <input class="input" v-model="form.last_name" placeholder="Rossi" />
          </div>
        </div>

        <div class="field">
          <label>Email</label>
          <input class="input" type="email" v-model="form.email" placeholder="tu@email.it" />
        </div>

        <div class="field">
          <label>Password</label>
          <div class="field-wrap">
            <input class="input" :type="showPw ? 'text' : 'password'" v-model="form.password" placeholder="min. 8 caratteri" style="padding-right:40px" />
            <button class="eye" type="button" @click="showPw = !showPw">{{ showPw ? '🙈' : '👁️' }}</button>
          </div>
          <div class="sbar">
            <div class="sseg" :style="{ background: strengthScore >= 1 ? strengthColor : 'var(--border)' }"></div>
            <div class="sseg" :style="{ background: strengthScore >= 2 ? strengthColor : 'var(--border)' }"></div>
            <div class="sseg" :style="{ background: strengthScore >= 3 ? strengthColor : 'var(--border)' }"></div>
            <div class="sseg" :style="{ background: strengthScore >= 4 ? strengthColor : 'var(--border)' }"></div>
          </div>
          <div class="slbl" :style="{ color: form.password ? strengthColor : 'var(--muted)' }">
            {{ form.password ? strengthLabel : 'Inserisci una password' }}
          </div>
        </div>

        <div class="field">
          <label>Conferma password</label>
          <input class="input" :type="showPw ? 'text' : 'password'" v-model="form.password2" placeholder="ripeti password" />
        </div>

        <button class="btn-full primary" :disabled="loading" @click="handleRegister">
          {{ loading ? 'Creazione...' : 'Crea account →' }}
        </button>

        <div class="auth-footer">
          Hai già un account?
          <router-link to="/login">Accedi</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const showPw = ref(false)
const error = ref('')
const loading = ref(false)

const roles = [
  { value: 'customer', icon: '↓', name: 'Cliente', desc: 'Acquista droni' },
  { value: 'designer', icon: '✎', name: 'Designer', desc: 'Pubblica progetti' },
  { value: 'print_node', icon: '⬢', name: 'Nodo stampa', desc: 'Stampi pezzi' },
  { value: 'assembly_center', icon: '⚙', name: 'Assemblaggio', desc: 'Monti droni' },
]

const form = ref({
  first_name: '', last_name: '', email: '',
  password: '', password2: '',
  role: 'customer',
})

const strengthScore = computed(() => {
  const p = form.value.password
  let s = 0
  if (p.length >= 8) s++
  if (/[A-Z]/.test(p)) s++
  if (/[0-9]/.test(p)) s++
  if (/[^a-zA-Z0-9]/.test(p)) s++
  return s
})
const strengthColor = computed(() => {
  return ['', '#ff4f4f', '#ff9060', '#ffcc44', '#5dff9f'][strengthScore.value] || 'var(--muted)'
})
const strengthLabel = computed(() => {
  return ['', 'Debole', 'Discreta', 'Buona', 'Ottima'][strengthScore.value] || ''
})

async function handleRegister() {
  if (!form.value.email || !form.value.password) {
    error.value = 'Email e password sono obbligatorie'
    return
  }
  if (form.value.password !== form.value.password2) {
    error.value = 'Le password non coincidono'
    return
  }
  if (form.value.password.length < 8) {
    error.value = 'Password troppo corta (min. 8 caratteri)'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const user = await auth.register(form.value)
    toast.show(`✓ Benvenuto ${user.first_name || user.email.split('@')[0]}`)
    router.push('/dashboard')
  } catch (e) {
    const errors = e.response?.data
    if (errors) {
      error.value = Object.values(errors).flat().join(' ')
    } else {
      error.value = 'Errore durante la registrazione.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 20px 60px;
  flex: 1;
}
.auth-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  width: 100%;
  max-width: 460px;
}
.auth-top { padding: 28px 28px 0; }
.auth-body { padding: 22px 28px 28px; display: flex; flex-direction: column; gap: 14px; }
.auth-title { font-size: 22px; font-weight: 800; letter-spacing: -.5px; margin-top: 4px; }
.auth-sub { font-size: 13px; color: var(--muted); line-height: 1.5; margin-top: 4px; margin-bottom: 8px; }

.role-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.role-opt {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 10px;
  cursor: pointer;
  text-align: center;
  transition: all .15s;
  background: var(--surface);
  color: var(--text);
  font-family: var(--font);
}
.role-opt:hover { border-color: var(--muted); }
.role-opt.sel { border-color: var(--accent); background: rgba(93,255,159,.06); }
.role-opt .ri { font-size: 22px; margin-bottom: 4px; line-height: 1; }
.role-opt .rn { font-size: 12px; font-weight: 700; }
.role-opt.sel .rn { color: var(--accent); }
.role-opt .rd { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 2px; }

.field-wrap { position: relative; }
.eye { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--muted); cursor: pointer; font-size: 13px; }

.sbar { display: flex; gap: 3px; height: 3px; margin-top: 6px; }
.sseg { flex: 1; background: var(--border); border-radius: 2px; transition: background .3s; }
.slbl { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 4px; }

.auth-footer { font-family: var(--mono); font-size: 12px; color: var(--muted); text-align: center; margin-top: 4px; }
.auth-footer a { color: var(--accent); cursor: pointer; }

.field { margin-bottom: 0; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
</style>
