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
- `WB0` puo guidare meglio la review manuale mostrando focus del profilo, campi minimi, segnali di fit e checklist prima dell'import
- il filename dei run `WB0` deve restare corto e compatibile con Windows: il titolo del run va slugificato e troncato per evitare errori di salvataggio

### Idee future

- aggiungere uno script Python che generi un primo prompt di ricerca a partire dagli input del run di `WB0`
- valutare in una fase successiva una versione di `WB0` che effettui la ricerca in automatico appoggiandosi a un chatbot cloud o locale
- valutare in una fase successiva se distinguere meglio nella review `lead cliente`, `partner` e `moltiplicatore` quando questo serve davvero

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
- `WB1` puo guidare meglio il salvataggio manuale distinguendo fonte verifica, livello del contatto e segnali utili alla qualificazione

### Vincoli da ricordare

- nessuna automazione fragile o scraping complesso in questa fase
- human in the loop sempre attivo
- `WB1` arricchisce lead gia presenti, non sostituisce `WB0`

### Idee future

- valutare in una fase successiva un salvataggio strutturato dedicato per i risultati WB1 separato dalle note organization
- aggiungere selezione o aggiornamento guidato di un contatto esistente invece della sola aggiunta di un nuovo referente
- valutare in una fase successiva se promuovere `fonte verifica`, `livello contatto` e `segnali qualificazione` da note a campi piu strutturati

## Profili operativi workbot

### Decisioni correnti

- introdurre un file `workbot_profiles.json` per progetto come configurazione operativa leggera di `WB0` e `WB1`
- usare il profilo per migliorare i prompt preview senza cambiare il database in questa fase
- mantenere i workbot generici e spostare la specializzazione nei profili di progetto
- tenere il sistema modificabile a mano e leggibile, senza motore di automazione nuovo
- il progetto attivo puo essere scelto dalla UI leggendo i progetti disponibili in `projects/`

### Profili previsti

- `melodema` come profilo base per il caso coro
- `ethics` come profilo base per il caso urgente di utilizzo reale

### Decisioni recenti sui contenuti

- il profilo `melodema` deve privilegiare target realisticamente contattabili e non solo coerenti sul piano artistico
- il profilo `melodema` deve distinguere meglio tra programmazione stabile, evento singolo e semplice compatibilita generica
- il profilo `ethics` deve privilegiare segnali operativi e verificabili di maturita organizzativa
- nel profilo `ethics` va distinta la natura del lead: potenziale cliente, partner o moltiplicatore
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

## WB4

### Decisioni correnti

- `WB4 Outreach Drafter` parte in versione minima dalla scheda `organization`
- la bozza viene generata da `projects/<project_key>/email_templates/first_outreach.md`
- la bozza resta sempre modificabile manualmente prima del salvataggio
- il salvataggio minimo usa le tabelle gia esistenti: `outreach_actions` per l'azione e `messages` per subject/body della bozza
- lo storico minimo delle bozze viene mostrato nella scheda `organization`, senza invio automatico e senza workflow commerciale avanzato
- per migliorare la qualita restando nell'MVP, la bozza puo leggere anche dati gia presenti nel CIS: blocco note `[PdR125]`, qualificazione lead e configurazione di presentazione/outreach del progetto in `communication_style.yaml`
- per mail a freddo `ethics`, la presentazione non va lasciata implicita: deve dichiarare chi scrive, da quale contesto arriva e quale problema operativo prova a semplificare, mantenendo tono sobrio e non promozionale
- per `ethics` il template base di prima mail resta consulenziale e sobrio; una variante piu diretta viene salvata come `projects/ethics/email_templates/first_outreach_direct.md` per interlocutori piu rapidi o orientati al sodo

### Evoluzione utile successiva

- conviene preparare una gestione di template outreach multipli con metadati e tag, prima ancora di introdurre suggerimenti automatici o LLM
- la prima fase puo restare manuale: selezione del template da UI aiutata da label, descrizione e tag come `destinatario`, `azienda`, `fase`, `tono`, `canale`
- per `ethics` i template possono iniziare a essere indicizzati in `projects/ethics/email_templates/templates_index.yaml`, mantenendo i contenuti testuali nei file `.md`
- una fase successiva puo aggiungere suggerimento automatico rule-based del template piu adatto usando dati gia presenti nel CIS, ad esempio ruolo del contatto, canale disponibile, segnali di qualificazione e struttura del lead
- solo dopo aver consolidato template e regole semplici ha senso valutare una selezione o riscrittura assistita da LLM

## Data Model

### Idee future

- spazio riservato per note e decisioni su schema, import e tracciabilita

## Qualificazione lead

### Decisioni correnti

- conviene tracciare un nucleo minimo di qualificazione riusabile per tutti i progetti, non solo per `ethics`
- il nucleo comune puo restare leggero: `fit`, `priorita`, `tipo opportunita`, `segnali`, `prossimo passo`, `nota`
- in questa fase il nucleo viene salvato nelle note organization con un blocco dedicato, senza cambiare il database
- i dettagli specifici di dominio restano nei profili progetto e nelle note generate dai workbot

### Razionale

- questa scelta rende il sistema trasferibile tra `melodema`, `ethics` e altri progetti commerciali
- evita di introdurre troppo presto campi database che potrebbero rivelarsi troppo specifici o troppo rigidi
- permette di capire con uso reale quali campi meritano in futuro di diventare strutturati

### Gancio commerciale `ethics` per lead PdR125 in rinnovo

- per lead gia certificati `UNI/PdR 125` con certificazione in scadenza, il gancio commerciale preferibile e il rinnovo triennale: aiutare l'azienda ad arrivare all'audit con un sistema documentale piu ordinato, aggiornato e facile da mantenere
- evitare formule come `rifare la certificazione da zero`, perche il caso ordinario e un rinnovo triennale con sorveglianze annuali, non necessariamente una ripartenza completa
- `E-docs` va proposto come punto di miglioramento operativo della gestione documentale e delle evidenze, non come sostituto dell'organismo di certificazione
- se emergono insoddisfazioni su costo, supporto o gestione precedente, puo essere valutata anche una proposta di consulenza per il rinnovo e, in modo separato, formazione
- questi lead possono essere utili come beta test e primi case study, ma senza allargare l'MVP: prima completare il flusso base con qualificazione, bozza modificabile, storico minimo e controllo umano
- i settori rilevanti per questo gancio sono definiti in `projects/ethics/relevant_sectors.md`, da usare come riferimento operativo per compilare `organizations.sector`, note `[PdR125]` e qualificazione lead

## Multi-progetto

### Decisioni correnti

- per mantenere database unico ma separazione operativa piu pulita, `organizations` deve avere un `project_key`
- tutte le organization esistenti possono essere attribuite a `melodema`
- nuove organization manuali, import CSV e import da `WB0` ereditano il progetto attivo
- la lista `Organizations` deve mostrare solo le organization del progetto attivo

## Step 7

### Decisioni correnti

- dopo l'uso reale su `ethics`, lo Step 6 puo considerarsi sostanzialmente chiuso come verifica operativa MVP
- lo Step 7 resta un consolidamento finale, non un'estensione di perimetro
- in Step 7 conviene dare priorita a chiarimenti operativi, micro-correzioni UX/testuali e pulizia minima di profili o prompt
- in Step 7 non conviene introdurre nuovo schema dati, nuove automazioni esterne o un workflow commerciale piu complesso
- le idee fuori perimetro MVP o non prioritarie per Step 7 vanno parcheggiate in `docs/OUT_OF_SCOPE_IDEAS.md`
- la roadmap di 2 settimane su profili `WB0` e `WB1` puo considerarsi chiusa
- il rientro nella roadmap principale deve ripartire dal gap MVP piu concreto rimasto: bozza outreach modificabile e storico minimo, prima di funzioni piu evolute
- la decisione operativa del prossimo step e salvata anche in `docs/NEXT_STEP_OUTREACH_MINIMUM.md`

### Attriti emersi da ricordare

- il confine tra `WB1` e qualificazione lead va mantenuto esplicito: `WB1` arricchisce il lead, la qualificazione decide il passo commerciale
- alcuni lead importati da `WB0` sono validi come prova di filtro ma non ancora pronti per uso commerciale senza un passaggio `WB1` minimo
- la chiusura pratica di sessione deve lasciare sempre un `prossimo passo` chiaro nella qualificazione lead
