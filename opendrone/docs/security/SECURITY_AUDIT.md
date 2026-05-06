# SECURITY AUDIT — OpenDrone

**Data audit**: 2026-05-06
**Scope**: backend Django (`opendrone/backend`), frontend Vue (`opendrone/frontend`), infrastruttura (EC2 + RDS + S3 + nginx + Vercel), dipendenze.
**Stato app**: in produzione (Vercel + EC2 + RDS), nessun cliente reale ancora.
**Riferimento parallelo GDPR**: vedi `docs/legal/GDPR_GAP_ANALYSIS.md`.

> Disclaimer: questo audit è una review tecnica. Non sostituisce un pentest formale né un assessment legale. Per il go-live commerciale è raccomandato un pentest esterno.

---

## 0. Sommario esecutivo

| Severità | Conteggio | Note |
|----------|-----------|------|
| 🔴 CRITICO | 5 | Vanno chiusi prima di ogni cliente reale |
| 🟠 ALTO | 11 | Vanno chiusi a breve (1-2 settimane) |
| 🟡 MEDIO | 11 | Vanno schedulati nel backlog |
| 🟢 BASSO | 8 | Nice-to-have / igiene |

**Top 3 da risolvere subito:**
1. **Stripe webhook accetta payload non firmato** in fallback (`payments/views.py:33-40`) → un attaccante può forgiare `payment_intent.succeeded` e attivare `Transfer.create` Stripe verso designer/nodi/assembly.
2. **Endpoint subscribe crea Subscription attiva senza pagamento** (`payments/views.py:164-178`) → revenue loss, abuso piano premium.
3. **Backend EC2 in HTTP plain** + JWT in `localStorage` → MITM sulla tratta Vercel→EC2 (token + PII in chiaro), e XSS-driven account takeover lato client.

---

## 1. Mappa flusso dati personali (PII)

```
USER (browser HTTPS)
  │  email, password / Google id_token
  ▼
VERCEL (HTTPS, EU)                            ◄── frontend statico, GSI script da accounts.google.com
  │  rewrites:
  │    /api/(.*)  → http://16.170.111.228 (HTTP PLAIN! ◄── 🔴 CRITICO)
  │    /(.*)      → /index.html
  ▼
EC2 nginx :80 (HTTP) ── eu-north-1
  │
  ▼
gunicorn :8000 (Django)
  ├── PostgreSQL RDS eu-north-1 (sslmode=require ✓)
  │   • users.User (email, first/last, bio, avatar)
  │   • DesignerProfile (portfolio, royalties_earned)
  │   • PrintNodeProfile / AssemblyCenterProfile (P.IVA implicita, indirizzo, lat/lon, prezzi)
  │   • Order (shipping_address JSON, tracking)
  │   • RoyaltyLedger (importi)
  │   • Notification.message (testi PII)
  ├── S3 opendrone-files eu-south-1 (private ACL ✓)
  │   • avatars/, brands/, projects/ (file STL, BOM, immagini)
  ├── Redis (Celery broker, no PII)
  ├── Stripe (sub-responsabile US-EU, dati pagamento)
  ├── Google OAuth (sub-responsabile, verifica id_token)
  └── AWS SES eu-south-1 (sub-responsabile email transazionali)

LATO CLIENT
  • access_token + refresh_token in localStorage  ◄── 🔴 vulnerabile a XSS
  • Google Fonts caricati da fonts.gstatic.com    ◄── 🟢 trasferimento IP a Google senza consenso
  • Google Identity Services script               ◄── caricato in lazy ma comunque trasferimento DNS pre-consenso
```

---

## 2. CRITICI 🔴

### C1 — Stripe webhook accetta payload non firmato in fallback
**File:** `opendrone/backend/apps/payments/views.py:33-40`
**Impatto:** un attaccante che raggiunga `POST /api/payments/webhook/` può inviare un finto `payment_intent.succeeded` con `id` valorizzato. Il codice cerca `Order` con quell'id e chiama `_execute_transfers`, che attiva `stripe.Transfer.create` verso `designer.stripe_account_id` / nodo stampa / assembly. Anche se i transfer Stripe richiedono saldo, il bypass del controllo firma trasforma un endpoint pubblico in un trigger arbitrario di logica finanziaria + abilita transizione di stato `payment_confirmed` su qualsiasi ordine.
```python
if settings.STRIPE_WEBHOOK_SECRET and not settings.STRIPE_WEBHOOK_SECRET.endswith('xxx'):
    try: event = stripe.Webhook.construct_event(...)
    except (...): return Response(status=400)
else:
    event = json.loads(payload)   # ← nessuna verifica
```
**Fix:**
- Rimuovere il fallback. Se `STRIPE_WEBHOOK_SECRET` non è configurato in produzione, `LOGGING.error` + `return Response(status=503)`. Nessun parsing senza firma.
- In dev/locale usare Stripe CLI (`stripe listen --forward-to ...`) che imposta un secret di test.
- Aggiungere assert di boot: in `production.py`, `assert STRIPE_WEBHOOK_SECRET` se la rotta è esposta.

### C2 — Subscribe crea abbonamento attivo senza pagamento
**File:** `opendrone/backend/apps/payments/views.py:164-178`
**Impatto:** chiunque autenticato chiama `POST /api/payments/subscriptions/subscribe/` con `plan_id` valido e ottiene `Subscription(status='active')`. Nessuna integrazione Stripe Subscription, nessun pagamento. Bypass commerciale + se il piano sblocca feature lato app, anche escalation di privilegi commerciali.
**Fix:**
- Sostituire con Stripe Checkout Session: creare Checkout, ritornare URL, attivare la sub solo dopo `customer.subscription.created` via webhook firmato.
- Nel frattempo, se la rotta non serve a nessuno: rimuoverla o restituire `503 not implemented`.

### C3 — Backend HTTP plain (token + PII in chiaro tra Vercel ed EC2)
**File:** `opendrone/frontend/vercel.json:3-4`, `opendrone/nginx/opendrone.conf:1-3`, `opendrone/backend/config/settings/production.py:10-16`
**Impatto:** ogni request Vercel→EC2 viaggia in chiaro su Internet pubblico inclusi: `Authorization: Bearer <jwt>`, payload con email/password al login (anche `email/password` in `POST /api/auth/login/`), `id_token` Google, `shipping_address`, `internal_notes`, ecc. Un MITM tra Vercel e l'EC2 (route AWS / ISP / WAN) può intercettare credenziali e prendere il controllo degli account. Anche il path `/admin/` Django è raggiungibile in HTTP.
**Fix:** vedi [TODO finale: Domain + SSL] (`docs/security/TODO_USER.md`).
- Acquistare dominio, puntare A record sull'EIP, generare cert Let's Encrypt via certbot (già nel docker-compose).
- Riconfigurare nginx HTTPS, redirect 80→443, riattivare in `.env`:
  - `SECURE_SSL_REDIRECT=True`
  - `SECURE_HSTS_SECONDS=31536000`
  - `SESSION_COOKIE_SECURE=True`
  - `CSRF_COOKIE_SECURE=True`
- Aggiornare `vercel.json` rewrites a `https://api.<dominio>`.
- Mitigazione temporanea (mentre si compra dominio): scope minimo, niente clienti reali, niente admin login da reti pubbliche.

### C4 — JWT in localStorage (token furto via XSS)
**File:** `opendrone/frontend/src/api/client.js:11-13`, `opendrone/frontend/src/stores/auth.js:7-8,22-23,30-33,42-43,54-55`
**Impatto:** access_token + refresh_token in `localStorage` significa che qualsiasi XSS (anche da una dependency npm compromessa, o da un iframe non sandboxato in futuro) ruba sessione + refresh long-lived (30 giorni). I refresh sono ROTATE+BLACKLIST (mitigazione parziale: il furto invalida la sessione legittima al primo refresh, rendendolo rilevabile), ma nel frattempo l'attaccante esfiltra dati e azioni a nome dell'utente.
**Fix (refactor invasivo, branch dedicato):**
- Spostare il refresh token in **HttpOnly + Secure + SameSite=Strict cookie**. Endpoint `/auth/token/refresh/` legge il cookie, ritorna nuovo access in JSON.
- Access token può restare in memoria (non localStorage). Lo si tiene nel Pinia store; se l'utente ricarica si rigenera dal refresh cookie.
- CSRF: con SameSite=Strict + check Origin/Referer non serve double-submit, ma per le mutation aggiungere header `X-Requested-With` controllato lato server.
- Logout: endpoint che blacklista refresh + cancella cookie.

### C5 — `.env.production` tracciato in repo (template confuso)
**File:** `opendrone/backend/.env.production`, presente in `git ls-files`. Anche se contiene solo placeholder (`CAMBIA-...`, `AKIAIOSFODNN7EXAMPLE`, `sk_live_xxx`), è committato e l'opendrone/.gitignore ha una rule `backend/.env.production` che fa pensare che sia ignorato (non lo è perché era già tracked).
**Impatto:** chiunque cloni il repo in futuro può sovrascrivere i placeholder e committare per errore segreti veri. Inoltre il file `.env.example` esiste già come template legittimo, quindi `.env.production` è un duplicato fuorviante.
**Fix:**
- `git rm --cached opendrone/backend/.env.production` + commit.
- Rinominare in `opendrone/backend/.env.production.example` se utile come reference, altrimenti eliminare.
- Verificare `opendrone/opendrone/backend/.env.example` (struttura duplicata sospetta) e ripulire.
- Aggiungere assert in CI (anche solo un grep `git ls-files | grep -E '\.env(\.production)?$' && exit 1`).

---

## 3. ALTI 🟠

### A1 — Nessun rate limiting su login/register/google
**File:** `opendrone/backend/apps/users/views.py:37-50, 56-150, 20-34`
**Impatto:** brute force credenziali, user enumeration via login (risposta diversa per email inesistente vs password sbagliata), abuso registrazione, abuso verify Google id_token.
**Fix:**
- Aggiungere `django-ratelimit` o usare `DEFAULT_THROTTLE_CLASSES` di DRF: scope `login` (5/min/IP), `register` (3/min/IP), `google_auth` (10/min/IP).
- Per login: rispondere SEMPRE con stesso messaggio generico (già fatto: "Credenziali non valide.") + non distinguere via timing (usa `authenticate()` con dummy hash quando email non esiste).
- Considerare CAPTCHA (hCaptcha o Turnstile) dopo N tentativi falliti.

### A2 — Admin Django (`/admin/`) in HTTP plain
**File:** `opendrone/backend/config/urls.py:7`, deploy in HTTP.
**Impatto:** session cookie admin sniffabile → admin takeover totale (read/write su tutti i dati personali via Django admin).
**Fix:**
- Bloccare `/admin/` finché non c'è HTTPS: nginx `location /admin/ { return 403; }` oppure `allow <ip-tuo>; deny all;`.
- Lungo termine: HTTPS (vedi C3) + 2FA admin (`django-otp` o `django-allauth`).
- Spostare l'admin su un path non-default (`ADMIN_URL` env) come security-by-obscurity aggiuntiva.

### A3 — UserSerializer espone profili business sensibili a utenti terzi
**File:** `opendrone/backend/apps/users/serializers.py:66-95`, `apps/marketplace/serializers.py:116` (`designer = UserSerializer(read_only=True)` in `DroneProjectDetailSerializer`).
**Impatto:** quando un visitatore (anche anonimo via `AllowAny` sul detail progetto) chiama `GET /api/projects/<slug>/`, riceve `designer = UserSerializer()` che include `designer_profile` con `total_royalties_earned`, `rating`, `total_reviews`. Analogamente, qualsiasi user che vede un altro user (es. via order o review) vede `print_node_profile` con `address`, `latitude`, `longitude`, `price_per_gram`, `total_revenue` e `assembly_profile` con dati commerciali equivalenti. Disclosure di dati economici e fiscali sensibili.
**Fix:**
- Creare due serializer: `UserPublicSerializer` (id, first_name, last_name, avatar) e `UserPrivateSerializer` (full). Il `MeView` usa private; tutti gli altri rendering usano public.
- Per il designer mostrato sul progetto: solo first_name/last_name + (eventuale link al profilo pubblico opt-in).
- Per print_node/assembly sul detail order: solo `business_name` + city, nessuna lat/lon, nessun fatturato.

### A4 — OrderSerializer espone (e accetta in scrittura) `internal_notes`
**File:** `opendrone/backend/apps/orders/serializers.py:24-34`
**Impatto:** `fields = '__all__'` con `read_only_fields` che NON include `internal_notes` né `shipping_address` né `tracking_number` né `courier`. Conseguenze:
- Customer legge `internal_notes` (può contenere appunti operativi non destinati al cliente).
- Customer può fare `PATCH` su `internal_notes` se la view lo permette (qui solo update_order_status patcha campi specifici, ma se aprissimo un Generic update sarebbe leak).
- `shipping_address`, `tracking_number`, `courier` non protetti da modifica accidentale via API.
**Fix:**
- `read_only_fields` esplicito: `['internal_notes']` rimosso dall'output e non scrivibile da non-admin.
- Considerare due serializer: `OrderCustomerSerializer` (no internal_notes), `OrderAdminSerializer` (full).

### A5 — Manca verifica email per registrazione email/password
**File:** `opendrone/backend/apps/users/views.py:20-34`, `apps/users/models.py:32` (`is_verified=False` ma non blocca login).
**Impatto:** account fake, recupero password impossibile (a fortiori vedi A6), spam registrazione, disclosure email valide.
**Fix:**
- Implementare email verification: alla registrazione spedire link firmato (`signing.dumps`) con scadenza 24h, endpoint `/api/auth/verify-email/<token>/`.
- Bloccare login finché non `is_verified=True` (opzionale: grace period 7gg).
- Per Google OAuth `is_verified=True` automatico (già fatto, OK).

### A6 — Manca password reset flow
**File:** `opendrone/backend/apps/users/views.py` (assente).
**Impatto:** utente che dimentica password non recupera l'account → richiesta manuale o account perso.
**Fix:**
- `POST /api/auth/password-reset/` con email → invio link firmato (anti-enumeration: rispondere sempre 200 anche se email non esiste).
- `POST /api/auth/password-reset-confirm/<token>/` con nuova password.
- Invalidare tutti i refresh token dell'utente al reset.

### A7 — nginx config nel repo ha IP obsoleto e mismatch con prod
**File:** `opendrone/nginx/opendrone.conf:3` ha `server_name 16.171.15.90;` (vecchio IP, sostituito da Elastic IP `16.170.111.228`).
**Impatto:** confusion in caso di rebuild dei container. Se docker-compose rigenera nginx dal file in repo, il `server_name` non matchera l'host header reale → comportamento inatteso (nginx accetta tutto comunque su default server, OK, ma è log inquinante e segnale di drift). La memory dice che l'EC2 ha modifiche locali permanenti al file → drift confermato.
**Fix:**
- Rimuovere il filtro `server_name` (usare `_`) o mettere il placeholder via env.
- Long-term: parametrizzare l'host con env file letto da nginx (`envsubst` su template).
- Aggiungere note in `DEPLOY.md` che il nginx live è divergente.

### A8 — Logout ignora errori del refresh token blacklist
**File:** `opendrone/backend/apps/users/views.py:155-161`
```python
try: token = RefreshToken(request.data.get('refresh')); token.blacklist()
except Exception: pass
return Response({'detail': 'Logout effettuato.'})
```
**Impatto:** se il client invia un refresh non valido o vuoto, il backend risponde "Logout effettuato" ma il refresh originale resta valido. L'utente crede di aver chiuso sessione, l'attacker (o il device dimenticato) continua ad avere accesso.
**Fix:**
- Loggare warning quando blacklist fallisce.
- Richiedere il refresh come field obbligatorio, rispondere 400 se mancante, 401 se invalido.
- Considerare blacklist di TUTTI i refresh dell'utente al logout (token cleanup completo).

### A9 — ChangePassword non revoca refresh token esistenti
**File:** `opendrone/backend/apps/users/views.py:172-182`
**Impatto:** dopo cambio password, sessioni su altri device restano attive con i vecchi refresh token. Tipicamente dopo cambio password si vuole invalidare tutto (specie in caso di sospetto compromise).
**Fix:**
- Dopo `user.set_password(new); user.save()`: `OutstandingToken.objects.filter(user=user).update(blacklisted=True)` (o analogo: iterare e blacklistare).
- Stessa cosa nel password-reset (A6).

### A10 — Stripe SDK inizializzato a module-load time
**File:** `opendrone/backend/apps/payments/views.py:15`, `apps/orders/views.py:16`
```python
stripe.api_key = settings.STRIPE_SECRET_KEY
```
**Impatto:** se `STRIPE_SECRET_KEY` cambia (es. env hot-reload o key rotation), serve restart container. Inoltre se il modulo viene importato prima di `settings`, fallisce. In multi-worker gunicorn, ogni worker ha il proprio `stripe.api_key`. Non è una vuln diretta ma è fragile.
**Fix:**
- Inizializzare lazy: piccola util `def stripe_client(): stripe.api_key = settings.STRIPE_SECRET_KEY; return stripe`.
- Documentare in `DEPLOY.md` la procedura di key rotation (richiede `docker compose restart backend`).

### A11 — File upload (`ProjectFile`, `avatar`) senza validazione tipo/size/MIME
**File:** `opendrone/backend/apps/marketplace/views.py:140-159`, `apps/users/models.py:27` (`avatar = ImageField`).
**Impatto:** un utente può caricare file arbitrari su S3 con qualsiasi extension/MIME. Rischi:
- Storage abuse (cloud bill esplode).
- Caricamento di file malevoli (HTML/SVG con payload XSS) — anche se S3 default ACL è private, se il presigned URL viene aperto in iframe c'è XSS via `Content-Type` ereditato.
- Caricamento di malware destinato ad altri utenti (designer pubblica, customer scarica).
**Fix:**
- Validare file size lato serializer (es. max 50 MB, già nginx `client_max_body_size 50M`).
- Whitelist extension per `file_type`: `stl` → `.stl`, `bom` → `.csv/.json/.xlsx`, `image` → `.jpg/.png/.webp`, ecc.
- Rifiutare MIME `text/html`, `image/svg+xml`, `application/javascript`.
- Su S3: forzare `ContentDisposition='attachment; filename=...'` per impedire rendering inline browser.
- Considerare scan AV (es. ClamAV via Lambda S3 trigger) prima di marcare il file `is_public=True`.

---

## 4. MEDI 🟡

### M1 — Pagination disabilitata su list endpoint admin
**File:** `apps/users/views.py:223` (`AdminUsersListView pagination_class = None`), `apps/marketplace/views.py:246, 261, 282` (admin projects), `apps/marketplace/views.py:213, 224` (categories, brands).
**Impatto:** quando ci saranno molti utenti/progetti, una singola GET restituirà migliaia di record (slow, DOS, spike memoria, mass disclosure dati personali). Per `categories`/`brands` è meno grave (cardinalità bassa) ma resta pattern fragile.
**Fix:**
- Lasciare la paginazione default (20 records, già configurata in `base.py:88-89`).
- Frontend: gestire la paginazione (already common pattern in DRF).

### M2 — `SECURE_PROXY_SSL_HEADER` attivo ma EC2 raggiungibile diretto
**File:** `opendrone/backend/config/settings/production.py:14`
**Impatto:** `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` istruisce Django a fidarsi dell'header. Oggi è innocuo perché `SECURE_SSL_REDIRECT=False`. Quando andremo in HTTPS (C3) e attiveremo `SESSION_COOKIE_SECURE=True`, un attaccante che bypassi il proxy (porta 80 EC2 aperta a `0.0.0.0/0`) e mandi `X-Forwarded-Proto: https` farà credere a Django di essere su HTTPS quando non lo è.
**Fix:**
- Aggiungere middleware/setting per fidarsi dell'header solo se l'IP source è nel range del proxy (Cloudflare/Vercel se in mezzo, oppure rete interna nginx).
- O più semplice: chiudere porta 80 EC2 al solo nginx interno + accettare solo connessioni da Vercel via Cloudflare Tunnel / private link (vedi cartella `cloudflared` untracked sull'EC2 menzionata in memoria).

### M3 — CORS `allow_credentials=True` senza utilizzo cookie di sessione
**File:** `opendrone/backend/config/settings/base.py:108`
**Impatto:** la combinazione `CORS_ALLOW_CREDENTIALS=True` + token in `localStorage` (non in cookie) è incoerente. Non porta direttamente a vuln, ma se in futuro si introducono cookie di sessione e una origin viene dimenticata in whitelist, il rischio CSRF cross-origin diventa reale.
**Fix:**
- Mettere a `False` se non si usano cookie di auth (ora). Quando si passa a refresh-cookie HttpOnly (C4 fix), allora rimettere `True` con whitelist origin stretta.

### M4 — Mancano headers di sicurezza HTTP (CSP, COOP, Referrer-Policy, Permissions-Policy, X-Content-Type-Options)
**File:** `opendrone/backend/config/settings/production.py` (assenti), `opendrone/nginx/opendrone.conf` (assenti).
**Impatto:** XSS post-leak più grave (no CSP), navigator metadata leakage, embedding in iframe terzo, ecc.
**Fix:**
- In `production.py`:
  ```python
  SECURE_CONTENT_TYPE_NOSNIFF = True
  SECURE_REFERRER_POLICY = 'same-origin'
  X_FRAME_OPTIONS = 'DENY'
  ```
- Aggiungere `django-csp` con `CSP_DEFAULT_SRC = ("'self'",)` + whitelist per Stripe.js, Google GSI, Google Fonts, S3.
- Aggiungere `Permissions-Policy: geolocation=(), microphone=(), camera=()` via nginx o middleware.
- Su Vercel aggiungere `headers` in `vercel.json` (CSP, HSTS dopo HTTPS, X-Content-Type-Options).

### M5 — `shipping_address` JSONField senza schema validation
**File:** `opendrone/backend/apps/orders/serializers.py:42` (`shipping_address = serializers.DictField()`)
**Impatto:** accetta qualsiasi dict (anche annidato profondo, anche con type confusion). Se un campo viene letto poi senza coercion (es. `shipping.get('latitude')` casted a float in `views.py:46-47`), una stringa malformata può crashare. PII non strutturata = audit difficile.
**Fix:**
- Definire `class ShippingAddressSerializer(serializers.Serializer): street, city, postal_code, country, latitude, longitude, ...` con `validators` su CAP, country code, ecc.
- Usare nested serializer in `OrderCreateSerializer`.

### M6 — `ProjectReview.reviewer_name` espone nome+cognome senza opt-out
**File:** `opendrone/backend/apps/marketplace/serializers.py:65-73`
**Impatto:** ogni review pubblica include "Mario Rossi" (full name del reviewer). Se l'utente non vuole comparire pubblicamente (legittimo per recensioni), non c'è opzione. GDPR: legittimo interesse contestabile, l'utente deve poter scegliere alias.
**Fix:**
- Aggiungere campo opzionale `display_name` su `User` o `ProjectReview` (alias scelto dall'utente).
- Default: mostrare solo `first_name + first letter of last_name` ("Mario R."), full name solo opt-in.

### M7 — Permessi check duplicati con stile incoerente
**File:** `apps/marketplace/views.py:294-303, 306-316, 321-335, 338-351`, `apps/users/views.py:240-263`
**Impatto:** stessa logica `if not (user.is_staff or user.has_role('admin'))` ripetuta in 5+ view. Se domani cambia la definizione di "admin" (es. nuovo ruolo "moderatore"), bisogna toccare ogni view. Code smell, non security ma authorization-prone-to-drift.
**Fix:**
- Usare uniformemente `permission_classes = [IsAuthenticated, IsAdminUser]` (la classe `IsAdminUser` esiste già in `apps/users/permissions.py:19-23`).
- Convertire i `@api_view` admin in `APIView` o aggiungere `@permission_classes([IsAdminUser])`.

### M8 — `roles__contains=[role]` PG-only (non bloccante ma fragile)
**File:** `apps/users/views.py:233`, `apps/marketplace/views.py:229`
**Impatto:** funziona solo su Postgres (`JSONField __contains`). Un eventuale switch DB lo rompe. Inoltre `roles__contains` su JSONField non usa indici → slow su molti utenti.
**Fix:**
- Lungo termine: convertire `roles JSONField` in `ManyToMany('Role')` oppure aggiungere campi `is_designer`, `is_print_node`, ecc. con indici.

### M9 — `OrderListView` non mostra ordini ai print_node/assembly come fornitori
**File:** `apps/orders/views.py:23-27`
**Impatto:** un print_node che riceve ordini da stampare non li vede via `GET /api/orders/`. Bug funzionale, ma sintomo di permission model incompleto.
**Fix:**
- Estendere queryset: include ordini dove user è `print_node` o `assembly_center`.

### M10 — `AUTH_PASSWORD_VALIDATORS` con `MinimumLengthValidator` default (8 chars)
**File:** `opendrone/backend/config/settings/base.py:161-166`
**Impatto:** 8 caratteri è minimo industry, ma OWASP racc. 12. Inoltre mancano controlli ad-hoc.
**Fix:**
- `MinimumLengthValidator(min_length=12)`.
- Considerare `django-passwords` o lista pwned passwords (have-i-been-pwned API).

### M11 — Audit log assente per azioni admin
**File:** `apps/users/views.py:240-277` (admin_update_user, certify), `apps/marketplace/views.py:294-351` (approve, reject, archive).
**Impatto:** non c'è traccia di chi-quando-cosa per azioni amministrative. Compliance / forensics impossibile.
**Fix:**
- Modello `AdminAuditLog(user, action, target_type, target_id, payload, created_at)` o usare `django-simple-history` / `django-auditlog` per tracking automatico.

---

## 5. BASSI 🟢

### B1 — Frontend carica Google Fonts senza consenso
**File:** `opendrone/frontend/index.html:7-9`
**Impatto:** preconnect/load di `fonts.googleapis.com` e `fonts.gstatic.com` invia IP utente a Google prima del consenso cookie/tracker. Tema GDPR (caso noto: sentenza Monaco 2022).
**Fix:**
- Self-host i font WOFF2 (Inter, Syne, DM Mono) sotto `/assets/fonts/`.
- Vercel rewrite o copy in build.

### B2 — Google Identity Services script caricato in lazy ma comunque trasferimento DNS pre-consenso
**File:** `opendrone/frontend/src/composables/useGoogleSignIn.js:7-28`
**Impatto:** il script viene caricato sulle pagine `/login` e `/register` step 2, anche se l'utente non clicca "Accedi con Google". Trasferimento dati a Google.
**Fix:**
- Caricare GSI solo on-demand (al click su "Accedi con Google" / button render). Refactor: lazy load in callback del button click.
- In ogni caso menzionare in privacy policy/cookie policy.

### B3 — Title HTML inconsistente con brand
**File:** `opendrone/frontend/index.html:6` `<title>PolyDrone — Marketplace open hardware</title>`
**Impatto:** branding inconsistente. Se PolyDrone è nome storico, OK; se refuso, fix.
**Fix:** decidere brand definitivo, allineare title.

### B4 — Frontend logga errori Google in console
**File:** `opendrone/frontend/src/views/auth/Login.vue:118`, `Register.vue:187`
**Impatto:** info disclosure minima, non sensibile.
**Fix:** rimuovere o filtrare in produzione.

### B5 — `internal_notes` esposto in OrderSerializer (incluso anche in M11)
Vedi A4. Già listato.

### B6 — `STRIPE_SECRET_KEY` default `''` permette boot senza Stripe
**File:** `opendrone/backend/config/settings/base.py:144-146`
**Impatto:** server boota senza Stripe (utile in dev), ma se ALLOWED_HOSTS è dominio prod e `STRIPE_SECRET_KEY=''`, l'app è in stato inconsistente.
**Fix:**
- In `production.py`: `assert STRIPE_SECRET_KEY, 'Stripe SK obbligatoria in prod'` se la rotta /payments è abilitata.

### B7 — `Order.shipping_address` letta con default arbitrari Bologna
**File:** `apps/orders/views.py:46-47` `shipping_lat = float(shipping.get('latitude', 44.4))` (44.4, 11.3 = Bologna).
**Impatto:** se il client manda payload senza lat/lon, l'ordine viene assegnato come se fosse a Bologna. Bug funzionale + audit data quality.
**Fix:** rendere lat/lon obbligatori in `ShippingAddressSerializer` (M5).

### B8 — Struttura repo `opendrone/opendrone/` duplicata
**File:** `Glob` mostra `opendrone/opendrone/backend/.env`, `opendrone/opendrone/docker-compose.prod.yml`, ecc.
**Impatto:** confusion. Probabilmente artefatto da deployment iniziale.
**Fix:** verificare se è cartella usata, altrimenti `git rm -rf opendrone/opendrone`.

---

## 6. Dipendenze (snapshot 2026-05-06)

Backend `requirements.txt`:
- Django 5.0.4 — ⚠️ **5.0.x EOL ad agosto 2025**, raccomandato passare a Django 5.1.x LTS o 5.2 (LTS aprile 2025)
- DRF 3.15.1 — ok
- djangorestframework-simplejwt 5.3.1 — ok
- django-cors-headers 4.3.1 — ok
- python-decouple 3.8 — ok
- Pillow 10.3.0 — ⚠️ patch 10.3.0 ha CVE noti, raccomandato 11.x
- gunicorn 22.0.0 — ok
- stripe 9.9.0 — ok (ultima 11.x al 2026)
- boto3 1.34.101 — datata ma ok
- google-auth 2.35.0 — ok

Frontend `package.json`:
- vue 3.4.0, vue-router 4.3.0, pinia 2.1.0 — datate, da aggiornare a vue 3.5.x, pinia 2.3.x
- axios 1.6.0 — ⚠️ ha CVE-2024-39338 (SSRF), aggiornare a 1.7.4+
- @stripe/stripe-js 3.0.0 — datata, 4.x disponibile

**Action:** lanciare `pip list --outdated`, `npm audit`, valutare upgrade in branch dedicato (test e2e prima di deploy).

---

## 7. Mappa fix → priorità → branch

| ID | Fix | Branch | Stima |
|----|-----|--------|-------|
| C1 | Stripe webhook strict | `security-audit` | 30 min |
| C2 | Disabilitare subscribe stub | `security-audit` | 15 min |
| C3 | HTTPS + dominio | bloccato su acquisto dominio (TODO_USER) | 2-3 ore |
| C4 | Refactor token in HttpOnly cookie | `security-audit` (deploy con OK) | 4-6 ore |
| C5 | Rimuovere .env.production da repo | `main` (safe) | 10 min |
| A1 | Rate limit | `main` (safe) | 1 ora |
| A2 | Block /admin/ in HTTP | `main` via nginx update | 30 min |
| A3 | UserPublicSerializer | `security-audit` | 2 ore |
| A4 | OrderSerializer split | `security-audit` | 1 ora |
| A5 | Email verification | `feature/email-verify` | 3 ore |
| A6 | Password reset | `feature/password-reset` | 3 ore |
| A7 | nginx config update | `main` | 15 min |
| A8 | Logout strict | `main` | 15 min |
| A9 | Revoke refresh on password change | `main` | 30 min |
| A10 | Stripe lazy init | `main` | 30 min |
| A11 | File upload validation | `security-audit` | 2 ore |
| M1 | Riabilitare paginazione | `main` (con frontend) | 1 ora |
| M2 | SECURE_PROXY_SSL_HEADER trust IP | dopo HTTPS | 30 min |
| M3 | CORS_ALLOW_CREDENTIALS=False | `main` (verificare frontend) | 15 min |
| M4 | Security headers | `main` | 1 ora |
| M5 | shipping_address schema | `security-audit` | 1 ora |
| M6 | Review display_name opt-in | `feature/review-privacy` | 2 ore |
| M7 | Permission class consistency | `main` | 1 ora |
| M11 | Audit log admin | `feature/audit-log` | 4 ore |
| B1 | Self-host fonts | `main` | 1 ora |
| B2 | GSI on-click load | `main` | 30 min |

---

## 8. Cosa NON è stato testato in questo audit

- Pentest dinamico (BurpSuite/ZAP)
- Fuzzing API
- Race conditions (es. doppio webhook payment)
- Rate limit bypass tramite distribuzione IP (servirebbe WAF)
- Privilege escalation chain end-to-end multi-ruolo
- Vulnerabilità in dependency tree completo (`npm audit` / `pip-audit`)
- Sicurezza fisica EC2 (AWS shared responsibility)
- Configurazione IAM AWS (chi può accedere al bucket S3, alla console, ecc.)
- Backup/restore RDS (RPO/RTO)

Per il go-live commerciale, raccomandato pentest esterno (3-5 giorni man).
