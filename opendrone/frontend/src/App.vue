<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="brand">POLY<span>DRONE</span></router-link>
      <div class="nav-center">
        <!-- ADMIN MODE: nav dedicata operatore di piattaforma -->
        <template v-if="auth.isAdmin">
          <router-link to="/admin" class="nav-link admin-link">★ Dashboard</router-link>
          <router-link to="/admin/projects" class="nav-link admin-link">Progetti</router-link>
          <router-link to="/admin/users" class="nav-link admin-link">Utenti</router-link>
          <router-link to="/admin/orders" class="nav-link admin-link">Ordini</router-link>
          <router-link to="/projects" class="nav-link" style="opacity: .6">Catalogo (preview)</router-link>
        </template>
        <!-- USER MODE: designer / customer / nodo -->
        <template v-else>
          <router-link to="/projects" class="nav-link">Catalogo</router-link>
          <router-link v-if="auth.isDesigner" to="/my-projects" class="nav-link">I miei progetti</router-link>
          <router-link v-if="auth.isDesigner" to="/projects/new" class="nav-link">Carica progetto</router-link>
          <router-link v-if="auth.isAuthenticated" to="/orders" class="nav-link">Ordini</router-link>
          <router-link v-if="auth.isAuthenticated" to="/dashboard" class="nav-link">Dashboard</router-link>
        </template>
      </div>
      <div class="nav-right">
        <template v-if="auth.isAuthenticated">
          <span class="role-badge" :class="primaryRoleClass">{{ primaryRole }}</span>
          <router-link to="/profile" class="btn-sm btn-ghost">{{ auth.user?.first_name || auth.user?.email?.split('@')[0] }}</router-link>
          <button class="btn-sm btn-danger" @click="handleLogout">Esci</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn-sm btn-ghost">Accedi</router-link>
          <router-link to="/register" class="btn-sm btn-accent">Registrati</router-link>
        </template>
      </div>
    </nav>

    <main class="main-content">
      <router-view :key="$route.fullPath" />
    </main>

    <div class="toast" :class="{ show: toast.visible }">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const primaryRole = computed(() => {
  if (!auth.user?.roles?.length) return 'user'
  const order = ['admin', 'designer', 'print_node', 'assembly_center', 'customer']
  for (const r of order) if (auth.user.roles.includes(r)) return r
  return auth.user.roles[0]
})
const primaryRoleClass = computed(() => {
  const r = primaryRole.value
  if (r === 'admin') return 'admin'
  if (r === 'designer' || r === 'print_node' || r === 'assembly_center') return 'creator'
  return 'user'
})

async function handleLogout() {
  await auth.logout()
  toast.show('Disconnesso')
  router.push('/')
}
</script>

<style>
:root {
  --bg: #0a0a0f;
  --surface: #111118;
  --card: #16161f;
  --border: #2a2a38;
  --accent: #5dff9f;
  --accent2: #ff6b35;
  --text: #eeeef5;
  --muted: #7a7a90;
  --danger: #ff4f4f;
  --warning: #ffcc44;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-display: 'Syne', 'Inter', sans-serif;
  --mono: 'DM Mono', ui-monospace, Menlo, monospace;
  --radius: 10px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
*::before, *::after { box-sizing: border-box; }

html, body, #app { min-height: 100vh; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  letter-spacing: 0;
}

h1, h2, h3, h4, h5 {
  font-family: var(--font-display);
  letter-spacing: -.3px;
  line-height: 1.2;
}
h1 { line-height: 1.15; }

p { line-height: 1.6; }
.muted, .sub { line-height: 1.55; }

#app { display: flex; flex-direction: column; min-height: 100vh; }

a { color: inherit; text-decoration: none; }
input, button, select, textarea { font-family: var(--font); }

/* ── NAV ── */
.navbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  position: sticky;
  top: 0;
  z-index: 200;
}
.brand {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -.3px;
  margin-right: 12px;
}
.brand span { color: var(--accent); }

.nav-center { display: flex; gap: 4px; align-items: center; }
.nav-link {
  background: none;
  border: none;
  color: var(--muted);
  font-family: var(--font);
  font-size: 13px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 6px;
  transition: color .15s;
}
.nav-link:hover { color: var(--text); }
.nav-link.router-link-active { color: var(--accent); }
.nav-link.admin-link { color: var(--accent2); }
.nav-link.admin-link:hover { color: #ff9060; }

.nav-right { margin-left: auto; display: flex; gap: 8px; align-items: center; }

.btn-sm {
  padding: 6px 14px;
  border-radius: 7px;
  font-family: var(--font);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all .15s;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-ghost { background: none; border: 1px solid var(--border); color: var(--muted); }
.btn-ghost:hover { border-color: var(--accent); color: var(--accent); }
.btn-accent { background: var(--accent); color: #060f0a; }
.btn-accent:hover { opacity: .85; }
.btn-danger { background: none; border: 1px solid var(--border); color: var(--muted); }
.btn-danger:hover { border-color: var(--danger); color: var(--danger); }

.role-badge {
  font-family: var(--mono);
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid;
  text-transform: lowercase;
}
.role-badge.user { color: var(--muted); border-color: var(--border); }
.role-badge.creator { color: var(--accent); border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.role-badge.admin { color: var(--accent2); border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }

/* ── LAYOUT ── */
.main-content { flex: 1; display: flex; flex-direction: column; }
.wrap { max-width: 900px; margin: 0 auto; padding: 32px 24px 60px; width: 100%; }
.wrap.narrow { max-width: 480px; }
.wrap.wide { max-width: 1100px; }

.page-label {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.page-title { font-family: var(--font-display); font-size: 28px; font-weight: 800; letter-spacing: -.5px; margin-bottom: 8px; line-height: 1.2; }
.page-sub { font-size: 14px; color: var(--muted); margin-bottom: 28px; line-height: 1.6; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}

/* ── BUTTONS ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 9px;
  font-family: var(--font);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all .15s;
  text-decoration: none;
}
.btn.primary { background: var(--accent); color: #060f0a; }
.btn.primary:hover { opacity: .88; }
.btn.outline { background: none; border: 1px solid var(--border); color: var(--muted); }
.btn.outline:hover { border-color: var(--muted); color: var(--text); }
.btn.danger { background: none; border: 1px solid rgba(255,79,79,.4); color: var(--danger); }
.btn-full { width: 100%; padding: 13px; border-radius: 9px; font-family: var(--font); font-size: 14px; font-weight: 800; cursor: pointer; border: none; transition: all .15s; }
.btn-full.primary { background: var(--accent); color: #060f0a; }
.btn-full.primary:hover { opacity: .88; }
.btn-full.primary:disabled { opacity: .4; cursor: not-allowed; }
.btn-full.outline { background: none; border: 1px solid var(--border); color: var(--muted); }
.btn-full.outline:hover { border-color: var(--muted); color: var(--text); }

/* ── FORM ── */
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.field label, .form-label {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--muted);
}
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.input, .select, .textarea {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 14px;
  border-radius: 8px;
  font-family: var(--font);
  font-size: 13px;
  outline: none;
  transition: border-color .2s;
}
.input:focus, .select:focus, .textarea:focus { border-color: var(--accent); }
.input::placeholder, .textarea::placeholder { color: var(--muted); }
.input.err { border-color: var(--danger); }
.select { appearance: none; cursor: pointer; padding-right: 36px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237a7a90' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
}
.select option { background: var(--card); }
.textarea { resize: vertical; min-height: 80px; line-height: 1.6; }

/* ── BADGES ── */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  text-transform: lowercase;
  border: 1px solid;
}
.badge-success { color: var(--accent); border-color: rgba(93,255,159,.3); background: rgba(93,255,159,.06); }
.badge-warning { color: #ff9060; border-color: rgba(255,107,53,.3); background: rgba(255,107,53,.06); }
.badge-danger { color: #ff8080; border-color: rgba(255,79,79,.3); background: rgba(255,79,79,.06); }
.badge-info { color: var(--muted); border-color: var(--border); }

.alert {
  border-radius: 8px;
  padding: 11px 14px;
  font-family: var(--mono);
  font-size: 12px;
  margin-bottom: 12px;
}
.alert.danger { background: rgba(255,79,79,.08); border: 1px solid rgba(255,79,79,.25); color: #ff8080; }
.alert.info { background: rgba(93,255,159,.06); border: 1px solid rgba(93,255,159,.2); color: var(--accent); }
.alert.warn { background: rgba(255,107,53,.08); border: 1px solid rgba(255,107,53,.25); color: #ff9060; }

/* ── CARD ── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 12px;
}

/* ── TOAST ── */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 999;
  background: var(--card);
  border: 1px solid var(--accent);
  color: var(--accent);
  padding: 10px 18px;
  border-radius: 8px;
  font-family: var(--mono);
  font-size: 12px;
  transform: translateY(60px);
  opacity: 0;
  transition: all .3s;
  pointer-events: none;
  max-width: 380px;
}
.toast.show { transform: translateY(0); opacity: 1; pointer-events: auto; }
</style>
