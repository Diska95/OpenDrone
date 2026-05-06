# Cookie Policy

> ⚠️ **BOZZA TECNICA — NON PUBBLICARE COSÌ COM'È**
> Va validata da un avvocato/DPO prima della pubblicazione. Compila i placeholder `[...]` con i dati reali della società.

**Ultimo aggiornamento:** [DATA_PUBBLICAZIONE]
**Versione:** 1.0

---

## 1. Cosa sono i cookie

I cookie sono piccoli file di testo che i siti web salvano sul tuo dispositivo quando li visiti. Possono essere usati per autenticarti, ricordare le tue preferenze, o tracciare il tuo comportamento per analisi statistiche o pubblicità.

Oltre ai cookie tradizionali, OpenDrone utilizza anche **localStorage** (uno storage del browser simile ai cookie ma gestito direttamente dal sito) e **script di terze parti** (es. Google Sign-In) che possono installare propri cookie.

Questa policy si applica a tutti gli strumenti di tracciamento sopra descritti, ai sensi del provvedimento del Garante del 10 giugno 2021 ("Linee guida cookie") e dell'art. 122 del Codice Privacy.

## 2. Quali cookie usa OpenDrone

### 2.1 Cookie e storage tecnici (necessari, non richiedono consenso)

| Nome | Tipo | Finalità | Durata |
|------|------|----------|--------|
| `access_token` | localStorage | Mantieni la sessione autenticata (JWT access) | 60 minuti |
| `refresh_token` | localStorage | Rinnova automaticamente la sessione | 30 giorni |
| `csrftoken` | Cookie | Protezione contro attacchi CSRF (Django) | 1 anno |
| `sessionid` | Cookie (solo per amministratori che usano l'admin Django) | Autenticazione admin | 2 settimane |
| `od_consent_v1` | Cookie | Memorizza le tue scelte sulla cookie policy | 6 mesi |

> Questi cookie sono **strettamente necessari** al funzionamento del sito. Possono essere installati senza il tuo consenso preventivo (art. 122 Codice Privacy). Se li blocchi a livello browser, parti del sito non funzioneranno.

### 2.2 Cookie e script di terze parti (richiedono consenso)

| Servizio | Cosa fa | Cosa è inviato | Quando si attiva |
|----------|---------|----------------|------------------|
| **Google Identity Services** (`accounts.google.com`) | Permette il login con account Google | Indirizzo IP, header browser, identificatore Google | Solo quando clicchi "Accedi con Google" o visiti la pagina di login/registrazione (se hai dato il consenso "funzionale") |
| **Google Fonts** (`fonts.gstatic.com`) | Carica i font tipografici del sito | Indirizzo IP, header browser | All'apertura di ogni pagina (se hai dato il consenso "funzionale") |
| **Stripe.js** (`js.stripe.com`) | Modulo di pagamento sicuro | Indirizzo IP, dati di sessione del checkout | Solo nella pagina di checkout (se hai dato il consenso "funzionale") |

> **Nessun cookie pubblicitario o di profilazione** è installato da OpenDrone al momento. Eventuali futuri cookie analitici (es. Plausible, Matomo, Google Analytics) saranno aggiunti a questa tabella e richiederanno consenso esplicito.

### 2.3 Categorie di consenso

Quando visiti il sito ti mostriamo un banner con tre scelte:

1. **Solo necessari**: installiamo solo i cookie tecnici della tabella 2.1. Non puoi usare il login Google e i font potrebbero essere caricati da fonti alternative o non caricati affatto.
2. **Solo funzionali**: in aggiunta ai necessari, abilitiamo i cookie/script di terze parti elencati in 2.2 (Google Sign-In, Google Fonts, Stripe.js).
3. **Accetta tutti**: equivalente a "Solo funzionali" oggi (non abbiamo cookie analitici/pubblicitari). Resta valido in futuro se aggiungeremo categorie ulteriori.

## 3. Come gestire e revocare il consenso

### 3.1 Sul sito
- **Modifica le scelte**: usa il link "Cookie Settings" nel footer.
- **Revoca**: stesso link, scegli "Solo necessari" e clicca "Salva".

La revoca **non ha effetto retroattivo**: i dati già raccolti prima della revoca restano trattati nei limiti esposti nella Privacy Policy.

### 3.2 A livello browser
Puoi bloccare o cancellare cookie e localStorage anche dalle impostazioni del tuo browser:
- **Chrome**: Impostazioni → Privacy e sicurezza → Cookie
- **Firefox**: Impostazioni → Privacy e sicurezza → Cookie e dati dei siti web
- **Safari**: Preferenze → Privacy
- **Edge**: Impostazioni → Cookie e autorizzazioni del sito

> Bloccare i cookie tecnici renderà impossibile l'accesso al tuo account.

## 4. Trasferimenti extra-UE

I servizi di terze parti che richiedono consenso (Google, Stripe) hanno sede negli Stati Uniti. I trasferimenti sono coperti dal **Data Privacy Framework UE-USA** e da **Clausole Contrattuali Standard**.

Vedi `sub_responsabili.md` per dettagli.

## 5. Modifiche a questa policy

Pubblicheremo modifiche sostanziali (es. nuovi servizi terzi, nuove categorie cookie) su questa pagina. Per le modifiche che richiedono nuovo consenso, ti rimostreremo il banner.

## 6. Contatti

Per domande sui cookie e sul tracciamento scrivi a **[EMAIL_PRIVACY]**.

Per la lista completa dei diritti (accesso, cancellazione, portabilità, ecc.) e per il reclamo al Garante, vedi la **Privacy Policy** dedicata.
