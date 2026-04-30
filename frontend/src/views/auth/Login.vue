<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-top">
        <div class="page-label">// accedi</div>
        <div class="auth-title">Bentornato</div>
        <div class="auth-sub">Accedi al tuo account PolyDrone</div>
      </div>
      <div class="auth-body">
        <div v-if="error" class="alert danger">{{ error }}</div>

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
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const route = useRoute()
const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)
const showPw = ref(false)

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
