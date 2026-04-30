# OpenDrone – Changelog

Tutte le modifiche apportate al progetto sono documentate in questo file.
Formato: `[DATA] TIPO: descrizione` — autore: Claude AI

---

## [2026-04-30]

### fix: rename PolyDrone → OpenDrone (frontend)
- `frontend/src/views/auth/Login.vue` → testo "Accedi al tuo account OpenDrone"
- `frontend/src/views/auth/Register.vue` → testo "Scegli come vuoi usare OpenDrone"
- `frontend/src/views/admin/AdminDashboard.vue` → rimossi tutti i riferimenti a PolyDrone
- `frontend/src/views/dashboard/Dashboard.vue` → rimossi tutti i riferimenti a PolyDrone

### audit: sistema auth verificato (nessuna modifica necessaria)
- `backend/apps/users/models.py` — User custom con AbstractBaseUser, ruoli via JSONField, profili per ogni ruolo ✓
- `backend/apps/users/serializers.py` — RegisterSerializer con validazione password, UserSerializer con profili nested ✓
- `backend/apps/users/views.py` — RegisterView, login_view, logout_view, MeView, ChangePasswordView, profili per ruolo, admin endpoints ✓
- `backend/apps/users/urls.py` — tutti gli endpoint auth mappati correttamente ✓
- `backend/config/settings/base.py` — JWT configurato (access 60min, refresh 30gg, blacklist attiva) ✓
- `frontend/src/api/client.js` — Axios con auto-refresh JWT e redirect a /login su 401 ✓
- `frontend/src/stores/auth.js` — Pinia store con login, register, logout, fetchMe ✓
- `frontend/src/api/auth.js` — authApi completo ✓
