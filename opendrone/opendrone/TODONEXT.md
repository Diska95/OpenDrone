# OpenDrone — TODO Next

Cose da implementare in ordine di priorità.
Aggiornato da Claude AI al termine di ogni sessione di lavoro.

---

## 🔴 PRIORITÀ ALTA

### 1. Checkout frontend — integrazione Stripe.js
- Collegare `Checkout.vue` a Stripe.js per il pagamento reale
- Gestire `client_secret` restituito dal backend
- Mostrare form carta di credito con Stripe Elements
- Gestire successo/fallimento pagamento e redirect

### 2. Stripe Connect onboarding
- Endpoint backend per generare link onboarding Stripe Connect
- UI nella dashboard per designer/nodi/centri per collegare il proprio account Stripe
- Gestione callback dopo onboarding completato
- Mostrare stato account Stripe (collegato / non collegato)

### 3. Navbar globale con stato auth
- `App.vue` — navbar con link corretti in base al ruolo
- Mostrare nome utente e avatar se loggato
- Bottone logout funzionante
- Menu mobile responsive

---

## 🟡 PRIORITÀ MEDIA

### 4. Notifiche email collegate agli eventi
- Ordine confermato → email a customer e nodo stampa
- Progetto approvato/rifiutato → email al designer
- Ordine spedito → email a customer con tracking
- Collegare `apps/notifications/emails.py` agli eventi reali

### 5. Home.vue con dati reali dall'API
- Caricare progetti in evidenza (`is_featured=true`) dal backend
- Mostrare statistiche reali (numero progetti, designer, ordini)
- Sezione "ultimi progetti" con chiamata API

### 6. .gitignore — verifica sicurezza
- Assicurarsi che `.env` e `.env.production` non finiscano su GitHub
- Verificare che `media/`, `staticfiles/`, `node_modules/` siano esclusi

---

## 🟢 PRIORITÀ BASSA

### 7. Test
- Test unitari backend (pytest-django) per auth, marketplace, pricing
- Test integration per il flusso ordine completo
- Test frontend (Vitest) per i componenti principali

### 8. Dominio
- Acquistare dominio (consiglio: Cloudflare Registrar)
- Configurare DNS verso EC2 (backend) e Vercel (frontend)
- Aggiornare `ALLOWED_HOSTS`, `CORS_ORIGINS`, `CSRF_TRUSTED_ORIGINS` in `.env.production`

### 9. AWS — provisioning risorse
- Creare EC2 t3.micro (Ubuntu 24.04)
- Creare RDS PostgreSQL t3.micro
- Creare bucket S3 `opendrone-files`
- Creare utente IAM con policy S3 + SES
- Verificare dominio su SES per invio email

---

## ✅ COMPLETATO

- [x] Auth completa (login, register, JWT, ruoli, profili)
- [x] Marketplace backend (progetti, BOM, file, recensioni, validazione, approvazione)
- [x] Marketplace frontend (lista, dettaglio, crea/modifica, i miei progetti)
- [x] Ordini backend (creazione, pricing, assegnazione nodo, stati, dispute)
- [x] Pagamenti backend (Stripe webhook, trasferimenti, royalty)
- [x] Dashboard per tutti i ruoli
- [x] Admin panel (utenti, progetti, ordini)
- [x] Router con guard per ruoli
- [x] Configurazione produzione AWS (settings, docker-compose.prod, nginx)
- [x] DEPLOY.md — guida step-by-step
- [x] Rename PolyDrone → OpenDrone in tutti i file
- [x] CHANGELOG.md
