# CIS Development Notes

Appunti e idee di sviluppo del progetto CIS, organizzati per argomento.

## Come usare questo file

- aggiungere note brevi e concrete
- raggruppare per area funzionale
- distinguere tra idee future, miglioramenti e decisioni aperte
- mantenere il file come memoria operativa del progetto

## WB0

### Stato attuale

- lo sviluppo di `WB0` si ferma qui per questa fase
- `WB0` oggi funziona come filtro operativo prima del database CIS
- il run e stato rifattorizzato per uso manuale via chatbot
- il prompt preview di `WB0` puo iniziare a leggere un profilo operativo specifico per progetto

### Idee future

- aggiungere uno script Python che generi un primo prompt di ricerca a partire dagli input del run di `WB0`
- valutare in una fase successiva una versione di `WB0` che effettui la ricerca in automatico appoggiandosi a un chatbot cloud o locale

### Vincoli da ricordare

- human in the loop sempre attivo
- mantenere separati discovery e database operativo
- evitare automazioni fragili o scraping complesso nelle fasi iniziali

## WB1

### Stato attuale

- `WB1 Contact Hunter` parte in versione base dentro la scheda di una `organization` gia presente nel CIS
- il flusso e manuale o assistito via chatbot tramite prompt preview locale
- i dati arricchiti aggiornano esplicitamente il database CIS: sito, email e telefono sulla organization; referente e ruolo come contatto associato
- i social ufficiali e le note di verifica WB1 vengono salvati nelle note della organization in forma leggibile
- il prompt preview di `WB1` puo iniziare a leggere un profilo operativo specifico per progetto

### Vincoli da ricordare

- nessuna automazione fragile o scraping complesso in questa fase
- human in the loop sempre attivo
- `WB1` arricchisce lead gia presenti, non sostituisce `WB0`

### Idee future

- valutare in una fase successiva un salvataggio strutturato dedicato per i risultati WB1 separato dalle note organization
- aggiungere selezione o aggiornamento guidato di un contatto esistente invece della sola aggiunta di un nuovo referente

## Profili operativi workbot

### Decisioni correnti

- introdurre un file `workbot_profiles.json` per progetto come configurazione operativa leggera di `WB0` e `WB1`
- usare il profilo per migliorare i prompt preview senza cambiare il database in questa fase
- mantenere i workbot generici e spostare la specializzazione nei profili di progetto
- tenere il sistema modificabile a mano e leggibile, senza motore di automazione nuovo

### Profili previsti

- `melodema` come profilo base per il caso coro
- `consulenza_certificazione` come profilo base per il caso urgente di utilizzo reale

### Decisioni recenti sui contenuti

- il profilo `melodema` deve privilegiare target realisticamente contattabili e non solo coerenti sul piano artistico
- il profilo `melodema` deve distinguere meglio tra programmazione stabile, evento singolo e semplice compatibilita generica
- il profilo `consulenza_certificazione` deve privilegiare segnali operativi e verificabili di maturita organizzativa
- nel profilo `consulenza_certificazione` va distinta la natura del lead: potenziale cliente, partner o moltiplicatore
- per `WB1` nel dominio certificazione va tracciato se il contatto trovato e decision maker, influencer o contatto ponte
- per `WB1` nel dominio certificazione conviene annotare anche la leva principale emersa: `PdR125`, `HR`, `ESG`, governance o compliance

### Vincoli da ricordare

- human in the loop sempre attivo
- nessuna esecuzione automatica esterna in questa fase
- non introdurre una meta-architettura complessa dei prompt
- prima migliorare prompt e input, poi valutare eventuali campi dati aggiuntivi per qualificazione certificazioni

## Dashboard

### Idee future

- spazio riservato per note e decisioni su UX, navigazione e viste operative

## Data Model

### Idee future

- spazio riservato per note e decisioni su schema, import e tracciabilita
