# Stato sessione audit sicurezza + GDPR

**Ultima sessione:** 2026-05-06 (parte 2: aggiunto branch `gdpr-compliance-rights`)
**Status:** Pausa per gestione budget token. Restano 2 task pending (#5 e #7).

---

## ✅ Cosa è stato fatto (su `main`, già committato)

### Documenti prodotti
- `opendrone/docs/security/SECURITY_AUDIT.md` — 5 critici / 11 alti / 11 medi / 8 bassi, ognuno con file:linea + fix proposto + branch consigliato + stima
- `opendrone/docs/legal/GDPR_GAP_ANALYSIS.md` — gap completo + risk score + roadmap
- `opendrone/docs/security/TODO_USER.md` — cose che DEVE fare l'utente in autonomia (società, dominio, validazione legale, DPA, SES, ecc.)
- `opendrone/docs/legal/` — 9 bozze legali in italiano, tutte con disclaimer "validare con legale" e placeholder `[DENOMINAZIONE SOCIETÀ]` / `[P.IVA]` / `[SEDE_LEGALE]` / `[EMAIL_PRIVACY]` / `[PEC]` / `[NOME_LEGALE_RAPPRESENTANTE]`:
  - `privacy_policy.md`
  - `cookie_policy.md`
  - `informativa_registrazione.md`
  - `termini_servizio.md`
  - `registro_trattamenti.md` (ex art. 30, 10 trattamenti)
  - `sub_responsabili.md` (lista DPA)
  - `data_retention.md`
  - `dpia_minima.md`
  - `procedura_data_breach.md`

### 7 commit su `main` (pronti per deploy)
```
0561810 docs(legal): bozze GDPR-compliant in italiano + TODO operativo
df23b6e fix(security): security headers HTTP (Django + nginx) + brand title
303f4e1 fix(security): nasconde internal_notes dal OrderSerializer pubblico
8aa3fd7 fix(security): rate limit auth + logout strict + revoke refresh on password change
7cd7ecc fix(security): stripe webhook firma obbligatoria, subscribe stub disabilitato
0a57295 docs: aggiunge SECURITY_AUDIT.md e GDPR_GAP_ANALYSIS.md
d495413 chore(security): untrack .env.production, conserva come .example
```

### Cosa cambia in produzione dopo il deploy di questi 7 commit
- Webhook Stripe **rifiuta payload non firmati** (richiede `STRIPE_WEBHOOK_SECRET` configurato)
- Endpoint `POST /api/payments/subscriptions/subscribe/` ora ritorna **503** (era stub che attivava sub gratis)
- Login: max **5 tentativi/min/IP**, register **3/min**, google_auth **10/min**
- Logout: richiede `refresh` nel body (400 se mancante)
- Cambio password: **disconnette gli altri device** dell'utente entro 60 min (current device riceve nuovi token)
- `internal_notes` degli ordini **non più visibile** ai customer
- HTTP security headers attivi (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`)
- nginx `server_name` catch-all (`_`) invece di IP hardcoded obsoleto
- `.env.production` non più tracciato (rinominato in `.env.production.example`)
- HTML title corretto: "OpenDrone" (era "PolyDrone")

### Comando di deploy per l'utente
```bash
ssh -i "C:\Users\lsacchetti\CHIAVE PEM OPENDRONE\Opendrone.pem" ubuntu@16.170.111.228
cd /home/ubuntu/OpenDrone
git pull
docker compose -f opendrone/docker-compose.prod.yml up -d --build backend
docker compose -f opendrone/docker-compose.prod.yml restart nginx
docker compose -f opendrone/docker-compose.prod.yml logs -f backend --tail=50
```

**Smoke test post-deploy** (5 minuti):
1. Vai su `https://open-drone-virid.vercel.app/login`
2. Log in con email+password → deve funzionare
3. Log in con Google → deve funzionare
4. Apri DevTools, fai 6 tentativi di login con password sbagliata → al 6° devi vedere `429 Too Many Requests`
5. Crea un account nuovo → deve funzionare
6. Verifica che `<title>OpenDrone — Marketplace open hardware</title>` (DevTools → Elements)

**ATTENZIONE durante git pull**: il file `nginx/opendrone.conf` è stato modificato in repo. Sull'EC2 c'è una versione locale divergente (`server_name` con dominio o IP custom). Se git segnala conflitto, **mantieni la versione live dell'EC2** (`git checkout --ours opendrone/nginx/opendrone.conf` dopo merge), il file in repo è solo template.

---

## ⏳ Cosa rimane da fare

> ✅ **Task #8 completato** nella parte 2 della sessione: branch locale `gdpr-compliance-rights` creato con 1 commit (`d494c44`). Vedi sotto §"Branch pending da mergiare".

### Task #5 — Branch `security-audit` (fix invasivi)
**Stima:** ~45-60 min lavoro modello.
**Niente migration DB.**

Da implementare:
- **C4** Refactor JWT token in HttpOnly+Secure+SameSite cookie (rimozione `localStorage`)
- **A3** Split `UserSerializer` in `UserPublicSerializer` (id, name, avatar) e `UserPrivateSerializer` (full); usare public ovunque tranne `/me/`. Adattare `DroneProjectDetailSerializer` per non leakare `total_royalties_earned`, `latitude`, `longitude`, `total_revenue`
- **A5** Email verification flow (`signing.dumps` token + endpoint verify + blocco login se non verificato)
- **A6** Password reset flow (request + confirm endpoints + email)
- **A11** File upload validation (MIME whitelist, size, scan extension)
- **M5** `ShippingAddressSerializer` con schema (street, city, postal_code, country, lat, lon validati)

**Cosa cambia per l'utente**: per lo più invisibile. Visibile: link "Hai dimenticato la password?" nel login + email verifica alla registrazione.

### Task #7 — Branch `gdpr-compliance-banner` (cookie banner + consensi)
**Stima:** ~60-75 min.
**Richiede 1 migration DB** (modelli `UserConsent` + `CookieConsent`).

Da implementare:
- Modello `UserConsent(user, consent_type, version, accepted, accepted_at, ip, user_agent)` con migration
- Modello `CookieConsent(session_key/user, choices_json, accepted_at)` con migration
- Endpoint `POST /api/auth/consent/` per registrare consensi
- Componente Vue `<CookieBanner />` (3 livelli: Necessari/Funzionali/Tutti) con persistenza in cookie `od_consent_v1`
- Componente Vue `<LegalFooter />` con link a Privacy/Cookie/Termini
- Page Vue `/privacy`, `/cookie`, `/termini` che rendono i markdown delle bozze (libreria es. `marked`)
- Checkbox "Accetto Privacy + Termini" obbligatorio in `Register.vue`
- Lazy-load Google Identity Services solo dopo consenso "funzionale" (refactor `useGoogleSignIn.js`)
- Self-host font (scaricare WOFF2 di Inter, Syne, DM Mono in `public/fonts/`, sostituire `<link>` di Google Fonts)

**Cosa cambia per l'utente**: MOLTO visibile. Banner all'apertura, footer, 3 nuove pagine, checkbox in registrazione.

### Task #8 ✅ COMPLETATO — Branch locale `gdpr-compliance-rights`

Branch già creato e committato (1 commit, `d494c44`). **Nessuna migration DB**: usa `is_active=False` come flag soft-delete + pseudonimizzazione in-place.

Cosa contiene il branch:
- `apps/users/services.py` (nuovo): `export_user_data(user)` + `anonymize_account(user)`
- `apps/users/views.py`: `data_export_view` (GET `/api/auth/me/data-export/`) + `delete_account_view` (POST `/api/auth/me/delete/`)
- `apps/users/serializers.py`: `DeleteAccountSerializer` con validazione `confirmation == "ELIMINA"`
- `apps/users/urls.py`: 2 nuove rotte
- `frontend/src/api/auth.js`: `exportMyData()` + `deleteAccount({password, confirmation})`
- `frontend/src/views/profile/Profile.vue`: nuova sezione "Privacy e dati personali" con bottone download JSON + modal conferma cancellazione (doppio check: password attuale + digitare "ELIMINA")

Da fare per metterlo in prod (azione utente):
```bash
git checkout main
git merge gdpr-compliance-rights
# nessun migrate da lanciare (zero migration DB)
git push (quando vuoi)
# poi deploy come per main
```

**Cosa cambia per l'utente finale dopo il merge:**
- Pagina `/profile` ha nuova sezione "Privacy e dati personali"
- Click su "Scarica i miei dati" → download di un file JSON con account, profili, ordini, recensioni, royalty, abbonamenti, ultime 200 notifiche
- Click su "Cancella il mio account" → modal con doppia conferma (password + "ELIMINA"). Esegue: blacklist refresh tokens, hard-delete avatar S3, hard-delete profili business, blank recensioni (per integrità rating), pseudonimizza User in-place. Ordini e royalty restano collegati per obblighi contabili 10 anni.

---

## 📌 Decisioni prese durante la sessione

| Decisione | Quando | Motivazione |
|-----------|--------|-------------|
| Titolare = società da definire (placeholder `[DENOMINAZIONE SOCIETÀ]`) | Q5 allineamento iniziale | L'utente ha detto "sarà una società da identificare" |
| Niente DPO, niente legale (oggi) | Q5 | Nessun cliente reale, sotto soglia obbligatoria |
| Cookie banner self-hosted (no Iubenda/Cookiebot) | Conferma utente prima del go | Zero costi, zero ulteriore sub-responsabile |
| Fix safe su `main`, invasivi su branch | Q4 allineamento | Utente vuole evitare downtime in prod |
| `subscribe()` → 503 invece di rimozione | Conferma utente prima del go | Evita rotture silenti se frontend la chiama |
| `.env.production` rinominato in `.env.production.example` | Discovery | Conserva il template senza tracciare segreti |
| Nessun cliente reale ancora → mitigazione retroattiva minima | Q5 | Si può rifare la cancellazione massiccia se serve, ma niente backfill consensi necessario |

---

## 🚦 Come riprendere la prossima sessione

1. **Apri Claude Code** in `C:\users\lsacchetti\OpenDrone`
2. Dimmi qualcosa tipo: *"riprendiamo audit sicurezza, leggi `opendrone/docs/security/SESSION_STATE.md` e parti dal task #X"* (sostituisci X con il task che vuoi)
3. Io leggerò questo file + la mia memoria persistente e ripartirò dal punto giusto.

**Ordine consigliato (per priorità GDPR):**
1. Prima: **deploy dei 7 commit attuali** sull'EC2 + smoke test (è azione tua, fattibile in 1-2h)
2. Poi: **task #7 (cookie banner)** — è il più visibile e il più bloccante per go-live commerciale
3. Poi: **task #8 (export/delete account)** — completa i diritti GDPR
4. Infine: **task #5 (security invasivi)** — importante ma non bloccante quanto i 2 GDPR

**Se preferisci ordine "security first":**
1. Deploy 7 commit
2. task #5 (branch security-audit)
3. task #7
4. task #8

---

## 🔗 File chiave da rileggere se si riprende dopo molto tempo

- `opendrone/docs/security/SECURITY_AUDIT.md` — quadro completo problemi security
- `opendrone/docs/legal/GDPR_GAP_ANALYSIS.md` — quadro completo gap GDPR
- `opendrone/docs/security/TODO_USER.md` — checklist cose da fare in autonomia (società, dominio, ecc.)
- Questo file (`SESSION_STATE.md`) — riassunto operativo per ripartire

---

## 📊 Cose che NON è stato necessario toccare in questa sessione

- Modello DB esistente (nessuna migration creata su main)
- Frontend Vue (eccetto title HTML)
- `package.json` / `requirements.txt` (zero nuove dipendenze)
- Configurazione Vercel (zero modifiche a `vercel.json`)
- Configurazione AWS console (zero accesso a console)
- Repository GitHub (zero push, le modifiche sono solo locali → l'utente farà push quando deciderà di deployare)
