# Data Retention Policy

> ⚠️ **DOCUMENTO INTERNO**
> Linee guida per la conservazione dei dati personali. Revisione almeno annuale.

**Ultima revisione:** [DATA_REVISIONE]

---

## 1. Principio

Conserviamo i dati personali **solo per il tempo strettamente necessario** alle finalità per cui sono stati raccolti (art. 5.1.e GDPR).

Per ogni categoria di dato è definito un **periodo di conservazione** dopo il quale il dato viene cancellato o pseudonimizzato.

## 2. Tabella di retention

| Categoria | Retention | Base | Eccezioni | Implementazione tecnica |
|-----------|-----------|------|-----------|--------------------------|
| **Account attivo** | Indefinita finché l'utente lo mantiene | Esecuzione contratto | – | Nessuna azione automatica |
| **Account inattivo (no login >24 mesi)** | 24 mesi → email warning → 6 mesi → soft delete | Legittimo interesse + minimizzazione | Account con ordini negli ultimi 10 anni: solo pseudonimizzazione, dati contabili conservati | Job Celery beat mensile (`apps/users/tasks.py:cleanup_inactive_users`) – DA IMPLEMENTARE |
| **Account cancellato dall'utente** | Hard-delete entro 30 giorni dalla richiesta | Diritto all'oblio (art. 17) | Ordini conclusi, fatture, royalty: pseudonimizzati (FK `user=NULL`, dati personali sostituiti con "Utente cancellato") | Endpoint `DELETE /api/auth/me/` – DA IMPLEMENTARE (task #8) |
| **Ordini conclusi** | 10 anni dalla conclusione | Obbligo legale (CC art. 2220, normativa fiscale) | – | Nessuna cancellazione automatica; dopo 10 anni job manuale o `archive_old_orders` |
| **Fatture / royalty** | 10 anni | Obbligo fiscale | – | Idem |
| **Indirizzi spedizione storici** | 10 anni (insieme all'ordine) | Esecuzione contratto + obbligo legale | – | Conservati nel JSONField `Order.shipping_address` |
| **Token JWT blacklisted** | 30 giorni post blacklist | Sicurezza (prevenire replay) | – | `python manage.py flushexpiredtokens` via Celery beat settimanale – DA SCHEDULARE |
| **Notifiche lette** | 6 mesi | Esecuzione contratto | – | Job Celery beat mensile – DA IMPLEMENTARE |
| **Notifiche non lette** | 12 mesi | Esecuzione contratto | – | Idem |
| **Log accesso (nginx)** | 12 mesi | Sicurezza, legittimo interesse | – | `logrotate` configurato su EC2 con `rotate 12` (mensile) – DA VERIFICARE config |
| **Log applicativo (gunicorn/django)** | 6 mesi | Debug, sicurezza | Errori critici archiviati 24 mesi | `logrotate` con `rotate 6` |
| **Audit log azioni admin** (in roadmap) | 5 anni | Compliance | – | Modello `AdminAuditLog`, no cancellazione automatica |
| **Recensioni** | Vita del progetto recensito | Consenso (pubblicazione opt-in) | Su cancellazione account: anonymizzate (`reviewer=NULL`, mantieni rating per integrità media) | Service `anonymize_user_reviews(user)` – DA IMPLEMENTARE |
| **File caricati su S3** | Vita del progetto/account | Consenso | Su cancellazione: rimossi da bucket | Storage signal `post_delete` su `ProjectFile` |
| **Foto build review** | Vita della recensione | Consenso | Su cancellazione account/review: rimossi | Idem |
| **Bio, avatar** | Vita dell'account | Consenso | Cancellazione: rimossi | Hard-delete |
| **Consensi (`UserConsent`)** | Per durata contratto + 5 anni | Obbligo prova art. 7 | Anche post-cancellazione account, conservati come "ex utente" | Soft-delete con flag `_account_deleted=True` |
| **Cookie consent (`CookieConsent`)** | 6 mesi (durata cookie banner) | Obbligo prova | – | Auto-cleanup |
| **Dati di sessione admin Django** | 2 settimane | Esecuzione contratto | – | Default `SESSION_COOKIE_AGE` |
| **Tentativi di login falliti** (per rate limit) | 1 ora (sliding window) | Sicurezza | – | DRF throttle in cache Redis (no persistenza) |
| **Email transazionali (log SES)** | 12 mesi | Esecuzione contratto + sicurezza | – | Lato Amazon SES, retention SES |

## 3. Cancellazione vs pseudonimizzazione

Per alcuni dati la cancellazione completa **non è possibile** per obblighi legali. In questi casi applichiamo la **pseudonimizzazione**:

- L'`Order.customer` viene messo a `NULL` o riassegnato a un utente fittizio "Utente cancellato".
- Il `shipping_address` viene mantenuto (è dato dell'ordine, non del cliente attuale) ma non più collegabile univocamente.
- Le `RoyaltyLedger.designer` viene messo a `NULL` ma `RoyaltyLedger` resta con importi per integrità contabile.

> Pseudonimizzazione ≠ cancellazione: i dati pseudonimizzati restano dati personali e vanno protetti, ma non sono più direttamente attribuibili all'interessato.

## 4. Job di retention da implementare (Celery beat)

```python
# apps/users/tasks.py

@shared_task
def cleanup_inactive_users():
    """Email warning + soft-delete per account inattivi."""
    cutoff_warning = now() - timedelta(days=24*30)
    cutoff_delete  = now() - timedelta(days=30*30)
    # ... vedi spec
```

Schedulare in `CELERY_BEAT_SCHEDULE`:
```python
CELERY_BEAT_SCHEDULE = {
    'cleanup_inactive_users':   {'task': 'apps.users.tasks.cleanup_inactive_users',   'schedule': crontab(day=1, hour=3, minute=0)},
    'cleanup_old_notifications': {'task': 'apps.notifications.tasks.cleanup',           'schedule': crontab(day=1, hour=4, minute=0)},
    'flush_expired_jwt':         {'task': 'apps.users.tasks.flush_expired_jwt',         'schedule': crontab(day_of_week=0, hour=5, minute=0)},
}
```

## 5. Verifica annuale

Una volta l'anno il responsabile privacy:
1. Verifica che i job di retention siano stati eseguiti regolarmente.
2. Controlla campioni a caso di dati per verificare l'effettiva cancellazione.
3. Aggiorna le retention se cambiano le finalità o gli obblighi legali.
4. Aggiorna questo documento.
