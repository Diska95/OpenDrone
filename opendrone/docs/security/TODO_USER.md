# TODO — Cose che DEVI fare tu (non posso farle io)

> Lista ordinata per priorità di tutto ciò che richiede:
> - Decisioni di business o legali
> - Acquisti (dominio, abbonamenti)
> - Login esterni (AWS console, Google Cloud, Stripe dashboard)
> - Operazioni manuali su EC2 (deploy, restart, ecc.)

**Compilato:** 2026-05-06

---

## 🔴 P0 — Bloccanti per il go-live commerciale

### 1. Costituire / identificare la società Titolare
**Perché:** senza una società formalmente identificata non puoi pubblicare la Privacy Policy né essere GDPR-compliant. Tutti i documenti in `docs/legal/` hanno placeholder `[DENOMINAZIONE SOCIETÀ]`, `[P.IVA]`, `[SEDE_LEGALE]`, `[PEC]`, `[NOME_LEGALE_RAPPRESENTANTE]`.

**Cosa fare:**
- Decidere forma giuridica (SRLS, SRL, SPA).
- Aprire P.IVA e PEC.
- Eleggere sede legale.

**Stima:** 2-4 settimane via commercialista.

---

### 2. Acquistare un dominio e attivare HTTPS
**Perché:** il backend EC2 è in HTTP plain → token + email/password viaggiano in chiaro tra Vercel ed EC2 (audit C3). Senza HTTPS NON è GDPR-compliant per dati professionali.

**Cosa fare:**
1. Comprare dominio (es. su Namecheap, OVH, Aruba) — costo ~10-30 €/anno.
2. Configurare DNS:
   - Record A `api.tuodominio.it` → `16.170.111.228` (Elastic IP attuale)
   - Record A `tuodominio.it` → IP Vercel (segui la guida Vercel "Add domain")
3. Sull'EC2, generare cert Let's Encrypt:
   ```bash
   ssh -i Opendrone.pem ubuntu@16.170.111.228
   cd /home/ubuntu/OpenDrone/opendrone
   docker compose -f docker-compose.prod.yml run --rm certbot certonly \
     --webroot -w /var/www/certbot \
     -d api.tuodominio.it \
     --email [TUA_EMAIL] --agree-tos --non-interactive
   ```
4. Aggiornare `nginx/opendrone.conf` con blocco `listen 443 ssl` + redirect 80→443. Esempio già nel docker-compose con certbot attivo.
5. Aggiornare `vercel.json`:
   ```json
   {"source": "/api/(.*)", "destination": "https://api.tuodominio.it/api/$1"}
   ```
6. Aggiornare `.env` sull'EC2:
   ```
   ALLOWED_HOSTS=api.tuodominio.it
   CSRF_TRUSTED_ORIGINS=https://api.tuodominio.it,https://tuodominio.it
   CORS_ORIGINS=https://tuodominio.it,https://www.tuodominio.it
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```
7. Restart backend: `docker compose -f docker-compose.prod.yml restart backend nginx`.
8. Su Google Cloud Console: aggiornare "Authorized JavaScript origins" e "Authorized redirect URIs" con il nuovo dominio.

**Stima:** 2-4 ore (incluso testing).

**Riferimento memoria:** `project_todo_domain_ssl.md`.

---

### 3. Validare TUTTE le bozze legali con un avvocato
**Perché:** ho scritto 9 bozze in `docs/legal/` con disclaimer "**bozza tecnica, non costituisce parere legale**". Non posso (e non devo) sostituire un avvocato. Specialmente i Termini di Servizio e la DPIA hanno implicazioni commerciali che richiedono validazione.

**Documenti da validare:**
- `privacy_policy.md`
- `cookie_policy.md`
- `informativa_registrazione.md`
- `termini_servizio.md` ← **PRIORITÀ MASSIMA** (commissioni, foro, recesso, responsabilità)
- `registro_trattamenti.md`
- `sub_responsabili.md`
- `data_retention.md`
- `dpia_minima.md`
- `procedura_data_breach.md`

**Cosa fare:** mandare i 9 file a un avvocato esperto in privacy/digital + commerciale e-commerce. Costo indicativo: 500-2000 € per validazione completa di marketplace.

**Stima:** 2-4 settimane.

---

### 4. Stipulare/Accettare i DPA con sub-responsabili
**Perché:** art. 28 GDPR. Senza DPA il trattamento dei dati tramite questi fornitori è illegittimo. Vedi `docs/legal/sub_responsabili.md`.

**Cosa fare:**
- **AWS**: Console → Account → AWS Artifact → cerca "AWS GDPR Data Processing Addendum" → Accept Agreement (1 click). Scaricare PDF firmato.
- **Vercel**: https://vercel.com/legal/dpa — se sei su free plan basta il riferimento; se su Pro/Enterprise richiedere copia firmata via email a privacy@vercel.com.
- **Stripe**: https://stripe.com/legal/dpa — accettato implicitamente con i ToS, scaricare PDF e archiviare.
- **Google Cloud / Workspace**: Console → IAM → Compliance → "Cloud Data Processing Addendum" → Accept.

**Stima:** 30 minuti.

**Output:** archiviare i PDF in cartella offline o cloud privato. Aggiornare data DPA in `sub_responsabili.md`.

---

### 5. Configurare AWS SES domain (per email transazionali)
**Perché:** SES in sandbox può inviare solo a indirizzi verificati. Per inviare a customer reali serve uscire dalla sandbox + verificare domain DKIM/SPF.

**Cosa fare:**
1. AWS Console → SES (region `eu-south-1`) → Verified identities → Create identity → Domain → `tuodominio.it`.
2. Pubblicare i record CNAME DKIM e TXT SPF nel DNS.
3. Richiedere uscita dalla sandbox: SES → Account dashboard → Request production access. Compila form (use case, volume stimato, opt-out process). Approvazione AWS in 24-48h.
4. Configurare DMARC (TXT record `_dmarc.tuodominio.it` con `v=DMARC1; p=quarantine; rua=mailto:postmaster@tuodominio.it`).

**Stima:** 1-2 ore + 1-2 giorni attesa AWS.

---

## 🟠 P1 — Importanti (settimana 1-2 post go-live)

### 6. Restringere SSH e bloccare /admin/ Django
**Perché:** audit A2 — l'admin Django è raggiungibile in HTTP plain.

**Cosa fare:**
- Sul Security Group EC2: confermare che SSH (port 22) sia ristretto al tuo IP (cambia se cambi rete).
- Decommentare il blocco `location /admin/` in `nginx/opendrone.conf` con `allow <TUO_IP>; deny all;` E aggiornare il file in repo + push + pull su EC2 + restart nginx.
- (Alternativa) Quando avrai HTTPS, aggiungere 2FA admin con `django-otp` o simile.

**Stima:** 30 minuti.

---

### 7. Configurare backup RDS automatici e testare il restore
**Perché:** AWS RDS ha backup di default ma raramente sono testati. In caso di breach o crash devi sapere che il restore funziona.

**Cosa fare:**
1. AWS Console → RDS → tua DB instance → Maintenance & backups → confermare:
   - Backup retention: 7-30 giorni (raccomandato 14)
   - Backup window: orario notturno
   - Snapshot manuali periodici (mensili) prima di migrazioni
2. **Test restore** (almeno una volta): create snapshot → restore in DB istanza temporanea → connetti e verifica → cancella istanza temporanea.
3. Documentare RPO (Recovery Point Objective) e RTO (Recovery Time Objective).

**Stima:** 2-3 ore (incluso test).

---

### 8. Acquistare/configurare un servizio di error monitoring
**Perché:** oggi gli errori finiscono solo in `docker logs`. Non sai quando il sistema è in degrado finché un utente non te lo dice.

**Cosa fare:** attivare Sentry (free plan: 5k errors/mese), Bugsnag, o Rollbar.
- Aggiungere DSN nel `.env`.
- Wrap Django settings con `sentry_sdk.init(...)`.
- **Importante**: configurare `before_send` per filtrare PII dagli stack trace (no email, no body request).
- Aggiungere come sub-responsabile in `sub_responsabili.md` + Privacy Policy.

**Stima:** 1-2 ore.

---

### 9. Pulire la struttura repo duplicata `opendrone/opendrone/`
**Perché:** audit B8. Cartella duplicata che confonde.

**Cosa fare:**
- Verificare se `opendrone/opendrone/` è usata da qualcosa (probabilmente artefatto di deployment iniziale, vedi memoria).
- Se non usata: `git rm -rf opendrone/opendrone` + commit.

**Stima:** 15 minuti.

---

### 10. Decidere il branding definitivo
**Perché:** notato refuso `<title>PolyDrone</title>` nel HTML (già fixato in commit `df23b6e`). Verifica anche:
- Nome dominio acquistato (vedi #2)
- Logo (`favicon`)
- Brand consistency in email (subject "OpenDrone — ...")

**Stima:** decisione personale.

---

## 🟡 P2 — Importanti ma non bloccanti (primi 90 giorni)

### 11. Pentest esterno
**Perché:** il mio audit è statico (lettura codice). Un pentest dinamico testa veramente l'app contro un attaccante.

**Cosa fare:** ingaggiare una società di sicurezza per 3-5 giorni man (~3000-8000 €). Output: report con vulnerabilità trovate, da riportare nel piano.

---

### 12. Implementare audit log per azioni admin
**Perché:** audit M11. Non sai chi-quando-cosa per le azioni amministrative.

**Cosa fare:** integrare `django-auditlog` o redigere modello custom `AdminAuditLog`. Roadmap.

---

### 13. Implementare retention job Celery beat
**Perché:** `data_retention.md` definisce policy ma i job non esistono. Senza job, i dati restano per sempre (violazione principio minimizzazione).

**Cosa fare:** vedi `data_retention.md` §4 per la spec dei task da implementare.

**Stima:** 1-2 giorni dev.

---

### 14. Considerare un WAF
**Perché:** rate limit lato app non basta contro DDoS distribuito o bot avanzati.

**Opzioni:**
- AWS WAF su un ALB davanti all'EC2 (~5-10 €/mese)
- Cloudflare in front di Vercel + EC2 (free plan ok per inizio) — c'è già la cartella `cloudflared` sull'EC2 quindi potresti averla parzialmente impostata.

---

### 15. Verifica se serve nominare un DPO
**Perché:** non è obbligatorio adesso ma diventa obbligatorio se:
- Tratti dati su larga scala (interpretazione: ~5000+ utenti).
- Tratti categorie particolari (art. 9) sistematicamente.
- Sei autorità pubblica.

**Cosa fare:** soglia di guardia 1000 utenti registrati → consultare avvocato per decidere se nominare DPO interno (lettera incarico) o esterno (~3000-8000 €/anno).

---

## 🟢 P3 — Nice-to-have

### 16. Implementare 2FA per utenti
- Per admin: prioritario.
- Per designer/print_node/assembly_center con saldo Stripe: raccomandato.
- Per customer: opzionale.

**Tool:** `django-otp` + `django-two-factor-auth`.

### 17. Self-host Google Fonts
Vedi audit B1. Eliminerebbe necessità di consenso per font. Faccio fare in task #7 (cookie banner).

### 18. Migliorare UX dell'export dati GDPR (ZIP con HTML + JSON)

**Perché:** oggi l'export dati personali (`/profile` → "Scarica i miei dati") restituisce un singolo file JSON. È **legalmente conforme** (art. 20 GDPR richiede "formato strutturato di uso comune leggibile da dispositivo automatico" → JSON ✓), ma poco user-friendly per clienti non tecnici.

**Pattern industria** (Google Takeout, Meta, Twitter): ZIP contenente:
- `index.html` umano-leggibile in italiano con tabelle: Account, Profili, Ordini effettuati, Recensioni, Royalty, ecc. — ogni sezione con titolo descrittivo invece dei nomi tecnici
- `data.json` con il dump completo (per portabilità tra servizi)
- `README.txt` con spiegazione di cosa c'è dentro

**Cosa fare:** modificare `apps/users/services.py:export_user_data` per restituire un buffer ZIP + adattare `data_export_view` con `Content-Type: application/zip`. Stima: ~30-45 min.

**Quando:** raccomandato quando avrai i primi customer reali non-tecnici. Per utenti tecnici (designer, print_node, assembly_center) il JSON attuale va già bene.

**Riferimento:** sessione audit 2026-05-06, conversazione post-deploy.

---

### 19. Pubblicare un security.txt
Standard RFC 9116. File `https://tuodominio.it/.well-known/security.txt` con email per security disclosure responsabile. Esempio:
```
Contact: mailto:security@tuodominio.it
Expires: 2027-01-01T00:00:00.000Z
Preferred-Languages: it, en
```

---

## Cose che NON devi fare in autonomia (le faccio io quando mi dici "go")

Queste sono tracciate nel mio task list e posso eseguirle quando vuoi:

- ✅ **task #4** (Fix critici/safe su main) — FATTO, 6 commit.
- ✅ **task #6** (Bozze legali) — FATTO, 9 file in `docs/legal/`.
- ⏳ **task #5** (Fix invasivi su branch `security-audit`):
  - C4 token in HttpOnly cookie
  - A3 UserPublicSerializer
  - A5+A6 email verification + password reset
  - A11 file upload validation
  - M1 paginazione
  - M5 shipping_address schema
- ⏳ **task #7** (Cookie banner + consent gate):
  - Modello UserConsent + CookieConsent
  - Componente Vue cookie banner
  - Self-host font
  - Lazy-load GSI post-consenso
  - Page /privacy, /cookie, /termini con MD render + footer
- ⏳ **task #8** (Diritti interessati):
  - Endpoint export dati account
  - Endpoint cancellazione account con anonimizzazione
  - UI in Profile page

Il deploy sull'EC2 dei task #5/#7/#8 (codice nuovo + migrations DB) richiederà la tua autorizzazione esplicita perché coinvolge migrations e UI changes — niente auto-deploy.

---

## Cheat sheet — comandi rapidi per emergenze

| Cosa | Comando |
|------|---------|
| SSH all'EC2 | `ssh -i "C:\Users\lsacchetti\CHIAVE PEM OPENDRONE\Opendrone.pem" ubuntu@16.170.111.228` |
| Restart backend | `docker compose -f docker-compose.prod.yml restart backend` |
| Logs backend | `docker compose -f docker-compose.prod.yml logs -f backend --tail=100` |
| Pull aggiornamenti | `cd /home/ubuntu/OpenDrone && git pull && docker compose -f opendrone/docker-compose.prod.yml up -d --build backend` |
| Snapshot DB ora | AWS Console → RDS → instance → Actions → Take snapshot |
| Bloccare un utente | Django admin → Users → seleziona → Action "Disattiva" |
| Revocare tutti i refresh token | `python manage.py shell -c "from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken; [BlacklistedToken.objects.get_or_create(token=t) for t in OutstandingToken.objects.all()]"` |
| Compromise sospetto: nuke chiavi AWS | AWS Console → IAM → Users → opendrone-s3-user → Security credentials → Make inactive → Delete |
| Compromise sospetto: rotate Stripe key | Stripe dashboard → Developers → API keys → Roll restricted key |
