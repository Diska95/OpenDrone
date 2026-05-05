# Manuale OpenDrone

Documentazione del sistema, dei flussi di autenticazione, della guida operativa per
utenti finali e per amministratori.

> **Aggiornato al**: 2026-05-05
> **URL produzione**: https://open-drone-virid.vercel.app

---

## Indice

1. [Architettura del sistema](#architettura)
2. [Cosa fa ogni macchina](#cosa-fa-ogni-macchina)
3. [Modalità di autenticazione](#modalità-di-autenticazione)
4. [Ruoli utente](#ruoli-utente)
5. [Guida utente finale](#guida-utente-finale)
6. [Guida gestore (admin)](#guida-gestore-admin)
7. [FAQ e troubleshooting](#faq-e-troubleshooting)

---

## Architettura

OpenDrone è un'applicazione web composta da **frontend SPA** (Vue 3) e **backend
API** (Django REST Framework). Le due parti sono ospitate su provider diversi e
comunicano via HTTPS.

### Diagramma di flusso

```
                  ┌─────────────────────────────────────┐
                  │        Utente (browser)             │
                  │  https://open-drone-virid.vercel.app│
                  └──────────────┬──────────────────────┘
                                 │ HTTPS
                                 ▼
            ┌────────────────────────────────────────────┐
            │ VERCEL (CDN globale + Frontend statico)    │
            │ - serve l'app Vue compilata (HTML+JS+CSS)  │
            │ - gestisce SPA fallback (/login → index)   │
            │ - rewrite /api/* verso EC2                 │
            └──────────┬─────────────────────┬───────────┘
                       │                     │
                       │ /                   │ /api/*
                       │ (file statici)      │ (proxy HTTP)
                       │                     ▼
                       │     ┌──────────────────────────────────┐
                       │     │  AWS EC2 (16.170.111.228)        │
                       │     │  Ubuntu 26.04 · t3.micro         │
                       │     │  Elastic IP                      │
                       │     │                                  │
                       │     │  ┌──────────────────────────┐    │
                       │     │  │ NGINX (porta 80)         │    │
                       │     │  └──┬───────────────────────┘    │
                       │     │     │                            │
                       │     │  ┌──▼─────────────────────────┐  │
                       │     │  │ Django + Gunicorn :8000    │  │
                       │     │  │ (container Docker)         │  │
                       │     │  └──┬─────────────────────────┘  │
                       │     │     │                            │
                       │     │  ┌──▼──────┐  ┌──────────────┐   │
                       │     │  │ Celery  │  │ Redis        │   │
                       │     │  │ worker  │  │ (broker)     │   │
                       │     │  └─────────┘  └──────────────┘   │
                       │     └────────┬────────┬────────────────┘
                       │              │        │
                       │              ▼        ▼
                       │   ┌──────────────┐ ┌──────────────┐
                       │   │ AWS RDS      │ │ AWS S3       │
                       │   │ PostgreSQL   │ │ opendrone-   │
                       │   │ (eu-north-1) │ │ files        │
                       │   └──────────────┘ │ (eu-south-1) │
                       │                    └──────────────┘
                       │
                       └─────► fonts.googleapis.com
                                accounts.google.com (OAuth)
```

---

## Cosa fa ogni macchina

### Vercel
**Cosa fa**: serve la parte frontend (Vue) e fa da gateway HTTPS verso il backend.

**In dettaglio**:
- Ospita il sito statico compilato da `opendrone/frontend` (HTML, JS, CSS,
  immagini) su una CDN globale → caricamento veloce per gli utenti
- Gestisce HTTPS automaticamente (certificato Let's Encrypt rinnovato in
  background)
- Esegue le **rewrite rules** definite in `frontend/vercel.json`:
  - `/api/*` → forward a `http://16.170.111.228/api/*` (proxy verso il backend
    EC2)
  - `/(*)` → fallback a `/index.html` (necessario per le SPA: quando un utente
    apre direttamente `/login`, Vercel serve `index.html` e il router Vue
    gestisce la route lato client)
- Triggera un **build automatico** ogni push su `main` di GitHub
- Env vars in produzione:
  - `VITE_API_URL=/api`
  - `VITE_GOOGLE_CLIENT_ID=805523359996-...apps.googleusercontent.com`

**Quando NON usare Vercel**: per il backend dati (Django serve da EC2). Vercel
non ha database persistente.

### AWS EC2 (`16.170.111.228`)
**Cosa fa**: ospita il backend Django e tutti i servizi di supporto.

**In dettaglio**:
- Una sola istanza `t3.micro` (1 GB RAM, 2 vCPU, 19 GB disco) in zona
  `eu-north-1b` (Stoccolma)
- IP pubblico **elastico** (`16.170.111.228`): non cambia anche dopo
  Stop+Start, quindi i rewrite Vercel rimangono validi
- Su questa macchina girano **5 container Docker** orchestrati da
  `docker-compose.prod.yml`:
  1. **nginx** (porta 80): reverse proxy, riceve le richieste HTTP da Vercel
     e le inoltra a Django
  2. **backend** (Django + gunicorn, porta 8000 interna): l'API REST
     (`/api/auth/`, `/api/projects/`, `/api/orders/`, ecc.)
  3. **celery**: worker per task asincroni (validazione STL, invio email, ecc.)
  4. **celery-beat**: scheduler per task ricorrenti
  5. **redis**: broker di messaggi tra Django e Celery
- Ha **2 GB di swap** su `/swapfile` (necessario perché 1 GB di RAM non basta
  per i `docker compose build`)
- Tutto in HTTP (no SSL): SSL lo gestisce Vercel; tra Vercel e EC2 si usa
  HTTP perché i due sono già in collegamento "interno" via il rewrite

**Quando NON usare EC2**: per servire pagine statiche al browser (lo fa già
Vercel più velocemente).

### AWS RDS PostgreSQL
**Cosa fa**: database relazionale persistente per tutti i dati dell'app.

**In dettaglio**:
- Endpoint: `opendrone.c9iiqqiiskta.eu-north-1.rds.amazonaws.com`
- Database: `opendrone`, user `opendrone_user`
- PostgreSQL 16
- Contiene: utenti, progetti drone, ordini, BOM, recensioni, categorie, brand
- Backup automatici giornalieri gestiti da AWS
- Accessibile **solo dall'EC2** (security group)

### AWS S3 (`opendrone-files`)
**Cosa fa**: storage per file caricati dagli utenti.

**In dettaglio**:
- Bucket in zona `eu-south-1` (Milano)
- Contiene: immagini di copertina progetti, file STL/3MF, avatar utenti, ecc.
- Accesso privato: i file vengono serviti via URL firmati temporanei

### Redis
**Cosa fa**: broker di messaggi (in-memory) tra Django e Celery.

**In dettaglio**:
- Container Docker locale all'EC2, non esposto pubblicamente
- Quando Django deve eseguire un task lungo (es. validazione STL al momento
  della pubblicazione), lo "appoggia" su Redis e Celery lo prende e lo esegue
  in background

### Google Cloud (OAuth)
**Cosa fa**: identity provider per il login con Google.

**In dettaglio**:
- Progetto Google Cloud `opendrone-495409`
- OAuth Client ID `805523359996-...apps.googleusercontent.com` (web app)
- Autorizzato per le origin: `https://open-drone-virid.vercel.app` e
  `http://localhost:5173`
- App in modalità **Production**: chiunque con un account Google può loggarsi
- Nessun costo, nessun limite

---

## Modalità di autenticazione

OpenDrone supporta **due modi** per accedere:

### 1. Email + Password (classico)

**Registrazione**:
1. Pagina `/register`, step 1: l'utente sceglie il ruolo (Cliente, Designer,
   Nodo stampa, Assemblaggio)
2. Step 2: compila email, nome, cognome, password (min. 8 caratteri)
3. Backend `POST /api/auth/register/` crea l'utente, gli applica il ruolo
   scelto e gli rilascia un JWT (access + refresh)

**Login**:
1. Pagina `/login`, inserisce email + password
2. Backend `POST /api/auth/login/` autentica e rilascia un JWT
3. Il token viene salvato in `localStorage`, ogni richiesta API successiva
   passa nell'header `Authorization: Bearer <token>`

**Quando usare**: utenti che preferiscono credenziali separate o non hanno un
account Google. Anche **i superuser** usano questa modalità.

### 2. Login con Google (OAuth)

**Registrazione/Login** (è lo stesso bottone):
1. Pagina `/login` o `/register` step 2 → bottone "Continue with Google"
2. Si apre il popup di Google: l'utente conferma con il suo account
3. Google restituisce un **id_token** firmato al frontend
4. Il frontend lo invia a `POST /api/auth/google/` (con il `role` se siamo in
   registrazione)
5. Il backend verifica la firma del token con la libreria `google-auth` e
   l'env `GOOGLE_OAUTH_CLIENT_ID`
6. Se l'email esiste già nel database → login (rilascia JWT)
7. Se l'email non esiste → registra l'utente nuovo con `is_verified=True`,
   `set_unusable_password()` e il ruolo scelto

**Quando usare**: ogni utente normale. È più veloce, non c'è password da
ricordare, l'email è verificata automaticamente.

**Limitazione**: gli utenti creati via Google **non possono fare login con
email/password** (la password è "unusable"). Questo è voluto.

### Riassunto

| Modalità | Quando usarla | Password |
|---|---|---|
| Email + Password | Superuser, utenti che la preferiscono | da ricordare |
| Google | Tutti gli altri | gestita da Google |

---

## Ruoli utente

Un utente può avere uno o più ruoli (campo JSON `roles`). I ruoli disponibili:

| Ruolo | Cosa fa |
|---|---|
| `customer` | Sfoglia il marketplace, ordina droni. Default per ogni nuovo iscritto. |
| `designer` | Pubblica progetti drone (STL, BOM, schemi). Riceve royalty sugli ordini. |
| `print_node` | Stampa pezzi 3D di drone. Riceve ordini di stampa automatici. |
| `assembly_center` | Assembla i droni stampati + componenti. Riceve ordini di assemblaggio. |
| `admin` | Approva progetti, gestisce utenti, certifica nodi. Ha accesso a `/admin/*`. |

Un utente è sempre `customer` (anche se è anche designer, può comprare droni).

I ruoli `print_node` e `assembly_center` sono inattivi finché un admin non
**certifica** il loro profilo (vedi sotto).

### Superuser

Un **superuser** è un utente con `is_staff=True` E `is_superuser=True` E
`roles=['admin']`. È creato lanciando sull'EC2:

```bash
ssh -i "..." ubuntu@16.170.111.228 -t "sudo docker compose -f /home/ubuntu/OpenDrone/opendrone/docker-compose.prod.yml exec backend python manage.py createsuperuser"
```

Email + password vengono inserite interattivamente. Il superuser ha accesso a
tutto (frontend `/admin/*` e Django admin `/api/admin/`).

---

## Guida utente finale

### Mi voglio iscrivere

1. Apri https://open-drone-virid.vercel.app
2. Click in alto a destra **Registrati**
3. **Step 1**: scegli che tipo di utente vuoi essere:
   - **Cliente** se vuoi comprare droni
   - **Designer** se vuoi pubblicare progetti
   - **Nodo stampa** se vuoi stampare pezzi
   - **Assemblaggio** se vuoi montare droni
4. **Step 2**: registrati con uno dei due metodi:
   - **Continue with Google** (consigliato, veloce)
   - oppure compila email/password
5. Sei dentro

### Voglio comprare un drone (cliente)

1. Login → ti porta su `/dashboard`
2. Vai su **Catalogo** dalla nav o `/projects`
3. Filtra per categoria (Racing FPV, Cinematic, ecc.) e/o difficoltà
4. Clicca su un progetto → vedi descrizione, BOM (lista componenti), cover, file
5. Premi **Ordina** → checkout
6. Riceverai aggiornamenti via email (stato dell'ordine: in stampa, in
   assemblaggio, spedito)

### Voglio pubblicare un progetto (designer)

⚠ Devi essere registrato come `designer` (lo scegli in step 1 della registrazione).

1. Login → in nav vedi **Carica progetto**
2. Compila in 3 step:
   - **Step 1 / Base**: titolo, descrizione, **categoria** (puoi sceglierne
     una tra le 14 standard oppure crearne una nuova al volo con "+ Nuova
     categoria"), difficoltà, peso/autonomia/payload, licenza (Open Source
     gratis, Open + Royalty, o Premium)
   - **Step 2 / Componenti**: lista BOM organizzata per categoria (frame,
     motori, ESC, FC, ricevitore, batteria, eliche, ecc.). Marca categorie
     "essenziali" obbligatorie per un drone funzionante
   - **Step 3 / File**: copertina (foto/render), STL, schemi, guida assemblaggio
3. Premi **Pubblica** → il progetto va in `pending_validation`
4. L'admin lo approva (di solito entro 24h) → diventa **published**
5. Ricevi royalty su ogni ordine

### Voglio stampare pezzi (print_node)

⚠ Devi essere registrato come `print_node` E **certificato** dall'admin.

1. Registrati come `print_node`
2. Compila il profilo: nome attività, indirizzo, città, materiali stampabili,
   capacità giornaliera, prezzo/grammo
3. Aspetta che l'admin ti certifichi (verifica documenti/qualità)
4. Una volta certificato, il sistema ti assegnerà ordini di stampa in
   automatico, in base a vicinanza e capacità
5. Vedi gli ordini su `/orders`

### Ho dimenticato la password

Funzione attualmente **non implementata** lato frontend. Se hai problemi
contatta un admin per il reset manuale tramite Django shell. Se invece ti sei
registrato con Google, semplicemente premi "Continue with Google" — non hai
una password da ricordare.

---

## Guida gestore (admin)

### Come accedere

1. Devi avere un superuser creato (vedi [Ruoli utente / Superuser](#ruoli-utente))
2. https://open-drone-virid.vercel.app/login → **email + password** del
   superuser
3. Vieni reindirizzato automaticamente su `/admin`

### Dashboard `/admin`

Panoramica generale: utenti totali, progetti, ordini, ecc. (al momento è
informativa).

### `/admin/projects` — moderazione progetti

Qui approvi i progetti caricati dai designer.

**Filtri rapidi** in alto:
- **In attesa**: progetti `pending_validation` o `pending_review` (default)
- **Tutti**: tutti i progetti
- **Pubblicati**, **Rifiutati**, **Bozze**, **Sospesi**

**Per ogni progetto** vedi:
- Cover, titolo, descrizione, designer, categoria, difficoltà, costo BOM, data
- Pulsanti:
  - **Vedi**: apre la pagina pubblica del progetto
  - **✓ Approva**: pubblica subito
  - **✕ Rifiuta**: chiede una motivazione, poi imposta status `rejected`
    (la motivazione viene aggiunta al campo `compliance_notes` del progetto)

**Workflow tipico**: filtri "In attesa" → apri il progetto in una nuova tab →
verifichi che abbia STL, BOM completa, descrizione decente, niente categorie
EASA problematiche → torni e approvi (o rifiuti spiegando il motivo).

### `/admin/users` — gestione utenti

Qui gestisci tutti gli iscritti.

**Filtri rapidi**: tutti / designer / nodi stampa / assemblaggio / clienti /
admin.

**Ricerca testuale**: input "Cerca per nome, cognome o email" che filtra in
tempo reale gli utenti già caricati.

**Per ogni utente** vedi: avatar (iniziali), nome, email, ruoli, stato
(attivo/disattivo).

**Azioni**:
- **★ Certifica / Annulla certifica** (solo per `print_node` e
  `assembly_center`): il flag `is_certified=True` è obbligatorio perché un
  nodo o centro riceva ordini. Senza certificazione il loro profilo è
  invisibile al sistema di assegnazione automatica
- **Disattiva / Attiva**: blocca/sblocca il login dell'utente. Non puoi
  disattivare te stesso

> **Designer**: non si certificano per persona — la qualità è filtrata
> per-progetto in `/admin/projects`. Quindi nelle card designer non vedi la
> stellina.

### `/admin/orders` — moderazione ordini

(In sviluppo) Gestione e tracciamento ordini.

### Differenza: `is_active` vs `is_certified`

| Flag | Effetto |
|---|---|
| `is_active=False` | l'utente NON può loggarsi (account sospeso) |
| `is_certified=False` | l'utente accede normalmente, ma il suo profilo (nodo stampa o centro assemblaggio) è "in standby": non riceve ordini, non appare nelle ricerche pubbliche |

### Workflow di certificazione di un nodo stampa

1. Mario si registra come `print_node`, compila il profilo (indirizzo,
   materiali, capacità, prezzo)
2. Mario è iscritto e logga, ma nessuno vede il suo nodo
3. Tu in `/admin/users` filtri **Nodi stampa**, trovi Mario
4. Verifichi documenti / qualità (al di fuori della piattaforma)
5. Click **★ Certifica** → da quel momento Mario è nel pool produttivo, il
   sistema gli assegna ordini in base a vicinanza e capacità

---

## FAQ e troubleshooting

### Il sito non risponde / dà 502 Bad Gateway

Cause possibili:
- Container backend EC2 giù → SSH all'EC2 e `sudo docker compose -f
  /home/ubuntu/OpenDrone/opendrone/docker-compose.prod.yml ps`. Se backend è
  giù: `docker compose ... up -d backend`
- EC2 stessa giù → AWS Console, controlla stato istanza (deve essere
  `Running`)
- IP cambiato → controlla che `vercel.json` abbia ancora `16.170.111.228`. Se
  hai fatto Stop+Start senza Elastic IP avresti perso l'IP, ma con l'Elastic
  attuale non dovrebbe più capitare

### Pagina /login dà 404

`vercel.json` non ha più la rewrite `/(*)` → `/index.html`. Verifica.

### Il bottone "Continue with Google" dà `invalid_client`

L'origin del browser non è nelle Authorized JavaScript origins su Google
Cloud Console. Vai su
https://console.cloud.google.com/apis/credentials?project=opendrone-495409 e
verifica:

```
https://open-drone-virid.vercel.app   ← senza slash finale
http://localhost:5173                  ← per sviluppo locale
```

Niente altro. Se ci sono URI vuoti o non validi il save fallisce silenziosamente.

### Gli utenti registrati con Google non riescono a fare login con password

Voluto: il backend crea utenti Google con `set_unusable_password()`. Devono
sempre usare il bottone "Continue with Google".

### SSH all'EC2 dà timeout durante banner exchange

Probabili cause:
1. **EC2 satura di RAM**: ora c'è 2 GB di swap, quindi non dovrebbe più
   succedere. Se accade: AWS Console → Reboot dell'istanza (NON Stop+Start)
2. **Security group non accetta il tuo IP**: il tuo IP residenziale può
   cambiare. Bypassa con **EC2 Instance Connect** dalla AWS Console (apre una
   shell nel browser senza chiave SSH)

### Vercel non aggiorna dopo un push

Verifica https://vercel.com/diska95s-projects/open-drone/deployments:
- Se ultimo deploy è "Stale" o "Queued" da troppo tempo → click sul deploy
  → "Redeploy" deselezionando "Use existing Build Cache"
- Se "Current Ready" è recente ma vedi ancora il vecchio sito → cache
  browser, fai Ctrl+Shift+R

### Voglio fare un nuovo deploy dopo aver modificato il backend

Sull'EC2 (o via SSH):
```bash
cd /home/ubuntu/OpenDrone
git pull --ff-only
cd opendrone
sudo docker compose -f docker-compose.prod.yml build backend
sudo docker compose -f docker-compose.prod.yml up -d --force-recreate backend
```

Le migration vengono applicate al boot del container (`migrate --noinput` è
nel command).

### Voglio aggiungere una nuova env var sul backend

1. SSH all'EC2 → `nano /home/ubuntu/OpenDrone/opendrone/backend/.env`
2. Aggiungi la riga `NUOVA_VAR=valore`
3. `sudo docker compose -f docker-compose.prod.yml up -d --force-recreate backend`
   (le env vengono lette al boot del container)

### Voglio aggiungere una nuova env var sul frontend

1. https://vercel.com/diska95s-projects/open-drone/settings/environment-variables
2. Add new (Production + Preview + Development)
3. Vai su Deployments → ultimo deploy → ⋯ → Redeploy
   (Vercel inietta le env al **build time**, non a runtime)

---

*Manutenzione: questo manuale va aggiornato quando si toccano i flussi
critici (auth, deploy, gestione admin).*
