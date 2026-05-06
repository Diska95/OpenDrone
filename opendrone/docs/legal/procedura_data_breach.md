# Procedura interna in caso di Data Breach

> ⚠️ **DOCUMENTO INTERNO — VINCOLANTE PER IL TEAM**
> Procedura operativa ai sensi degli art. 33 e 34 GDPR. Revisione almeno annuale.

**Versione:** 1.0
**Data:** [DATA_REDAZIONE]

---

## 1. Cosa è un Data Breach (art. 4.12 GDPR)

Una "violazione dei dati personali" è qualsiasi violazione della sicurezza che comporti **accidentalmente o in modo illecito**:
- la **distruzione** o la perdita di dati personali
- la **modifica** non autorizzata
- la **divulgazione** non autorizzata o l'**accesso** non autorizzato
ai dati personali trasmessi, conservati o trattati.

Esempi concreti per OpenDrone:
- Compromissione di un account admin → accesso non autorizzato a tutti i dati utenti.
- Bug che espone via API dati di utente a un altro utente.
- Furto di un device con credenziali di accesso ai sistemi.
- Email transazionale inviata al destinatario sbagliato (PII leak).
- Accesso non autorizzato al bucket S3 (file utente esposti).
- Compromissione di un sub-responsabile (notifica da loro).
- Ransomware su server.
- Pubblicazione accidentale su GitHub di credenziali / dati personali.

## 2. Soglie di notifica

| Scenario | Notifica al Garante (entro 72h) | Comunicazione agli interessati |
|----------|--------------------------------|--------------------------------|
| Breach con rischi probabili per diritti e libertà | **SÌ** | Solo se rischio **elevato** (art. 34) |
| Breach senza rischi (es. dati pseudonimizzati senza chiave) | **NO** ma annotare nel registro interno | NO |
| Breach in cui il rischio elevato è **mitigato** (es. dati cifrati e chiave non compromessa) | SÌ al Garante, NO agli interessati | NO se misure adeguate |

## 3. Ruoli

| Ruolo | Chi | Responsabilità |
|-------|-----|----------------|
| **Rilevatore** | Dev, Admin, fornitore esterno, utente, autorità | Segnala il breach |
| **Incident Manager** | [NOME_RESPONSABILE_PRIVACY] o [LEGALE_RAPPRESENTANTE] | Gestisce il workflow, decide notifiche |
| **Tech Lead** | [NOME_DEV_LEAD] | Contiene tecnicamente il breach, raccoglie evidence |
| **Legale** | Avvocato esterno | Valida la decisione di notifica e i testi |
| **Comunicazione** | [LEGALE_RAPPRESENTANTE] | Notifica formale al Garante e agli interessati |

> **Nessuna persona individuale può autonomamente decidere di NON notificare**. La decisione è collegiale (incident manager + legale).

## 4. Workflow operativo

### Fase 1 — Rilevazione (T+0)
- Chiunque rilevi un sospetto breach **scrive immediatamente** a [EMAIL_INCIDENT] o [TELEFONO_INCIDENT].
- Non attendere conferma: meglio falso allarme che ritardo.

### Fase 2 — Triage e contenimento (T+0 a T+4h)
**Tech Lead**:
1. Conferma il breach (verifica log, accessi, evidence).
2. **Contiene** il breach: revoca chiavi compromesse, chiude porte, blocca account compromessi, isola sistemi infetti.
3. Apre un incident ticket interno con:
   - Quando è iniziato (timestamp)
   - Quando è stato rilevato
   - Cosa è stato compromesso (sistema, dati, utenti)
   - Da chi (se identificabile)
   - Misure di contenimento applicate

### Fase 3 — Valutazione del rischio (T+4h a T+24h)
**Incident Manager** valuta:
- **Tipologia di breach**: confidenzialità, integrità, disponibilità.
- **Categorie di dati coinvolti**: identificativi, fiscali, di pagamento, particolari?
- **Numero di interessati** coinvolti.
- **Rischio per i diritti e le libertà** dell'interessato (furto identità, frode, danno economico, danno reputazione, discriminazione).
- **Misure di mitigazione** applicate (cifratura, blocchi, ecc.).

**Output**: classificazione del rischio (basso / medio / alto).

### Fase 4 — Notifica al Garante (entro T+72h dalla rilevazione)
Se rischio ≥ medio:
- Compilare modulo online: https://servizi.gpdp.it/databreach/s/
- Indicare:
  - Natura del breach
  - Categorie e numero approssimativo di interessati
  - Categorie e numero approssimativo di record
  - Conseguenze probabili
  - Misure adottate o proposte
  - Contatti DPO (se nominato) o referente

**Se non si raggiungono le 72h**: notifica preliminare con quanto noto + integrazione successiva (motivare il ritardo).

### Fase 5 — Comunicazione agli interessati (se rischio elevato)
**Quando**: senza ingiustificato ritardo (giorni, non settimane).
**Come**: email registrata + notifica in-app + (eventuale) post pubblico se non si possono identificare singolarmente gli interessati.
**Cosa dire** (template in §6):
- Cosa è successo
- Quali dati sono coinvolti
- Conseguenze probabili
- Misure adottate
- Cosa l'interessato può fare (es. cambiare password, monitorare conti, ecc.)
- Contatti per domande

### Fase 6 — Documentazione e lessons learned
- Aggiornare il **registro interno dei breach** (vedi §7).
- Conservare tutti i log e evidence per almeno 5 anni.
- Sessione di **post-mortem** entro 2 settimane: cosa è andato storto, come prevenirlo.
- Aggiornare procedure, formazione, controlli tecnici.

## 5. Contatti rapidi

| Chi | Contatto | Per cosa |
|-----|----------|----------|
| Incident Manager | [EMAIL_INCIDENT] / [TELEFONO_INCIDENT] | Tutto |
| Garante per la Protezione dei Dati Personali | https://servizi.gpdp.it/databreach/s/ | Notifica formale |
| Legale | [EMAIL_AVVOCATO] | Validazione comunicazioni |
| AWS Security | https://aws.amazon.com/security/vulnerability-reporting/ | Breach lato AWS |
| Stripe | dataprotectionofficer@stripe.com | Breach lato Stripe |
| Google Cloud | https://support.google.com/cloud/contact/dpo | Breach lato Google |
| Vercel | privacy@vercel.com | Breach lato Vercel |

## 6. Template comunicazione agli interessati

```text
Oggetto: Informazioni importanti sulla sicurezza del tuo account OpenDrone

Caro/a [NOME],

ti scriviamo per informarti che il [DATA] abbiamo rilevato una violazione
di sicurezza che potrebbe aver coinvolto alcuni dei tuoi dati personali.

Cosa è successo:
[descrizione concisa: es. "un accesso non autorizzato al nostro database
di nomi e indirizzi email"]

Quali dati sono coinvolti:
[elenco preciso: es. "email, nome, cognome, indirizzo di spedizione"]

Cosa NON è coinvolto:
[ciò che NON è stato esposto: es. "le password (cifrate e non leggibili in
chiaro), i dati di carta di credito (gestiti da Stripe e mai presenti sui
nostri server)"]

Cosa abbiamo fatto:
[misure di contenimento e correttive]

Cosa puoi fare tu:
[azioni consigliate: es. "cambiare la password, prestare attenzione a
email sospette che usano i tuoi dati"]

Per qualsiasi domanda scrivi a [EMAIL_PRIVACY] o chiama [TELEFONO].

Hai diritto di proporre reclamo al Garante per la Protezione dei Dati
Personali (www.gpdp.it).

Ci scusiamo per l'accaduto e prendiamo molto seriamente la sicurezza dei
tuoi dati.

Il team di OpenDrone
```

## 7. Registro interno dei breach

Tabella da mantenere aggiornata (anche per breach **non notificati**, art. 33.5):

| ID | Data rilevazione | Tipologia | Categorie dati | N° interessati | Rischio | Notificato Garante? | Notificato interessati? | Misure adottate | Chiuso il |
|----|------------------|-----------|----------------|----------------|---------|---------------------|--------------------------|------------------|-----------|
| 001 | – | – | – | – | – | – | – | – | – |

Conservare per almeno 5 anni.
