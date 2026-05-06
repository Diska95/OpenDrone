# Informativa sulla Privacy

> ⚠️ **BOZZA TECNICA — NON PUBBLICARE COSÌ COM'È**
> Questa è una bozza redatta in fase di audit. **Va validata da un avvocato/DPO** prima della pubblicazione. I placeholder `[...]` vanno compilati con i dati reali della società titolare.

**Ultimo aggiornamento:** [DATA_PUBBLICAZIONE]
**Versione:** 1.0

---

## 1. Titolare del trattamento

Il Titolare del trattamento dei dati personali è:

**[DENOMINAZIONE SOCIETÀ]**
Sede legale: [SEDE_LEGALE]
P.IVA / C.F.: [P.IVA]
Email: [EMAIL_PRIVACY]
PEC: [PEC]
Legale rappresentante: [NOME_LEGALE_RAPPRESENTANTE]

Per qualsiasi questione relativa al trattamento dei tuoi dati personali puoi scrivere a **[EMAIL_PRIVACY]**.

> Nota: al momento il Titolare **non ha nominato un Responsabile della Protezione dei Dati (DPO)** in quanto non ricorrono i presupposti dell'art. 37 GDPR. Il DPO sarà nominato qualora i trattamenti raggiungano la scala prevista dalla normativa.

## 2. Cosa è OpenDrone

OpenDrone è un marketplace open hardware che mette in contatto:
- **Designer** che pubblicano progetti di droni open source o con royalty
- **Nodi di stampa 3D** che producono i componenti su ordine
- **Centri di assemblaggio** che montano e collaudano i droni
- **Clienti** che acquistano droni in kit o assemblati

Per offrire questo servizio trattiamo dati personali di tutte le categorie sopra elencate.

## 3. Quali dati raccogliamo e perché

### 3.1 Dati di registrazione (obbligatori)
| Dato | Finalità | Base giuridica | Conservazione |
|------|----------|----------------|---------------|
| Email, nome, cognome | Creazione account, autenticazione, comunicazioni di servizio | Esecuzione contratto (art. 6.1.b GDPR) | Per la durata dell'account + 24 mesi inattività |
| Password (cifrata con PBKDF2) | Autenticazione | Esecuzione contratto | Idem |
| Ruolo (cliente/designer/nodo stampa/centro assemblaggio) | Configurazione funzionalità | Esecuzione contratto | Idem |

### 3.2 Dati profilo (facoltativi)
| Dato | Finalità | Base giuridica | Conservazione |
|------|----------|----------------|---------------|
| Bio, avatar | Personalizzazione profilo | Consenso (art. 6.1.a) | Fino a richiesta cancellazione |
| Portfolio URL (designer) | Visibilità professionale | Consenso | Idem |

### 3.3 Dati professionali (per nodi stampa e centri assemblaggio)
| Dato | Finalità | Base giuridica | Conservazione |
|------|----------|----------------|---------------|
| Ragione sociale, indirizzo, città, provincia | Fatturazione, geolocalizzazione assegnazione ordini | Esecuzione contratto + obbligo legale fiscale | 10 anni (CC art. 2220) |
| Latitudine/longitudine | Matching ordini per distanza | Esecuzione contratto | Per la durata dell'account |
| Materiali, capacità oraria, prezzi | Funzionamento marketplace | Esecuzione contratto | Idem |

### 3.4 Dati di pagamento e fatturazione
| Dato | Finalità | Base giuridica | Conservazione |
|------|----------|----------------|---------------|
| ID account Stripe (`stripe_account_id`, `stripe_customer_id`) | Trasferimenti automatici, abbonamenti | Esecuzione contratto + obbligo legale | 10 anni |
| Importi royalty / commissioni / fatture | Contabilità e fiscale | Obbligo legale | 10 anni |

> **Nota importante:** OpenDrone **non memorizza dati di carta di credito**. Il pagamento avviene direttamente su infrastruttura **Stripe Inc.** che è certificata PCI-DSS Level 1. Vedi sezione 6 sui sub-responsabili.

### 3.5 Dati di ordine e spedizione
| Dato | Finalità | Base giuridica | Conservazione |
|------|----------|----------------|---------------|
| Indirizzo di spedizione, latitudine/longitudine | Consegna ordini | Esecuzione contratto | 10 anni (per esigenze post-vendita e contabili) |
| Numero tracking, corriere | Tracciamento spedizione | Esecuzione contratto | 24 mesi post-consegna |

### 3.6 File caricati
| Dato | Finalità | Base giuridica | Conservazione |
|------|----------|----------------|---------------|
| File STL, BOM, schemi, immagini, video di progetti | Pubblicazione marketplace | Consenso (caricamento volontario) | Fino a cancellazione del progetto o dell'account |
| Foto di build per recensioni | Recensioni pubbliche | Consenso | Idem |

> **Avvertenza:** se i tuoi file caricati contengono dati personali di terzi (es. foto di persone identificabili), è tua responsabilità avere ottenuto il loro consenso prima di pubblicarli.

### 3.7 Dati di navigazione e tecnici
- Indirizzo IP (loggato dai server per sicurezza, conservato 12 mesi).
- User-agent.
- Token di autenticazione (memorizzati nel browser per mantenerti loggato).

Vedi anche la **Cookie Policy** dedicata.

## 4. Come trattiamo i dati

### 4.1 Modalità
I dati sono trattati con strumenti elettronici (server, database) con misure di sicurezza tecniche e organizzative ex art. 32 GDPR:
- Database PostgreSQL con cifratura in transito (`sslmode=require`).
- Storage file su Amazon S3 con permessi privati (no public read).
- Password cifrate con PBKDF2-SHA256.
- Sessione autenticata con token JWT a scadenza breve.
- Audit log per le operazioni amministrative.

### 4.2 Decisioni automatizzate (art. 22 GDPR)
- L'**assegnazione automatica del nodo di stampa** all'ordine è basata su distanza geografica e capacità disponibile. Non produce effetti legali sull'interessato.
- Il **rating** di designer e nodi è calcolato come media delle recensioni utenti. Non è una decisione automatizzata né profilazione ai sensi dell'art. 22.

## 5. Con chi condividiamo i dati

Condividiamo i tuoi dati solo con i seguenti soggetti, nei limiti strettamente necessari:

### 5.1 All'interno della piattaforma
- **Tu vedi tu stesso**: tutti i tuoi dati di profilo e ordini.
- **Designer pubblico**: il tuo first_name/cognome (o alias scelto), avatar e bio sono visibili agli utenti che visitano i tuoi progetti.
- **Recensioni**: il tuo nome (o alias) e il commento sono visibili pubblicamente sotto il progetto recensito.
- **Nodo di stampa / centro assemblaggio**: ricevono il tuo indirizzo di spedizione per evadere l'ordine.
- **Cliente**: vede il nome commerciale e città del nodo/centro assegnato al suo ordine.
- **Admin OpenDrone**: vedono tutti i dati per gestione operativa, supporto, prevenzione frodi.

### 5.2 Sub-responsabili esterni (art. 28 GDPR)
Vedi documento dedicato `sub_responsabili.md` per la lista completa con DPA stipulati. In sintesi:
- **Amazon Web Services (AWS)** — hosting EU (Stoccolma + Milano), email transazionali (SES).
- **Vercel Inc.** — hosting frontend.
- **Stripe Inc.** — pagamenti, abbonamenti, payout.
- **Google LLC** — login federato (Google Sign-In) per chi sceglie questa modalità.

### 5.3 Trasferimenti extra-UE
Alcuni sub-responsabili (Stripe, Google, eventualmente AWS account-level) hanno sede negli Stati Uniti. I trasferimenti sono garantiti da:
- **Data Privacy Framework (DPF)** UE-USA per Stripe, Google, AWS.
- **Clausole Contrattuali Standard (SCC)** della Commissione UE come backup.

Puoi richiedere copia delle garanzie scrivendo a [EMAIL_PRIVACY].

## 6. I tuoi diritti (art. 15-22 GDPR)

Hai il diritto di:
- **Accesso** (art. 15): conoscere quali tuoi dati trattiamo e ottenerne copia.
  → Endpoint `Profilo > Privacy > Scarica i miei dati` (export JSON).
- **Rettifica** (art. 16): correggere dati inesatti.
  → Sezione `Profilo`.
- **Cancellazione** (art. 17): chiedere la cancellazione del tuo account e dei dati associati.
  → Sezione `Profilo > Privacy > Cancella account`. Alcuni dati (ordini, fatture, royalty) sono conservati in forma pseudonimizzata per obblighi contabili (10 anni).
- **Limitazione del trattamento** (art. 18): chiedere la sospensione di trattamenti specifici.
  → Scrivi a [EMAIL_PRIVACY].
- **Portabilità** (art. 20): ricevere i tuoi dati in formato strutturato (JSON).
  → Stesso endpoint dell'accesso.
- **Opposizione** (art. 21): opporti a trattamenti basati su legittimo interesse o marketing.
  → Scrivi a [EMAIL_PRIVACY] o usa l'apposito opt-out.
- **Revoca del consenso** (art. 7.3): per i trattamenti basati sul consenso, puoi revocarlo in qualunque momento.
  → Sezione `Profilo > Privacy > Consensi`.
- **Reclamo al Garante** (art. 77): se ritieni che il trattamento violi la normativa, puoi proporre reclamo al **Garante per la Protezione dei Dati Personali** (https://www.gpdp.it/) o all'autorità competente del tuo Stato membro.

## 7. Per quanto tempo conserviamo i dati

Vedi la tabella in §3 e il documento dedicato `data_retention.md`. In sintesi:
- **Account attivo**: fino a richiesta cancellazione.
- **Account inattivo (>24 mesi)**: warning email, poi cancellazione dopo 6 mesi.
- **Ordini e fatture**: 10 anni (obbligo civilistico/fiscale).
- **Token autenticazione blacklisted**: 30 giorni.
- **Log accesso**: 12 mesi.

## 8. Sicurezza

Adottiamo misure tecniche e organizzative adeguate al rischio (art. 32 GDPR). Vedi documento interno `data_breach_procedura.md` per la procedura in caso di violazione. In caso di **data breach con rischio elevato per i tuoi diritti**, sarai informato senza ingiustificato ritardo via email registrata.

## 9. Modifiche a questa informativa

Pubblicheremo eventuali modifiche sostanziali su questa pagina e ti chiederemo di accettare la nuova versione al successivo accesso. Le modifiche minori (correzioni tipografiche, riformulazioni) saranno indicate solo dalla data di aggiornamento in cima.

## 10. Reclami

Per qualsiasi reclamo o richiesta scrivi a **[EMAIL_PRIVACY]** o alla PEC **[PEC]**. Risponderemo entro 30 giorni (prorogabili a 60 in casi complessi).

In alternativa puoi rivolgerti direttamente al Garante:
**Garante per la Protezione dei Dati Personali**
Piazza Venezia 11 - 00187 Roma
www.gpdp.it
