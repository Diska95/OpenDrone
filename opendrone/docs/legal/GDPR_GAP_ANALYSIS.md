# GDPR GAP ANALYSIS — OpenDrone

**Data:** 2026-05-06
**Stato:** in produzione, **nessun cliente reale** (mitiga rischio retroattivo).
**Titolare del trattamento:** `[DENOMINAZIONE SOCIETÀ DA DEFINIRE]` — sarà una società, da costituire/identificare.
**DPO:** non nominato (al momento non obbligatorio, vedi §6).
**Riferimento parallelo sicurezza:** `docs/security/SECURITY_AUDIT.md`.

> Disclaimer: questa analisi è una review tecnica/organizzativa. Non costituisce parere legale. Tutti i testi prodotti (privacy policy, cookie policy, ecc.) sono **bozze tecniche da far validare a un avvocato/DPO** prima della pubblicazione.

---

## 0. Sommario esecutivo

| Area | Stato attuale | Gap | Priorità |
|------|--------------|-----|----------|
| Informativa privacy | Assente | Mancano informative ex art. 13 | 🔴 Bloccante go-live |
| Consensi | Nessuno raccolto | Mancano checkbox in registrazione, consent log | 🔴 Bloccante |
| Cookie banner | Assente | Cookie tecnici + Google Fonts/GSI senza consenso | 🔴 Bloccante |
| Diritti interessati (art. 15-22) | Non implementati | Mancano endpoint export + cancellazione | 🟠 Alto |
| Registro trattamenti (art. 30) | Non esiste | Documento da redigere | 🟠 Alto |
| Sub-responsabili (art. 28) | Mai formalizzati | Verificare DPA AWS/Vercel/Google/Stripe | 🟠 Alto |
| Trasferimenti extra-UE (cap. V) | Stripe/Google US | Coperti da SCC/Adequacy ma da dichiarare | 🟡 Medio |
| Sicurezza (art. 32) | Lacune (vedi audit sicurezza) | HTTPS, encryption, rate limit, XSS hardening | 🔴 Vedi audit |
| DPIA (art. 35) | Non fatta | Necessaria per geolocalizzazione + scoring designer | 🟡 Medio |
| Data retention | Implicita illimitata | Definire policy per ogni dato | 🟡 Medio |
| Data breach notification | Procedura assente | Documento + responsabili | 🟠 Alto |

**Top 3 azioni bloccanti per go-live commerciale:**
1. Pubblicare privacy policy + cookie banner + checkbox consenso registrazione.
2. Implementare endpoint export + delete account.
3. Costituire/identificare la società titolare e firmare i DPA mancanti con sub-responsabili.

---

## 1. Mappa dei trattamenti

### 1.1 Categorie di interessati
- **Customer**: utenti che acquistano droni assemblati o kit.
- **Designer**: utenti che pubblicano progetti (persone fisiche o universitari).
- **Print node**: titolari di nodi di stampa (persone fisiche con P.IVA o ditte).
- **Assembly center**: titolari di centri assemblaggio (idem).
- **Admin**: personale interno OpenDrone.

### 1.2 Categorie di dati personali trattati

| Categoria | Dato | Dove | Base giuridica | Note |
|-----------|------|------|----------------|------|
| Identificativi | email, first_name, last_name | `users.User` (RDS) | Esecuzione contratto art. 6.1.b | obbligatori per account |
| Identificativi (Google) | email, given_name, family_name verificati Google | `users.User` (RDS) | Consenso (uso login) art. 6.1.a + esecuzione contratto | id_token Google verificato server-side |
| Profilo | bio, avatar | `users.User` (RDS + S3) | Consenso (compilazione profilo) | facoltativi |
| Contatto fiscale (implicito) | indirizzo, città, provincia (PrintNode/Assembly) | `users.PrintNodeProfile/AssemblyCenterProfile` (RDS) | Esecuzione contratto + obbligo legale (fattura) | servono per fatturazione e geolocalizzazione assegnazione ordini |
| Geolocalizzazione | latitude, longitude (PrintNode/Assembly) | `users.PrintNodeProfile/AssemblyCenterProfile` (RDS) | Esecuzione contratto (matching ordini) | precisione 6 decimali = ~10cm |
| Pagamento | stripe_account_id, stripe_customer_id | `users.User` (RDS) + Stripe | Esecuzione contratto + obbligo legale (antiriciclaggio) | dati pagamento veri restano su Stripe |
| Indirizzo spedizione | shipping_address (street, city, lat/lon) | `orders.Order.shipping_address` (RDS, JSONField) | Esecuzione contratto | per ogni ordine |
| Tracking | tracking_number, courier | `orders.Order` (RDS) | Esecuzione contratto | |
| Royalty/Fatturazione | gross_amount, net_amount, paid_at | `payments.RoyaltyLedger` (RDS) | Obbligo legale (contabile) | conservazione 10 anni |
| Recensioni | comment, rating, build_photos | `marketplace.ProjectReview` (RDS + S3 per foto) | Consenso (pubblicazione opt-in) | nome+cognome reviewer esposto pubblicamente — vedi M6 audit |
| File progetto | STL, BOM, immagini, video | S3 `opendrone-files` | Consenso (caricamento opt-in) | possibili dati di terzi se BOM include URL fornitori, foto build con persone |
| Notifiche | message, link | `notifications.Notification` (RDS) | Esecuzione contratto | testi includono nomi prodotti, importi |
| Audit/log | log gunicorn, log nginx | EC2 stdout/file | Legittimo interesse (sicurezza) | NO IP utente di norma loggato (verificare conf nginx in prod) |
| Cookie/storage | access_token, refresh_token in localStorage | Browser | Esecuzione contratto (autenticazione) | tecnico, no consenso necessario |

### 1.3 Categorie particolari (art. 9)
**Nessuna trattata intenzionalmente.** Possibile leak in:
- Foto profilo (`avatar`) e foto build (`ProjectReview.build_photos`) potrebbero contenere persone identificabili.
- Bio testuale potrebbe contenere dati che l'utente sceglie di rivelare (religione, salute, ecc.) — di sua iniziativa.
- File caricati su S3 (STL, BOM) — improbabile ma non impossibile.

→ **Mitigation**: linee guida + ToS che vietano caricamento dati sensibili di terzi senza consenso.

### 1.4 Trasferimenti extra-UE
- **Stripe Inc.** (US) per processing pagamenti → coperto da DPF (Data Privacy Framework) post-Schrems II + SCC.
- **Google LLC** (US) per Google Sign-In + Google Fonts (se non self-hosted) → coperto da DPF.
- **AWS Inc.** se la console root user è gestita da account US — i dati sono in EU (`eu-north-1`, `eu-south-1`) ma il provider è US → DPF + SCC + AWS DPA.

→ Da dichiarare in privacy policy e raccogliere DPA + SCC firmati.

---

## 2. Gap per area

### 2.1 Informativa (art. 13) — 🔴 ASSENTE
**Gap:** non esiste alcuna informativa visibile all'interessato al momento della raccolta dati. Né in registrazione, né in checkout, né nel profilo.

**Cosa serve (per ogni punto di raccolta):**
- Identità + contatti del titolare
- DPO se nominato (no oggi)
- Finalità + base giuridica per ogni trattamento
- Destinatari/categorie di destinatari (sub-responsabili)
- Trasferimenti extra-UE + garanzie
- Periodo di conservazione
- Diritti (15-22) + come esercitarli
- Diritto di proporre reclamo al Garante

**Output prodotto in questa sessione:** `docs/legal/privacy_policy.md` (bozza, vedi §5).

### 2.2 Consensi (art. 7) — 🔴 ASSENTI
**Gap:** nessun consenso raccolto. Il bottone "Crea account" non è preceduto da accettazione informativa. Per Google Sign-In si applica ma comunque mancano accettazioni esplicite.

**Cosa serve:**
- Checkbox **non pre-selezionato** "Ho letto e accetto la [Privacy Policy](link)" obbligatorio in registrazione email + Google.
- Checkbox separato (facoltativo) "Accetto di ricevere comunicazioni di marketing" (per future newsletter, oggi no).
- Persistenza del consenso: tabella `users.UserConsent(user, type, version, accepted_at, ip, user_agent)`.
- Versionamento informativa: ogni modifica → nuovo `version` + invito ad accettare di nuovo al login successivo.

**Da implementare:**
- Modello `UserConsent` (lavoro task #8).
- UI checkbox in `frontend/src/views/auth/Register.vue` (lavoro task #7).
- Endpoint `POST /api/auth/consent/` per registrare versioni accettate.

### 2.3 Cookie banner (e-Privacy) — 🔴 ASSENTE
**Gap:** nessun banner. Il sito carica:
- localStorage con token (tecnico, no consenso).
- Google Fonts da `fonts.gstatic.com` (terza parte → consenso necessario).
- Google Identity Services script (terza parte → caricato lazy ma DNS preconnect comunque).

**Categorizzazione cookie/storage:**
| Item | Tipo | Consenso |
|------|------|----------|
| `access_token`, `refresh_token` (localStorage) | Tecnico | Non necessario |
| Cookie sessione Django (futuro, post HTTPS+HttpOnly) | Tecnico | Non necessario |
| Google Fonts (`gstatic.com`) | Terza parte/profilazione | **NECESSARIO** o self-host |
| Google Sign-In script | Terza parte/funzionale | **NECESSARIO** (il bottone va abilitato solo dopo consenso) |
| Stripe.js (futuro caricamento) | Terza parte/funzionale | Necessario (o limitato a pagina checkout con disclosure) |

**Da implementare (task #7):**
- Banner consent gate con 3 livelli: "Solo necessari" / "Personalizza" / "Accetta tutti".
- Memorizzare scelta in cookie `od_consent_v1` (con `SameSite=Lax`, durata 6 mesi).
- Solo dopo consenso "funzionale" caricare Google Sign-In script.
- Self-host font (B1 audit) → rimuove necessità di consenso per font.
- Tabella DB `consent.CookieConsent` per audit (timestamp, scelte).

### 2.4 Diritti dell'interessato (art. 15-22) — 🟠 NON IMPLEMENTATI
| Diritto | Articolo | Stato attuale | Azione |
|---------|----------|---------------|--------|
| Accesso | 15 | ❌ | Endpoint `GET /api/auth/me/data-export/` ritorna JSON con tutti i dati personali |
| Rettifica | 16 | ⚠️ Parziale (PATCH /me/) | Estendere a profili business |
| Cancellazione (oblio) | 17 | ❌ | Endpoint `DELETE /api/auth/me/` con conferma password + email warning |
| Limitazione | 18 | ❌ | Endpoint `POST /api/auth/me/restrict/` (sospende trattamenti non necessari) |
| Portabilità | 20 | ❌ | Stesso export di art.15 ma in formato standard (JSON o CSV) |
| Opposizione | 21 | ❌ | Per marketing futuro: opt-out via `UserConsent`. Per trattamenti necessari: rispondere case-by-case |
| Decisione automatizzata | 22 | N/A | Nessuna decisione 100% automatizzata oggi (assegnazione print_node è basata su distanza ma non produce effetti legali) |

**Implementazione (task #8):**
- Endpoint export: ritorna JSON con `User`, profili, ordini, royalty, recensioni, file URL S3 (presigned). Hash file per integrità.
- Endpoint delete:
  - **Soft delete** per ordini/royalty (ragioni contabili, art. 6.1.c — obbligo legale conservazione 10 anni).
  - **Hard delete** per profilo, recensioni (anonymizzate: `reviewer = NULL`, `comment` blank), avatar, bio, file caricati che non sono referenziati in ordini consegnati.
  - Email di conferma "Il tuo account è stato cancellato. Ordini storici conservati in forma pseudonimizzata per obbligo contabile."
  - Blacklist refresh token + invalidate session.
- UI: `frontend/src/views/profile/Profile.vue` → sezione "Privacy" con bottoni "Scarica i miei dati" e "Cancella account".

### 2.5 Registro trattamenti (art. 30) — 🟠 ASSENTE
**Obbligatorio per:**
- Aziende con >250 dipendenti, **OPPURE**
- Trattamenti **non occasionali**, **OPPURE**
- Trattamenti che includano **dati particolari** o relativi a **condanne penali**.

OpenDrone tratta dati non occasionalmente → **obbligatorio anche se sotto i 250 dipendenti**.

**Output prodotto:** `docs/legal/registro_trattamenti.md` (bozza ex art. 30 con tabella per ogni trattamento).

### 2.6 Sub-responsabili (art. 28) — 🟠 DA FORMALIZZARE
Sub-responsabili attuali e azioni:

| Fornitore | Trattamento | DPA disponibile | Azione |
|-----------|-------------|-----------------|--------|
| **AWS** (RDS, S3, SES, EC2) | Hosting + storage + email | Sì, in console: Account → AWS Artifact → "AWS GDPR Data Processing Addendum" | Accettare via console (1 click) |
| **Vercel** | Hosting frontend + edge | Sì, https://vercel.com/legal/dpa | Firmare/accettare (Pro plan o richiesta scritta) |
| **Stripe** | Pagamenti + transfer | Sì, https://stripe.com/legal/dpa | Accettato implicitamente con ToS, scaricare PDF per archivio |
| **Google** (OAuth, Fonts) | Login federato | Sì, https://privacy.google.com/businesses/processorterms/ | Accettare via console Google Cloud |
| **Cloudflare** (se cloudflared usato in futuro) | Tunnel/CDN | Sì | Verificare se attivato |

**Output:** `docs/legal/sub_responsabili.md` (lista + link DPA).

### 2.7 Sicurezza (art. 32) — 🔴 LACUNE GRAVI
Vedi `docs/security/SECURITY_AUDIT.md` per dettaglio. Sintesi GDPR-rilevante:
- ❌ Trasporto in chiaro Vercel→EC2 (C3 audit) → violazione `art. 32.1.a` (cifratura in transito).
- ⚠️ Token in localStorage (C4 audit) → violazione potenziale dell'obbligo di adeguatezza misure tecniche.
- ❌ Mancano rate limiting (A1) → enumerazione utenti, brute force.
- ❌ Mancano validazione file upload (A11) → abuse vector.
- ✓ Database in transit cifrato (`sslmode=require`).
- ✓ S3 ACL private.
- ✓ Password hashing PBKDF2 (default Django).

### 2.8 Data retention — 🟡 IMPLICITA ILLIMITATA
**Gap:** nessuna regola di cancellazione automatica. Tutto è conservato finché l'utente non chiede cancellazione.

**Policy proposta (`docs/legal/data_retention.md`):**

| Categoria | Retention | Base | Cancellazione |
|-----------|-----------|------|---------------|
| Account attivo | Indefinita finché attivo | Esecuzione contratto | Cancellazione su richiesta |
| Account inattivo (no login >24 mesi) | 24 mesi → email warning → 6 mesi → soft delete | Legittimo interesse | Job Celery beat mensile |
| Ordini conclusi | 10 anni | Obbligo legale (CC art. 2220) | Pseudonimizzati alla cancellazione account |
| Royalty / fatturazione | 10 anni | Obbligo fiscale | Idem |
| Log accesso (nginx/django) | 12 mesi | Sicurezza/legittimo interesse | Rotazione automatica `logrotate` |
| Token blacklisted (SimpleJWT) | 30 giorni post-rotation | Sicurezza | Cleanup task `flushexpiredtokens` Celery beat settimanale |
| Notifiche lette | 6 mesi | Esecuzione contratto | Job Celery beat |
| Notifiche non lette | 12 mesi | Esecuzione contratto | Job Celery beat |
| Consensi (UserConsent) | Per durata contratto + 5 anni | Obbligo (prova) | Mantieni anche post-cancellazione account |
| Audit log admin | 5 anni | Compliance | Mai cancellati senza autorizzazione |

### 2.9 DPIA — Art. 35 — 🟡 NECESSARIA (limitata)
**Soglia art. 35.3:** DPIA obbligatoria per:
- Profilazione/decisioni automatizzate con effetti legali → **NO** (assegnazione print_node non è decisione legale).
- Categorie particolari su larga scala → **NO**.
- Monitoraggio sistematico zone pubbliche → **NO**.

**Per OpenDrone serve DPIA "leggera"** per:
- Geolocalizzazione precisa (lat/lon a 6 decimali) di nodi di stampa e assembly center → identifica esattamente la sede di lavoro/abitazione (per i piccoli operatori che lavorano da casa).
- Scoring rating designer/print_node → reputazione professionale impattata.

**Output:** `docs/legal/dpia_minima.md` con valutazione + misure di mitigazione.

### 2.10 Notifica violazioni (art. 33-34) — 🟠 PROCEDURA ASSENTE
**Gap:** nessuna procedura interna per:
- Rilevare violazioni (mancano alert, log centralizzati).
- Notificare al Garante entro 72h.
- Comunicare agli interessati se rischio elevato.

**Output:** `docs/legal/procedura_data_breach.md` con:
- Chi rileva (admin/dev), come (alert + revisione log).
- Chi notifica (titolare/società), template comunicazione Garante (https://servizi.gpdp.it/databreach/s/).
- Template comunicazione utenti.
- Chain of custody / log forensics.

---

## 3. Misure tecniche specifiche da implementare (lato app)

| ID | Cosa | Dove | Linked task |
|----|------|------|-------------|
| GT1 | Modello `UserConsent` | `apps/users/models.py` | #7, #8 |
| GT2 | Modello `CookieConsent` | nuova app `consent` | #7 |
| GT3 | Endpoint `POST /api/auth/consent/` | `apps/users/views.py` | #7, #8 |
| GT4 | Endpoint `GET /api/auth/me/data-export/` | `apps/users/views.py` | #8 |
| GT5 | Endpoint `DELETE /api/auth/me/` | `apps/users/views.py` | #8 |
| GT6 | UI checkbox accettazione in Register | `views/auth/Register.vue` | #7 |
| GT7 | UI cookie banner | `components/CookieBanner.vue` | #7 |
| GT8 | UI sezione privacy in Profile | `views/profile/Profile.vue` | #8 |
| GT9 | Page `/privacy` con MD render | `views/legal/PrivacyPage.vue` | #6 |
| GT10 | Page `/cookie` con MD render | `views/legal/CookiePage.vue` | #6 |
| GT11 | Footer con link a Privacy + Cookie + Termini | `App.vue` | #6 |
| GT12 | Self-host font (rimuove cookie banner per font) | `index.html` | #7 (in B1 audit) |
| GT13 | Lazy-load GSI solo post-consenso | `composables/useGoogleSignIn.js` | #7 |
| GT14 | Job Celery beat retention | `apps/users/tasks.py` | post-MVP |
| GT15 | Audit log admin (vedi M11 audit) | trasversale | post-MVP |
| GT16 | Anonimizzazione recensioni alla cancellazione account | `apps/users/services.py` | #8 |

---

## 4. Documenti legali da produrre (in `docs/legal/`)

Tutti con disclaimer "**bozza tecnica, non costituisce parere legale, validare con avvocato/DPO prima della pubblicazione**" + placeholder `[DENOMINAZIONE SOCIETÀ]`, `[P.IVA]`, `[SEDE LEGALE]`, `[EMAIL_CONTATTO_PRIVACY]`, `[PEC]`, `[NOME LEGALE RAPPRESENTANTE]`.

| File | Scopo | Pubblicazione |
|------|-------|---------------|
| `privacy_policy.md` | Informativa ex art. 13 | Public web `/privacy` |
| `cookie_policy.md` | Informativa cookie + tabella | Public web `/cookie` |
| `informativa_registrazione.md` | Snippet breve mostrato in checkbox registrazione | UI in form |
| `termini_servizio.md` | T&C piattaforma | Public web `/termini` |
| `registro_trattamenti.md` | Registro art. 30 (interno) | Documento aziendale |
| `sub_responsabili.md` | Lista DPA stipulati | Interno + sezione public privacy |
| `data_retention.md` | Policy retention | Interno |
| `dpia_minima.md` | DPIA per geolocalizzazione + scoring | Interno |
| `procedura_data_breach.md` | Procedura art. 33-34 | Interno |

→ Verranno tutti creati nel task #6.

---

## 5. Costituzione società e nomina figure

**Richiesto prima del go-live commerciale:**
1. Costituire/identificare società titolare → ottenere P.IVA, sede legale, PEC.
2. Nominare per iscritto:
   - Titolare del trattamento (la società).
   - Responsabili interni (sviluppatori, amministratori) con lettera incarico.
3. Valutare se nominare DPO:
   - Non obbligatorio se non si trattano dati su larga scala né categorie particolari.
   - **Consigliato** appena si supera ~1000 utenti o si trattano dati di minori.
4. Stipulare/accettare DPA con tutti i sub-responsabili (vedi §2.6).

→ Tracciato in `docs/security/TODO_USER.md` (creato in task #9).

---

## 6. Risk assessment — sintesi

| Rischio | Probabilità | Impatto | Risk score | Note |
|---------|-------------|---------|------------|------|
| Data breach via MITM Vercel→EC2 | Media | Alto | 🔴 ALTO | Pre-mitigation: nessuna. Post HTTPS: bassa. |
| XSS → token furto | Bassa-Media | Alto | 🟠 MEDIO-ALTO | Mitigato da SimpleJWT rotation, peggiora con XSS conclamata |
| Disclosure dati business via UserSerializer | Alta | Medio | 🟠 ALTO | Già osservato in audit (A3) |
| Reclamo Garante per cookie/Google Fonts | Bassa | Medio (sanzione fino a €20k) | 🟡 MEDIO | Sanata da self-host + banner |
| Reclamo Garante per assenza informativa | Media | Alto (sanzione fino a 4% fatturato o €20M) | 🔴 ALTO | Bloccante go-live |
| Stripe webhook spoofing → finanziario | Media | Alto | 🔴 ALTO | Vedi C1 audit |
| Account takeover (no email verify, no rate limit, no 2FA) | Media | Alto | 🔴 ALTO | Vedi A1, A5 audit |
| Geolocalizzazione print_node esposta | Alta (default) | Medio | 🟠 ALTO | Vedi A3 audit |

---

## 7. Roadmap allineata audit sicurezza

**Fase 0 — pre-go-live (questa sessione)**
- ✅ Audit sicurezza prodotto
- ✅ Gap analysis GDPR prodotta
- ⏳ Fix critici/safe su main (task #4)
- ⏳ Fix invasivi su branch security-audit (task #5)
- ⏳ Bozze documenti legali (task #6)
- ⏳ Cookie banner + consent (task #7)
- ⏳ Code path diritti interessati (task #8)
- ⏳ TODO finale utente (task #9)

**Fase 1 — settimana go-live (TODO utente)**
- Costituire/identificare società, ottenere P.IVA, PEC.
- Acquistare dominio + attivare HTTPS.
- Far validare bozze legali da avvocato.
- Pubblicare privacy/cookie/termini sul sito.
- Verificare DPA con sub-responsabili.
- Configurare AWS SES domain (necessario per email transactional non-sandbox).

**Fase 2 — primi 90 giorni**
- Pentest esterno.
- Implementare audit log admin.
- Implementare retention job Celery.
- Considerare 2FA admin + utenti.
- Verificare se serve DPO (al raggiungimento soglie).

**Fase 3 — quando si supera ~1000 utenti**
- Nominare DPO (interno o esterno).
- DPIA formale (anche se non strettamente obbligatoria, best practice).
- Iso 27001 / SOC2 valutazione.
