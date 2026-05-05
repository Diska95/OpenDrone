# OpenDrone – Changelog

Tutte le modifiche apportate al progetto sono documentate in questo file.
Formato: `[DATA] TIPO: descrizione` — autore: Claude AI

---

## [2026-05-05] — fix login produzione (HTTPS Vercel ↔ HTTP EC2)

### fix: production.py — SECURE_SSL_REDIRECT/HSTS non più hard-coded a True
- `backend/config/settings/production.py`
  - `SECURE_SSL_REDIRECT` ora letto da env (default `False`)
  - `SECURE_HSTS_*` derivati da `SECURE_HSTS_SECONDS` (default `0` → disattivati)
  - `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` ora opt-in via env
  - **Motivo**: con backend EC2 esposto in HTTP (no SSL su `16.171.15.90`), il vecchio `True` causava un 301 a `https://...` su ogni richiesta proxata da Vercel → login rotto. Da riattivare via env quando ci sarà il dominio + Let's Encrypt.

### fix: client axios — fallback a `/api` (path relativo)
- `frontend/src/api/client.js`
  - `baseURL` di default ora è `/api` invece di `http://localhost:8000/api`
  - Così il rewrite di `vercel.json` viene effettivamente usato anche se `VITE_API_URL` non è impostata su Vercel
  - In dev funziona comunque grazie al proxy `/api` di `vite.config.js`

---

## [2026-05-04] — deploy produzione AWS + Vercel

### fix: requirements.txt — nome pacchetto corretto
- `backend/requirements.txt` — corretto `django-decouple==3.8` → `python-decouple==3.8` (il pacchetto corretto su PyPI)

### fix: nginx — rimossa configurazione SSL per deploy senza dominio
- `nginx/opendrone.conf` — riscritta completamente per funzionare con IP pubblico senza certificati SSL
  - Rimossi tutti i blocchi `listen 443 ssl`
  - Rimossi riferimenti a `tuodominio.it`
  - Aggiunto unico server block `listen 80` con `server_name 16.171.15.90`
  - Proxy verso `backend:8000` per tutte le route

### fix: production.py — disabilitato SECURE_SSL_REDIRECT
- `backend/config/settings/production.py` — `SECURE_SSL_REDIRECT = False` per deploy senza HTTPS diretto
- ⚠️ **Da riabilitare** quando verrà aggiunto il dominio con SSL Let's Encrypt

### fix: backend/.env — ALLOWED_HOSTS aggiornato
- `backend/.env` — aggiunto `ALLOWED_HOSTS=*` per accettare richieste da qualsiasi host (temporaneo, da restringere in produzione con dominio)
- Aggiunto `SECURE_SSL_REDIRECT=False`
- Compilati valori reali: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`

### feat: vercel.json — proxy API verso backend EC2
- `frontend/vercel.json` — **file nuovo**
  - Rewrite `/api/:path*` → `http://16.171.15.90/api/:path*`
  - Risolve il problema Mixed Content (Vercel HTTPS → EC2 HTTP)
  - Il frontend usa URL relativi `/api/...` invece dell'IP diretto

### infra: risorse AWS create
- **EC2**: `t3.micro` Ubuntu 24.04 LTS, IP pubblico `16.171.15.90`, Security Group con porte 22/80/443
- **RDS**: PostgreSQL 16, istanza `opendrone`, utente `opendrone_user`, endpoint `opendrone.c9iiqqiiskta.eu-north-1.rds.amazonaws.com`
- **S3**: bucket `opendrone-files`, regione `eu-south-1`
- **IAM**: utente `opendrone-s3-user` con policy `AmazonS3FullAccess`
- Connessione EC2↔RDS configurata tramite Security Group automatico AWS

### infra: stack Docker avviato su EC2
- Servizi attivi: `backend` (gunicorn), `celery`, `celery-beat`, `redis`, `nginx`, `certbot`
- Migrazioni applicate, static files copiati su S3
- Frontend deployato su Vercel: `open-drone-virid.vercel.app`

---

## [2026-04-30] — ruoli utente & submit progetto

### feat: dashboard differenziata per ruolo (customer vs designer)
- `frontend/src/views/dashboard/Dashboard.vue`
  - **Customer**: sezione di benvenuto con CTA al catalogo + banner 🔒 "Caricamento progetti non disponibile" con link alla registrazione come Designer
  - **Customer**: le voci "I miei progetti" e "Carica nuovo progetto" sono rimosse dalle azioni rapide
  - **Designer**: banner gradient "Hai un progetto da condividere?" con pulsante diretto a `/projects/submit`
  - **Designer**: azioni rapide includono "I miei progetti" e "Carica nuovo progetto"
  - Print node e Assembly center: invariati

### feat: nuova view SubmitProject.vue — wizard 3-step
- `frontend/src/views/marketplace/SubmitProject.vue` — **file nuovo**
  - **Step 1 – Dati base**: titolo, descrizione breve/completa, categoria, difficoltà, peso, autonomia, payload, raggio, categoria EASA, licenza, use cases (tag input)
  - **Step 2 – BOM**: lista componenti dinamica (aggiungi/rimuovi righe), calcolo totale live
  - **Step 3 – File & Invio**: upload STL/STEP, PDF assemblaggio, immagini; note per l'admin; info stato "in validazione"
  - **Step 4 – Success**: schermata di conferma con link a "I miei progetti"
  - Validazione step 1 prima di avanzare (campi obbligatori)
  - Flusso reale: `createProject` → `uploadFile` (x3) → `publishProject`
  - Box requisiti sempre visibile (EASA, formato file, peso max)

### feat: pulsante "Carica progetto" in MyProjects
- `frontend/src/views/marketplace/MyProjects.vue`
  - Header: link cambiato da `/projects/new` a `/projects/submit`
  - Aggiunto banner gradient con CTA a `/projects/submit`
  - Aggiunto stile `.submit-cta` e `.submit-cta-text`

### feat: nuova route /projects/submit
- `frontend/src/router/index.js`
  - Aggiunta `{ path: '/projects/submit', component: SubmitProject, meta: { requiresDesigner: true } }`
  - Protetta da guard `requiresDesigner`: redirect a `/dashboard` per customer e non autenticati

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

## [2026-04-30] — sicurezza

### feat: aggiunto .gitignore
- `.gitignore` — creato da zero: esclude .env, .env.production, staticfiles, media, node_modules, __pycache__, .DS_Store, certificati SSL, editor files
- Verificato che backend/.env contenga solo valori placeholder, nessun segreto reale
