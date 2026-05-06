# Registro dei trattamenti — art. 30 GDPR

> ⚠️ **DOCUMENTO INTERNO — NON PUBBLICARE SUL SITO**
> Va tenuto aggiornato a cura del Titolare e mostrato al Garante in caso di ispezione. Compila i placeholder.

**Ultima revisione:** [DATA_REVISIONE]
**Revisore:** [NOME_RESPONSABILE_PRIVACY]
**Frequenza minima di revisione:** annuale o ad ogni modifica sostanziale.

---

## 0. Identificazione del Titolare

| Voce | Valore |
|------|--------|
| Denominazione | [DENOMINAZIONE SOCIETÀ] |
| Forma giuridica | [SRL / SRLS / SPA / DITTA INDIVIDUALE] |
| Sede legale | [SEDE_LEGALE] |
| P.IVA / C.F. | [P.IVA] |
| Legale rappresentante | [NOME_LEGALE_RAPPRESENTANTE] |
| Contatto privacy | [EMAIL_PRIVACY] / [PEC] |
| DPO nominato? | No (non ricorrono i presupposti art. 37) |

---

## 1. Trattamento: Gestione account utenti

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Creazione e gestione account, autenticazione, profilazione di base (ruolo) |
| **Base giuridica** | Esecuzione contratto (art. 6.1.b) |
| **Categorie di interessati** | Utenti registrati (Cliente, Designer, Nodo stampa, Centro assemblaggio, Admin) |
| **Categorie di dati** | Identificativi (email, nome, cognome), credenziali (password hash), bio, avatar, ruoli |
| **Categorie particolari** | Nessuna |
| **Destinatari** | Personale autorizzato OpenDrone, AWS (hosting RDS+S3), Google (se login federato) |
| **Trasferimenti extra-UE** | Sì, USA (Google) — DPF + SCC |
| **Termini di conservazione** | Per la durata dell'account + 24 mesi inattività; cancellazione su richiesta (con eccezioni contabili) |
| **Misure di sicurezza** | Cifratura DB in transito, password PBKDF2, JWT a scadenza breve, rate limit, log accesso |

## 2. Trattamento: Profili professionali (Print Node, Assembly Center)

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Matching ordini, fatturazione, geolocalizzazione |
| **Base giuridica** | Esecuzione contratto + obbligo legale (fattura) |
| **Categorie di interessati** | Titolari di nodi di stampa e centri di assemblaggio (persone fisiche con P.IVA o ditte) |
| **Categorie di dati** | Ragione sociale, indirizzo, città, provincia, latitudine/longitudine, materiali, capacità, prezzi |
| **Destinatari** | Personale autorizzato, AWS, Stripe (per payout), Clienti che ordinano dal nodo (vedono nome e città) |
| **Trasferimenti extra-UE** | Sì, USA (Stripe) — DPF + SCC |
| **Conservazione** | Account: come §1. Dati fiscali: 10 anni (CC art. 2220) |
| **Sicurezza** | Come §1 + S3 ACL private |

## 3. Trattamento: Pubblicazione progetti

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Visibilità marketplace, generazione catalogo, validazione tecnica, pubblicazione recensioni |
| **Base giuridica** | Consenso (caricamento volontario) + esecuzione contratto |
| **Categorie di interessati** | Designer; eventuali persone identificabili nelle foto build delle recensioni |
| **Categorie di dati** | Titolo, descrizione, file STL/BOM/immagini/video, nome+cognome (o alias) reviewer |
| **Destinatari** | Pubblico (visitatori del sito), AWS S3, Nodi/Centri assegnati agli ordini |
| **Trasferimenti extra-UE** | No (S3 in EU `eu-south-1`) |
| **Conservazione** | Fino a richiesta cancellazione del progetto/account; recensioni pseudonimizzate alla cancellazione account |
| **Sicurezza** | S3 ACL private, presigned URL, validazione MIME upload, scan AV (in roadmap) |

## 4. Trattamento: Ordini e spedizioni

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Gestione ordine, calcolo prezzo, assegnazione nodo, spedizione, dispute |
| **Base giuridica** | Esecuzione contratto + obbligo legale (registri contabili) |
| **Categorie di interessati** | Clienti |
| **Categorie di dati** | Indirizzo spedizione (street, city, lat/lon), tracking, importi, status |
| **Destinatari** | Personale autorizzato, Nodo/Centro assegnato (ricevono indirizzo per consegna), corriere (riceve indirizzo per spedizione), Stripe (per pagamento), AWS |
| **Trasferimenti extra-UE** | USA (Stripe) — DPF + SCC |
| **Conservazione** | 10 anni (obbligo civilistico/fiscale per ordini conclusi) |
| **Sicurezza** | DB cifrato in transito, validazione dati, audit log status (da implementare) |

## 5. Trattamento: Pagamenti e payout

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Incasso pagamenti dai clienti, payout a designer/nodi/centri, gestione abbonamenti |
| **Base giuridica** | Esecuzione contratto + obbligo legale (antiriciclaggio, fattura) |
| **Categorie di interessati** | Clienti, designer, nodi, centri |
| **Categorie di dati** | ID account Stripe, ID customer Stripe, importi, royalty, transfer ID |
| **Destinatari** | Personale autorizzato, **Stripe Inc.** (responsabile esterno) |
| **Trasferimenti extra-UE** | USA (Stripe) — DPF + SCC. Dati sensibili pagamento (PAN, CVV) **non transitano mai** sui server OpenDrone (Stripe.js diretto) |
| **Conservazione** | Lato OpenDrone: 10 anni per registri contabili. Lato Stripe: secondo loro retention (vedi DPA Stripe) |
| **Sicurezza** | Webhook con signature mandatory, JWT auth lato API, cifratura in transito |

## 6. Trattamento: Comunicazioni transazionali (email)

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Notifiche operative (ordine confermato, spedito, password reset, ecc.) |
| **Base giuridica** | Esecuzione contratto |
| **Categorie di interessati** | Tutti gli utenti registrati |
| **Categorie di dati** | Email, contenuto messaggio (può includere nome ordine, importo, link tracking) |
| **Destinatari** | **Amazon SES** (responsabile esterno) |
| **Trasferimenti extra-UE** | No (SES `eu-south-1`) |
| **Conservazione** | Log invio: 12 mesi su SES; contenuto: nessuna copia OpenDrone |
| **Sicurezza** | TLS SES, SPF/DKIM/DMARC (da configurare al go-live dominio) |

## 7. Trattamento: Notifiche in-app

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Comunicazione eventi piattaforma all'utente loggato |
| **Base giuridica** | Esecuzione contratto |
| **Interessati** | Utenti registrati |
| **Dati** | Email destinatario (FK), titolo, message (può includere PII), link |
| **Destinatari** | Solo l'utente |
| **Trasferimenti extra-UE** | No |
| **Conservazione** | Lette: 6 mesi. Non lette: 12 mesi |
| **Sicurezza** | Auth obbligatoria, queryset filtra per `user=request.user` |

## 8. Trattamento: Log tecnici e di sicurezza

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Monitoraggio sicurezza, debugging, prevenzione abuso |
| **Base giuridica** | Legittimo interesse (art. 6.1.f) — sicurezza infrastruttura |
| **Interessati** | Tutti i visitatori (anche non registrati) |
| **Dati** | Indirizzo IP, user-agent, URL richiesto, timestamp, codice risposta |
| **Destinatari** | Personale tecnico autorizzato |
| **Conservazione** | 12 mesi (rotazione automatica `logrotate`) |
| **Sicurezza** | Accesso SSH ristretto a IP autorizzati, log su filesystem locale EC2 |

## 9. Trattamento: Audit log azioni amministrative (in roadmap)

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Tracciabilità azioni admin (approvazione progetti, certificazione utenti, archiviazione, ecc.) |
| **Base giuridica** | Legittimo interesse + compliance |
| **Interessati** | Admin (operanti) e utenti oggetto delle azioni |
| **Dati** | Admin user, action, target, payload, timestamp |
| **Conservazione** | 5 anni |
| **Sicurezza** | Append-only (no update/delete da app) |

## 10. Trattamento: Consensi (GDPR + cookie)

| Voce | Dettaglio |
|------|-----------|
| **Finalità** | Prova del consenso ex art. 7.1 |
| **Base giuridica** | Obbligo legale (art. 7 GDPR) |
| **Interessati** | Tutti gli utenti registrati e visitatori (cookie) |
| **Dati** | Tipo consenso, versione testo, timestamp, IP, user-agent, scelta |
| **Destinatari** | Personale autorizzato, eventuale Garante in caso di ispezione |
| **Conservazione** | Per la durata del rapporto + 5 anni (anche post-cancellazione account come prova storica) |

---

## Misure organizzative trasversali

| Misura | Stato |
|--------|-------|
| Designazione del Titolare per iscritto | ⏳ Da formalizzare alla costituzione società |
| Lettera incarico a Responsabili interni (sviluppatori) | ⏳ Da redigere |
| DPA con sub-responsabili (AWS, Stripe, Google, Vercel) | ⏳ Da firmare/accettare formalmente |
| Procedura data breach | ✓ Bozza in `procedura_data_breach.md` |
| Formazione privacy del personale | ⏳ Da fare al primo onboarding |
| Test ripristino backup RDS | ⏳ Da pianificare |
| Pentest esterno | ⏳ Pre go-live |

---

## Storico revisioni

| Data | Modifica | Revisore |
|------|----------|----------|
| [DATA_REVISIONE_1] | Stesura iniziale | [NOME] |
