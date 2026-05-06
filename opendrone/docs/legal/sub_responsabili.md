# Sub-responsabili del trattamento — art. 28 GDPR

> ⚠️ **DOCUMENTO INTERNO + ESTRATTO PUBBLICO**
> La tabella sintetica può essere mostrata in fondo alla Privacy Policy. Le copie firmate dei DPA vanno conservate offline.

**Ultima revisione:** [DATA_REVISIONE]

---

## Sub-responsabili attivi

| Fornitore | Servizio | Sede legale | Trattamento dati | Garanzie | DPA stipulato? |
|-----------|----------|-------------|------------------|----------|----------------|
| **Amazon Web Services EMEA SARL** | Hosting (EC2), database (RDS), storage (S3), email (SES) | Lussemburgo (HQ EU); data center: Stoccolma (`eu-north-1`) per EC2/RDS, Milano (`eu-south-1`) per S3/SES | Tutti i dati piattaforma | AWS GDPR DPA + SCC standard | ⏳ DA ACCETTARE — AWS Console → Account → AWS Artifact → "AWS GDPR DPA" → Accept Agreement |
| **Vercel Inc.** | Hosting frontend statico (CDN edge) | San Francisco, USA | Solo asset statici (HTML/JS/CSS); nessun dato utente persistito | DPF + SCC + Vercel DPA | ⏳ DA SCARICARE — https://vercel.com/legal/dpa (richiedere copia firmata se Pro/Enterprise plan) |
| **Stripe Payments Europe Ltd.** | Pagamenti, payout, abbonamenti | Dublino, Irlanda (con sub-processor Stripe Inc. negli USA) | Dati di pagamento, dati di fatturazione, importi ordini | Stripe DPA + SCC + DPF | ⏳ DA SCARICARE — https://stripe.com/legal/dpa accettato implicitamente con i ToS, scaricare PDF per archivio |
| **Google Ireland Ltd.** | Login federato (Google Sign-In/OAuth), Google Fonts (se non self-hosted) | Dublino, Irlanda (sub-processor Google LLC USA) | Email Google verificata, given_name, family_name (solo per chi sceglie Google login); IP per Google Fonts | Google DPA Cloud Processor Terms + SCC + DPF | ⏳ DA ACCETTARE — Google Cloud Console → IAM → Compliance |

## Sub-responsabili potenziali (non ancora attivi)

| Fornitore | Servizio | Quando attivare |
|-----------|----------|-----------------|
| Cloudflare Inc. | CDN/WAF/Tunnel (cartella `cloudflared` osservata sull'EC2 ma non in repo) | Verificare se attivata: se sì, firmare Cloudflare DPA (https://www.cloudflare.com/cloudflare-customer-dpa/) |
| Sentry / Bugsnag / DataDog | Error tracking, APM | Quando si introduce monitoring |
| Newsletter provider (Mailchimp, Brevo) | Email marketing | Quando si lancia newsletter |

## Procedura per nuovi sub-responsabili

Quando si introduce un nuovo fornitore che tratta dati personali per conto del Titolare:

1. **Valutare** se il fornitore è qualificabile come responsabile esterno ex art. 28 (sì se tratta dati per conto nostro su nostre istruzioni; no se è un titolare autonomo).
2. **Verificare** la sede legale e l'eventuale presenza di trasferimenti extra-UE.
3. **Stipulare DPA** (Data Processing Agreement) prima dell'attivazione.
4. **Verificare** le misure di sicurezza dichiarate (certificazioni ISO 27001, SOC2, ecc.).
5. **Aggiornare** questo documento e la Privacy Policy pubblica.
6. **Informare** gli utenti se il nuovo trattamento richiede consenso aggiuntivo.

## Documenti da archiviare (offline o in cloud privato)

```
/legal/dpa/
  ├── aws_gdpr_dpa_signed_YYYY-MM-DD.pdf
  ├── vercel_dpa_signed_YYYY-MM-DD.pdf
  ├── stripe_dpa_signed_YYYY-MM-DD.pdf
  └── google_dpa_signed_YYYY-MM-DD.pdf
```

> Conservare almeno per la durata del contratto + 10 anni dopo la sua cessazione.

---

## Snippet per Privacy Policy pubblica (sezione 5.2)

```markdown
### Sub-responsabili esterni

Per offrire il servizio ci avvaliamo dei seguenti sub-responsabili,
con cui abbiamo stipulato accordi di trattamento dei dati conformi
all'art. 28 GDPR:

- **Amazon Web Services** — hosting in UE (Stoccolma, Milano) e
  email transazionali. DPA + SCC.
- **Vercel** — hosting frontend (USA, ma niente dati utente persistiti).
  DPF + SCC.
- **Stripe** — pagamenti e payout. Sede UE (Dublino) con sub-processor USA.
  DPA + SCC + DPF.
- **Google** — solo se usi il login Google. Sede UE (Dublino) con
  sub-processor USA. DPA + SCC + DPF.

Puoi richiedere copia degli accordi stipulati scrivendo a [EMAIL_PRIVACY].
```
