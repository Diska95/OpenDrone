# Snippet — Informativa breve per il form di registrazione

> ⚠️ **BOZZA TECNICA — VALIDARE CON LEGALE**
> Questo è il testo da mostrare nel form di registrazione (sopra al checkbox di accettazione) e nel popup informativo. Compila i placeholder.

---

## Snippet "informativa breve" (mostrato sopra il checkbox)

```text
Trattiamo i tuoi dati per crearti un account su OpenDrone, gestire i tuoi
ordini/progetti e adempiere agli obblighi di legge (es. fatturazione).
I dati restano in UE e non vengono ceduti a terzi salvo i fornitori
indispensabili (AWS, Stripe, Google se usi il login Google) — vedi
l'Informativa completa.

Hai sempre diritto di accedere, correggere o cancellare i tuoi dati,
e di proporre reclamo al Garante. Titolare: [DENOMINAZIONE SOCIETÀ],
[EMAIL_PRIVACY].
```

## Checkbox obbligatorio

```text
☐ Ho letto e accetto la Privacy Policy e i Termini di Servizio
```

> Il checkbox **non deve essere pre-selezionato** (art. 7 GDPR + Cass. it. 17278/2018).

## Checkbox facoltativo (per future newsletter — non attivare oggi)

```text
☐ Acconsento a ricevere comunicazioni di marketing via email da OpenDrone
   (puoi disiscriverti in qualsiasi momento dal link in fondo a ogni email)
```

> Da abilitare solo quando si introdurrà una newsletter. **Separato** dal consenso obbligatorio (no consensi cumulativi — Garante 2018).

## Snippet per "Accedi con Google"

```text
Cliccando su "Continua con Google" ti registri/accedi tramite il tuo
account Google. Riceveremo da Google il tuo nome, cognome ed email
verificata. Per i dettagli vedi l'Informativa completa e la
Privacy Policy di Google.
```

> Anche per il login Google va mostrato un riferimento alla Privacy Policy. Se l'utente clicca Google senza aver accettato i T&S, si può:
> - Mostrare un modal "Per continuare con Google accetta prima la Privacy Policy"
> - Oppure considerare il click stesso come accettazione (ma il Garante è severo: meglio modal esplicito)

## Footer del modulo

```html
<p class="legal-footer">
  Cliccando su "Crea account" dichiari di aver letto e accettato la
  <a href="/privacy">Privacy Policy</a> e i <a href="/termini">Termini di Servizio</a>.
  Per i cookie consulta la <a href="/cookie">Cookie Policy</a>.
</p>
```

## Versionamento testi

Ogni modifica sostanziale a Privacy Policy o T&S richiede:
1. Incrementare la `version` in `UserConsent` (es. `pp_v1` → `pp_v2`).
2. Al login successivo dell'utente già registrato, mostrare modal "Abbiamo aggiornato la Privacy Policy. [Leggi le novità] [Accetta] [Esci]".
3. Salvare nuovo record `UserConsent(user, type='privacy_policy', version='pp_v2', accepted_at=now, ip, user_agent)`.

## Salvataggio consenso (lato app)

**Modello DB** (da implementare in task #7):
```python
class UserConsent(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50)  # 'privacy_policy', 'terms', 'marketing'
    version = models.CharField(max_length=20)        # 'pp_v1', 'tos_v1', 'mkt_v1'
    accepted = models.BooleanField()
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'consent_type', '-accepted_at'])]
```

Endpoint `POST /api/auth/consent/`:
```json
{
  "consents": [
    {"type": "privacy_policy", "version": "pp_v1", "accepted": true},
    {"type": "terms",          "version": "tos_v1", "accepted": true},
    {"type": "marketing",      "version": "mkt_v1", "accepted": false}
  ]
}
```
