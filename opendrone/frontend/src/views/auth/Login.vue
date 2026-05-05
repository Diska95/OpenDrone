<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-top">
        <div class="page-label">// accedi</div>
        <div class="auth-title">Bentornato</div>
        <div class="auth-sub">Accedi al tuo account OpenDrone</div>
      </div>
      <div class="auth-body">
        <div v-if="error" class="alert danger">{{ error }}</div>

        <div v-if="googleClientId" class="google-block">
          <div ref="googleBtnEl" class="google-btn-host"></div>
          <div v-if="googleLoading" class="google-loading">Accesso con Google…</div>
        </div>

        <div v-if="googleClientId" class="divider"><span>oppure con email</span></div>

        <div class="field">
          <label>Email</label>
          <input class="input" type="email" placeholder="tu@email.it" v-model="form.email" />
        </div>
        <div class="field">
          <label>Password</label>
          <div class="field-wrap">
            <input class="input" :type="showPw ? 'text' : 'password'" placeholder="••••••••" v-model="form.password" style="padding-right:40px" />
            <button class="eye" @click="showPw = !showPw" type="button">{{ showPw ? '🙈' : '👁️' }}</button>
          </div>
        </div>

        <button class="btn-full primary" :disabled="loading" @click="handleLogin">
          {{ loading ? 'Accesso...' : 'Accedi →' }}
        </button>

        <div class="auth-footer">
          Non hai un account?
          <router-link to="/register">Registrati</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { loadGoogleScript, getGoogleClientId } from '@/composables/useGoogleSignIn'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const route = useRoute()
const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)
const googleLoading = ref(false)
const showPw = ref(false)
const googleBtnEl = ref(null)
const googleClientId = getGoogleClientId()

async function handleLogin() {
  if (!form.value.email || !form.value.password) {
    error.value = 'Inserisci email e password'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const user = await auth.login(form.value.email, form.value.password)
    toast.show(`✓ Bentornato ${user.first_name || user.email.split('@')[0]}`)
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Credenziali non valide.'
  } finally {
    loading.value = false
  }
}

async function handleGoogleResponse(response) {
  if (!response?.credential) return
  googleLoading.value = true
  error.value = ''
  try {
    const { user } = await auth.loginWithGoogle({ credential: response.credential })
    toast.show(`✓ Bentornato ${user.first_name || user.email.split('@')[0]}`)
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore con Google. Riprova.'
  } finally {
    googleLoading.value = false
  }
}

onMounted(async () => {
  if (!googleClientId) return
  await nextTick()
  try {
    const google = await loadGoogleScript()
    google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleResponse,
      ux_mode: 'popup',
    })
    if (googleBtnEl.value) {
      google.accounts.id.renderButton(googleBtnEl.value, {
        theme: 'filled_black',
        size: 'large',
        type: 'standard',
        text: 'continue_with',
        shape: 'rectangular',
        width: 360,
        logo_alignment: 'left',
      })
    }
  } catch (e) {
    console.error('Google script load failed', e)
  }
})
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  flex: 1;
}
.auth-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  width: 100%;
  max-width: 400px;
}
.auth-top { padding: 28px 28px 0; }
.auth-body { padding: 22px 28px 28px; display: flex; flex-direction: column; gap: 14px; }
.auth-title { font-size: 22px; font-weight: 800; letter-spacing: -.5px; margin-top: 4px; }
.auth-sub { font-size: 13px; color: var(--muted); line-height: 1.5; margin-top: 4px; margin-bottom: 12px; }

.google-block { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.google-btn-host { min-height: 40px; }
.google-loading { font-family: var(--mono); font-size: 11px; color: var(--muted); }

.divider {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 10px; color: var(--muted);
  text-transform: uppercase; letter-spacing: 1px;
  margin: 4px 0;
}
.divider::before, .divider::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

.field-wrap { position: relative; }
.eye {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 13px;
}

.auth-footer {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--muted);
  text-align: center;
  margin-top: 4px;
}
.auth-footer a { color: var(--accent); cursor: pointer; }

.field { margin-bottom: 0; }
</style>
