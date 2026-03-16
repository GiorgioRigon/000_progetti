# CIS Architecture

Versione semplice dell'architettura tecnica iniziale del Commercial Intelligence System (CIS).

## Obiettivo dell'architettura

L'architettura dell'MVP deve rispettare quattro principi:

- mantenere il controllo umano sulle azioni esterne
- separare chiaramente dati, logica e interfaccia
- restare semplice da capire e modificare
- consentire evoluzioni future senza riscrivere tutto

## Vista generale

Il sistema e organizzato in quattro livelli:

```text
Human Orchestrator
        |
        v
Workbot Layer
        |
        v
Data Layer
        |
        v
Local Web Interface
```

Questa vista non rappresenta una sequenza rigida, ma i confini logici principali del sistema.

## 1. Human Orchestrator

### Ruolo

Il livello umano governa il sistema.

L'utente:

- sceglie il progetto commerciale attivo
- decide cosa cercare
- conferma o corregge i dati raccolti
- approva ogni strategia di contatto
- modifica manualmente le bozze prima dell'uso

### Responsabilità

- definire obiettivi e priorità
- avviare i workflow
- validare i risultati dei workbot
- decidere se un lead va contattato oppure no

### Confini

Questo livello non delega mai completamente all'AI:

- invio automatico di email: escluso
- contatto automatico dei prospect: escluso
- decisioni commerciali finali: sempre umane

## 2. Workbot Layer

### Ruolo

Questo livello contiene i moduli di lavoro specializzati che assistono l'utente.

Per l'MVP il layer può essere inizialmente semplice e anche in parte rule-based.

### Workbot previsti

- `WB0 Target Discovery`
- `WB1 Contact Hunter`
- `WB2 Lead Qualifier`
- `WB3 Strategy Builder`
- `WB4 Outreach Drafter`
- `WB5 Follow-up Planner`
- `WB6 Call Assistant` futuro
- `WB7 CRM Memory Manager`

### Responsabilità

- trasformare input dell'utente in output strutturati
- leggere dati dal database
- scrivere risultati validati nel database
- proporre suggerimenti, non eseguire azioni esterne

### Confini

I workbot non devono:

- parlare direttamente con clienti o prospect
- inviare messaggi autonomamente
- aggirare le configurazioni di progetto
- modificare dati critici senza tracciabilità

I workbot devono operare entro regole chiare:

- input definiti
- output strutturati
- comportamento osservabile

## 3. Data Layer

### Ruolo

Il Data Layer e il nucleo del sistema.

Qui vengono conservati:

- organizzazioni
- contatti
- campagne
- messaggi
- azioni commerciali
- memoria relazionale
- configurazioni dei progetti

### Componenti principali

- database SQLite locale
- file di configurazione per progetto
- eventuali file CSV di import

### Responsabilità

- persistenza dei dati
- lettura e scrittura consistente
- tracciabilità dello storico
- separazione tra dati di progetto e logica applicativa

### Confini

Il Data Layer non deve:

- contenere logica di presentazione HTML
- contenere decisioni di business sparse e non documentate
- dipendere da servizi esterni per funzionare nell'MVP

## 4. Local Web Interface

### Ruolo

La Local Web Interface e la parte visibile del sistema.

Per l'MVP è una dashboard locale costruita con:

- Python
- Flask
- HTML templates

### Responsabilità

- mostrare dati e stato del sistema
- permettere inserimento e modifica manuale dei dati
- rendere leggibili score, motivazioni, bozze e storico
- offrire un punto unico di accesso alle funzioni principali

### Schermate minime previste

- Home
- Organizations
- dettaglio organization

### Confini

L'interfaccia non deve:

- contenere logica complessa di scoring
- sostituire il livello dati
- implementare automazioni nascoste

L'interfaccia deve chiamare servizi applicativi chiari, non accedere in modo disordinato ai dati.

## Relazione tra i livelli

Flusso minimo previsto nell'MVP:

1. L'utente avvia un'attivita o inserisce dati.
2. I workbot elaborano o arricchiscono le informazioni.
3. I risultati vengono letti o salvati nel Data Layer.
4. La dashboard locale mostra i risultati all'utente.
5. L'utente decide il passo successivo.

## Regole architetturali iniziali

- `Human Orchestrator` decide, il sistema suggerisce.
- `Workbot Layer` produce output strutturati e verificabili.
- `Data Layer` resta la fonte di verita del sistema.
- `Local Web Interface` presenta e raccoglie input, ma non governa la logica di business.

## Confine dell'MVP

Per la prima versione l'architettura deve restare locale, leggibile e a basso rischio.

Quindi sono fuori perimetro architetturale:

- automazioni esterne non supervisionate
- dipendenze obbligatorie da servizi cloud
- architetture distribuite
- code, broker o microservizi
- multiutenza complessa

## Evoluzione futura

L'architettura potra evolvere in seguito con:

- workbot piu sofisticati
- supporto LLM locale o cloud
- pipeline commerciale piu completa
- interfacce e viste aggiuntive

Queste estensioni devono pero rispettare il confine base definito qui: dati solidi, controllo umano, separazione chiara dei livelli.
