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

## [2026-04-30] — go-live preparation

### feat: configurazione produzione AWS
- `backend/config/settings/production.py` — riscritta completamente: sicurezza HTTPS, RDS con SSL, S3, SES, Redis cache, logging strutturato
- `backend/.env.production` — template env per produzione con tutti i valori necessari
- `backend/requirements.txt` — aggiunto `gunicorn==22.0.0` necessario per produzione
- `docker-compose.prod.yml` — nuovo file per deploy su EC2: gunicorn, nginx, certbot SSL, redis persistente, celery
- `nginx/opendrone.conf` — riscritta per produzione: HTTP→HTTPS redirect, SSL TLS 1.2/1.3, proxy frontend Vercel, proxy backend API
- `DEPLOY.md` — guida completa step-by-step: EC2, RDS, S3, SES, SSL Let's Encrypt, Vercel

## [2026-04-30] — documentazione

### docs: aggiunto TODONEXT.md
- `TODONEXT.md` — lista completa delle cose da fare con priorità (alta/media/bassa) e sezione completato

## [2026-04-30] — navbar

### feat: navbar globale aggiornata (App.vue)
- `frontend/src/App.vue` — fix brand POLYDRONE → OPENDRONE
- Aggiunto menu hamburger per mobile (viewport < 768px)
- Menu mobile con overlay, animazione apertura/chiusura
- Link auth (accedi/registrati/logout) visibili anche su mobile
- Chiusura automatica menu al click su un link
