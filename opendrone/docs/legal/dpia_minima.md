# DPIA — Valutazione d'Impatto sulla Protezione dei Dati

> ⚠️ **DOCUMENTO INTERNO**
> Anche se non strettamente obbligatoria (le soglie art. 35.3 GDPR non sono raggiunte), questa DPIA leggera è **best practice** per documentare i due trattamenti potenzialmente più rischiosi: geolocalizzazione precisa di nodi/centri e scoring rating.

**Versione:** 1.0
**Data:** [DATA_REDAZIONE]
**Redattore:** [NOME_RESPONSABILE_PRIVACY]
**Approvato da:** [LEGALE_RAPPRESENTANTE]

---

## 1. Quando è obbligatoria una DPIA (art. 35 GDPR)

Una DPIA è obbligatoria se il trattamento:
1. Consiste in **valutazione sistematica e approfondita** di aspetti personali che producono effetti legali (profilazione automatizzata).
2. Tratta su **larga scala** categorie particolari (art. 9) o dati relativi a condanne penali.
3. Comporta **monitoraggio sistematico** di zone pubbliche.
4. Rientra nell'**elenco delle tipologie del Garante italiano** (allegato 1 provv. 11 ottobre 2018).

**Per OpenDrone**: nessuna delle 4 condizioni è strettamente integrata, ma due trattamenti meritano valutazione:
- **Geolocalizzazione precisa** di nodi e centri (lat/lon a 6 decimali ~ precisione 10cm).
- **Sistema di scoring/rating** che impatta reputazione professionale.

## 2. Trattamento 1 — Geolocalizzazione precisa nodi/centri

### 2.1 Descrizione
Per assegnare gli ordini al nodo di stampa più vicino al cliente, conserviamo le coordinate GPS dei nodi e centri (`PrintNodeProfile.latitude/longitude`, `AssemblyCenterProfile.latitude/longitude`).

### 2.2 Necessità e proporzionalità
- **Necessità**: il matching geografico riduce costi spedizione e tempi consegna. Senza coordinate precise dovremmo basarci su CAP, troppo grossolano.
- **Proporzionalità**: la precisione 6 decimali è eccessiva (~10 cm). Sufficiente 3-4 decimali (~10-100m).
- **Alternativa**: troncare a 3 decimali in storage, oppure usare H3 / S2 cell-id.

### 2.3 Rischi
| Rischio | Probabilità | Impatto | Score |
|---------|-------------|---------|-------|
| Disclosure indirizzo casa (per piccoli operatori che lavorano da casa) → stalking, furto | Media | Alto | 🟠 |
| Use abusivo da admin per geo-tracking competitivo | Bassa | Medio | 🟡 |
| Esposizione via UserSerializer ad altri utenti (vedi audit A3) | Alta (oggi) | Medio | 🟠 |

### 2.4 Misure di mitigazione
| ID | Misura | Stato |
|----|--------|-------|
| M-G1 | Troncare lat/lon a 3 decimali alla scrittura DB | ⏳ DA IMPLEMENTARE |
| M-G2 | Non esporre lat/lon nei serializer pubblici (vedi audit A3) | ⏳ branch security-audit |
| M-G3 | Audit log accesso ai profili nodo/centro | ⏳ post-MVP |
| M-G4 | Informativa esplicita in registrazione print_node/assembly su uso coordinate | ⏳ task #6 informativa registrazione |
| M-G5 | Permettere all'utente di indicare un punto di ritiro alternativo (non casa) | ⏳ Roadmap |

### 2.5 Decisione
Trattamento **lecito e proporzionato** dopo implementazione M-G1 e M-G2. Riproporre DPIA quando si introducono nuove finalità.

---

## 3. Trattamento 2 — Sistema di scoring (rating designer/nodo/centro)

### 3.1 Descrizione
Calcoliamo un rating per ogni designer/nodo/centro come media delle recensioni (per nodi: anche per categoria materiale). Il rating influenza la visibilità nel marketplace.

### 3.2 È profilazione ex art. 22?
**No, perché:**
- Il rating non produce **decisioni 100% automatizzate con effetti legali**.
- L'amministratore mantiene controllo umano (può approvare/rifiutare).
- Le recensioni sono visibili e contestabili.

→ **Non rientra nell'art. 22**, ma resta dato personale rilevante per la reputazione professionale.

### 3.3 Necessità e proporzionalità
- **Necessità**: il rating è strumento essenziale per distinguere fornitori di qualità.
- **Proporzionalità**: è basato solo su recensioni reali, non su comportamenti tracciati.

### 3.4 Rischi
| Rischio | Probabilità | Impatto | Score |
|---------|-------------|---------|-------|
| Recensioni false/diffamatorie → rating ingiustamente basso | Media | Alto | 🟠 |
| Disclosure economica via `total_revenue`, `total_royalties_earned` (audit A3) | Alta | Medio-Alto | 🟠 |
| Manipolazione rating tramite account fake | Media | Alto | 🟠 |

### 3.5 Misure di mitigazione
| ID | Misura | Stato |
|----|--------|-------|
| M-R1 | Rimuovere `total_revenue`, `total_royalties_earned` dai serializer pubblici | ⏳ branch security-audit (A3) |
| M-R2 | Rate limit + verifica email registrazione | ✓ Rate limit fatto, email verify in branch (A5) |
| M-R3 | Permettere al fornitore di rispondere alle recensioni | ⏳ Roadmap |
| M-R4 | Permettere all'admin di rimuovere recensioni illegittime con audit trail | ⏳ task M11 audit log |
| M-R5 | Diritto di "rettifica" rating: l'utente può chiedere ricalcolo se evidenza di review fraud | ⏳ Procedura interna |
| M-R6 | Notifica al fornitore al ricevimento recensione (così può contestare entro X giorni) | ⏳ Roadmap |

### 3.6 Decisione
Trattamento **lecito** dopo implementazione M-R1, M-R2, M-R4. Trasparenza pieces verso utente: il rating è basato su recensioni medie, non altro.

---

## 4. Consultazione del Garante (art. 36)

**Non necessaria** in questa fase: i rischi residui dopo le misure sopra sono **bassi-medi**, non "elevati".

Se in futuro si introducessero:
- Profilazione di designer per tariffe dinamiche.
- Decisioni automatizzate di sospensione account.
- Trattamento di dati di minori.

Allora valutare consultazione preventiva del Garante.

---

## 5. Storico revisioni DPIA

| Data | Modifica | Revisore |
|------|----------|----------|
| [DATA] | Stesura iniziale | [NOME] |

**Trigger di revisione**:
- Modifiche sostanziali ai trattamenti.
- Nuove tipologie di dati raccolti.
- Eventi di sicurezza (data breach).
- Cambio normativo.
- Comunque: revisione almeno biennale.
