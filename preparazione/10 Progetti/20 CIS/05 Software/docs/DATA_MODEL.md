# CIS Data Model

Questo documento descrive il primo modello dati SQLite del CIS.

## Obiettivo

Lo schema iniziale serve a coprire il perimetro dell'MVP:

- salvare campagne e progetti operativi
- registrare organizzazioni e contatti
- tracciare azioni commerciali e bozze di comunicazione
- conservare memoria relazionale minima
- collegare materiali di supporto

## Tabelle principali

### `campaigns`

Rappresenta una campagna commerciale o un'iniziativa operativa.

Serve a raggruppare lead, azioni e materiali.

### `organizations`

Rappresenta enti, aziende o organizzazioni target.

Contiene i dati principali del lead a livello organizzazione.

Campi operativi rilevanti:

- `employee_count`: numero dipendenti, quando disponibile. Serve come dato semplice di qualificazione lead e non sostituisce le note qualitative su dimensione, gruppo o sedi.

### `contacts`

Rappresenta persone associate a una organizzazione.

Permette di tenere distinti il lead organizzazione e i singoli referenti.

### `outreach_actions`

Rappresenta un'azione commerciale pianificata o eseguita.

Esempi:

- email da inviare
- follow-up
- chiamata
- contatto tramite evento

### `messages`

Contiene il contenuto dei messaggi, in particolare le bozze di outreach dell'MVP.

E collegata facoltativamente a una `outreach_action`.

### `relationship_memory`

Contiene memoria commerciale e relazionale.

Esempi:

- preferenze del contatto
- informazioni sensibili al contesto
- esiti di precedenti interazioni

### `assets`

Contiene materiali collegati a campagne o organizzazioni.

Esempi:

- brochure
- presentazioni
- link a materiali esterni

## Scelte di modellazione

- SQLite e usato come database locale principale.
- Le chiavi primarie sono interi autoincrementali per mantenere lo schema semplice.
- Le foreign key sono attive per mantenere coerenza referenziale.
- I campi `created_at` e `updated_at` sono presenti in ogni tabella per facilitare tracciabilità e debugging.
- Alcune relazioni usano `ON DELETE SET NULL` per non perdere storico dove non necessario.
- Le relazioni più forti, come `contacts -> organizations`, usano `ON DELETE CASCADE`.

## Confine di questo primo schema

Questo schema e intenzionalmente semplice.

Non include ancora:

- tabelle di autenticazione
- versionamento avanzato
- tagging complesso
- audit log completo
- normalizzazione spinta di lookup e vocabolari

Per l'MVP l'obiettivo non e la perfezione teorica del modello, ma una base solida e leggibile su cui costruire i flussi principali.
