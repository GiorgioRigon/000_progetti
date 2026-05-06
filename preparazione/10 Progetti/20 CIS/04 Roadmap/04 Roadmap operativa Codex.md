---
title: CIS - Roadmap operativa Codex
type: roadmap
project: CIS
status: attivo
created: 2026-03-14
updated: 2026-05-04
tags:
  - roadmap
  - codex
  - cis
  - sviluppo
---
Controlla se è stato implementato il passo 16
# CIS - Roadmap operativa Codex

Tag: #roadmap #codex #cis #sviluppo

## Indice

- [[../00 CIS Home|CIS Home]]
- [[../02 PRD/02 PRD|PRD]]
- [[../02 PRD/CIS PRD Obsidian|PRD Obsidian v0.2]]

## Come usare questa checklist

Questa roadmap e pensata per essere eseguita con Codex da terminale, un passaggio alla volta.

Regola pratica:

- chiedi a Codex un solo passo per volta
- fai implementare solo quel passo
- verifica il risultato
- passa al passo successivo solo quando quello precedente funziona

Prompt base consigliato da riutilizzare in ogni turno:

```text
Leggi prima i file esistenti rilevanti.
Poi implementa solo questo passo: [incolla qui il passo].
Non fare altro.
Alla fine dimmi:
1. quali file hai creato o modificato
2. come verificare il risultato
3. qual e il prossimo passo naturale
```

## Obiettivo da ricordare

Obiettivo originario del `CIS`:

- costruire una piattaforma locale assistita da AI per ricerca commerciale mirata e generazione di contatti altamente qualificati
- mantenere `human in the loop` su ogni azione esterna
- rendere riusabile il sistema su progetti diversi tramite configurazioni di progetto
- arrivare almeno a un flusso minimo completo: discovery -> import -> arricchimento -> qualificazione -> bozza outreach -> storico minimo

Questo obiettivo oggi puo essere considerato il perimetro di `CIS 1.0`.

## Stato reale al 2026-04-30

### Sintesi

Lo sviluppo ordinato della roadmap e stato interrotto durante l'uso reale sul progetto `ethics`.

Da quel momento il `CIS` ha continuato a evolvere in parallelo tra:

- completamento di parte della roadmap originale
- aggiunte operative emerse dall'uso reale
- prima estensione verso modulo `Preventivi`

Il risultato pratico e questo:

- `CIS 1.0` esiste ed e gia usabile come sistema locale `human in the loop`
- il flusso minimo e stato portato oltre il solo MVP dati/dashboard
- non tutta la roadmap originale e stata completata
- alcune parti previste sono rimaste indietro
- alcune parti fuori roadmap sono gia entrate nel prodotto

### Stato per passo

Legenda:

- `fatto`: implementato e presente in codice o test/documentazione operativa
- `parziale`: presente in forma minima o implicita, ma non come modulo pienamente chiuso
- `non fatto`: non risulta implementato come parte distinta
- `superato`: il lavoro reale ha preso una forma diversa rispetto al passo originario

#### Fase 1 - Fondazioni

1. `fatto`
2. `fatto`
3. `fatto`
4. `fatto`

#### Fase 2 - Dati e configurazione

5. `fatto`
6. `fatto`
7. `fatto`
8. `fatto`
9. `fatto`
10. `fatto`

#### Fase 3 - Prima applicazione funzionante

11. `fatto`
12. `fatto`
13. `fatto`
14. `fatto`
15. `fatto`

#### Fase 3 bis - Consolidamento operativo prima dei Workbot

16. `fatto`
17. `fatto`
18. `fatto`
19. `fatto`
20. `fatto`
21. `fatto`

#### Fase 4 - Workbot essenziali

22. `fatto`
22bis. `fatto`
22tris. `fatto`
22 quater. `fatto`
22 quinquies. `fatto`
23. `fatto`
24. `fatto`
25. `fatto`
26. `non fatto`
27. `fatto`
28. `fatto`
29. `non fatto`
30. `parziale`

#### Fase 5 - Rifinitura e consolidamento

31. `parziale`
32. `parziale`
33. `fatto`
34. `fatto`
35. `fatto`
36. `non fatto`

### Cosa considerare chiuso per CIS 1.0

Per il `CIS 1.0` si possono considerare sostanzialmente chiusi:

- fondazioni architetturali locali `Flask + SQLite + configurazioni per progetto`
- gestione manuale `organizations` e `contacts`
- import CSV
- selezione progetto attivo
- `WB0` come filtro operativo prima del database
- `WB1` come arricchimento manuale o assistito
- qualificazione lead semplice
- `WB4` con bozza outreach modificabile e storico minimo
- uso reale del sistema su `ethics`

### Gap ancora aperti rispetto all'obiettivo originario

Restano aperti o incompleti, rispetto al traguardo iniziale:

- `WB3 Strategy Builder` come modulo esplicito
- `WB5 Follow-up Planner` come modulo esplicito
- `relationship_memory` come funzione davvero operativa e non solo appoggiata alle note
- rifinitura finale di UX e logging come fase deliberata di consolidamento
- piano scritto di introduzione `LLM` coerente con l'architettura

## Fasi aggiunte fuori roadmap originaria

Durante l'uso reale sono emerse fasi non previste o non prioritarie nella roadmap iniziale.

### Fase A - Roadmap 2 settimane su profili WB0/WB1

Questa fase e da considerare `fatta`.

Ha introdotto:

- `workbot_profiles.json` per progetto
- affinamento operativo di `WB0` e `WB1`
- profili reali per `melodema` e `ethics`
- riallineamento dei prompt preview al lavoro commerciale reale

### Fase B - Uso operativo reale su Ethics

Questa fase e da considerare `fatta`.

Ha prodotto:

- verifica concreta del flusso `WB0 -> import -> WB1 -> qualificazione -> prossimo passo`
- adattamenti del modello ai lead `PdR125`
- documentazione operativa reale invece di pura pianificazione

### Fase C - Preventivi multi-progetto

Questa fase e `avviata`.

Ha introdotto:

- modello dati e UI per `quotes`
- configurazioni per progetto su listini e intake

Questa fase non faceva parte dell'obiettivo iniziale `CIS 1.0`, ma nasce dall'evoluzione verso gestione commerciale piu completa.

## Roadmap aggiornata per chiudere CIS 1.0

Ordine pragmatico consigliato:

1. chiudere `WB3 Strategy Builder` in forma minima e leggibile
2. chiudere `WB5 Follow-up Planner` in forma minima e leggibile
3. rendere `relationship_memory` esplicita e consultabile
4. fare un passaggio breve ma intenzionale su UX, logging e error handling
5. scrivere un piano `PHASE2_LLM` che distingua bene cosa resta locale e cosa puo usare cloud

## Nota di riallineamento prima del CIS 2.0

Durante l'uso del `CIS 1.0` e diventato chiaro un punto importante:

- `WB0` nel `1.0` e utile, ma resta soprattutto un assistente per ricerca manuale e review
- l'idea originaria dell'utente era piu forte: impostare criteri e lasciare a `WB0` il compito di aiutare davvero a trovare candidati sul web

Quindi la prima priorita del `CIS 2.0` non deve essere solo "piu review", ma:

- trasformare `WB0` in un workbot capace di partire da una missione di ricerca
- generare query e task di ricerca riusabili
- raccogliere evidenze e candidati in forma strutturata
- lasciare all'umano la selezione finale e l'orchestrazione

## Punto di uscita da CIS 1.0

`CIS 1.0` puo considerarsi completato quando saranno vere queste condizioni:

1. il flusso discovery -> import -> arricchimento -> qualificazione -> strategy -> bozza -> follow-up e coperto almeno in forma minima
2. ogni passaggio resta tracciabile e approvato dall'umano
3. le note relazionali non vivono solo in testo libero ma in una memoria commerciale piu leggibile
4. la documentazione distingue chiaramente MVP chiuso e fase successiva

Da qui in poi il progetto puo passare in modo ordinato a `CIS 2.0`.

## Checklist numerata

### Fase 1 - Fondazioni

1. Definire il perimetro MVP.
Prompt:

```text
Leggi i PRD del progetto CIS e crea un file MVP_SCOPE.md con il perimetro della prima versione: obiettivi, funzionalita incluse, funzionalita escluse, utente target, criterio di completamento.
```

2. Creare la struttura iniziale del progetto software.
Prompt:

```text
Crea lo scheletro iniziale del progetto CIS in una nuova cartella software, con struttura ordinata per app Flask locale: app, templates, static, data, projects, tests, docs. Aggiungi anche README.md e .gitignore.
```

3. Preparare l'ambiente Python.
Prompt:

```text
Nella cartella software prepara un ambiente Python minimale per Flask e SQLite. Crea requirements.txt e spiega come avviare l'ambiente in locale.
```

4. Creare il documento di architettura tecnica iniziale.
Prompt:

```text
Crea docs/ARCHITECTURE.md con una versione semplice dell'architettura CIS: Human Orchestrator, Workbot Layer, Data Layer, Local Web Interface, e spiega responsabilita e confini di ogni livello.
```

### Fase 2 - Dati e configurazione

5. Modellare il database SQLite.
Prompt:

```text
Implementa il primo modello dati del CIS con SQLite partendo dalle tabelle del PRD: organizations, contacts, campaigns, outreach_actions, messages, relationship_memory, assets. Crea schema SQL iniziale e una breve spiegazione.
```

6. Creare lo script di inizializzazione database.
Prompt:

```text
Aggiungi uno script semplice per creare il database SQLite locale a partire dallo schema. Deve essere eseguibile da terminale e salvare il db nella cartella data.
```

7. Definire la configurazione multi-progetto.
Prompt:

```text
Implementa la struttura projects/<nome_progetto>/ con file di configurazione iniziali: project_config.yaml, lead_scoring.yaml, target_sources.yaml, communication_style.yaml e cartella email_templates.
```

8. Creare un progetto di esempio reale.
Prompt:

```text
Crea un progetto di esempio dentro projects chiamato melodema, con configurazioni compilate in modo plausibile per la ricerca concerti di un coro.
```

9. Implementare il layer di accesso ai dati.
Prompt:

```text
Implementa un data access layer molto semplice per leggere e scrivere organizations, contacts e campaigns nel database SQLite. Mantieni il codice minimale e leggibile.
```

10. Aggiungere test minimi sul database.
Prompt:

```text
Aggiungi test minimi per verificare creazione database e operazioni base CRUD su organizations e contacts.
```

### Fase 3 - Prima applicazione funzionante

11. Creare la prima app Flask funzionante.
Prompt:

```text
Crea una app Flask minima con una homepage locale che confermi che il CIS e attivo, e istruzioni per avviarla.
```

12. Aggiungere la schermata elenco organizzazioni.
Prompt:

```text
Estendi l'app Flask con una pagina Organizations che legga i dati dal database e mostri la lista delle organizzazioni in modo semplice.
```

13. Aggiungere creazione manuale organizzazioni.
Prompt:

```text
Aggiungi alla dashboard una form semplice per inserire manualmente una organization nel database.
```

14. Aggiungere la pagina dettaglio organizzazione.
Prompt:

```text
Aggiungi una pagina di dettaglio organization con campi principali, contatti associati e note.
```

15. Implementare il primo workflow manuale di import lead.
Prompt:

```text
Implementa un flusso semplice per importare lead da CSV dentro organizations e contacts, con validazione minima e gestione errori leggibile.
```

### Fase 3 bis - Consolidamento operativo prima dei Workbot

16. Estendere la gestione manuale delle organization.
Prompt:

```text
Estendi la form manuale di creazione organization con i principali campi gia presenti nel database e aggiungi nella pagina dettaglio organization una form semplice per modificare manualmente questi campi: name, organization_type, sector, city, region, country, website, email, phone, notes.
```

17. Aggiungere la gestione manuale dei contatti associati a una organization.
Prompt:

```text
Aggiungi la gestione manuale dei contatti associati a una organization dalla pagina dettaglio, con creazione semplice di full_name, first_name, last_name, role, email, phone, linkedin_url e notes.
```

18. Aggiungere la modifica manuale dei contatti gia inseriti.
Prompt:

```text
Aggiungi la modifica manuale dei contatti gia inseriti nella pagina dettaglio organization, mantenendo il codice e l'interfaccia semplici.
```

19. Migliorare UX minima della dashboard operativa.
Prompt:

```text
Migliora la dashboard Flask mantenendo tutto semplice: navigazione chiara tra home, organizations e dettaglio organization, messaggi piu leggibili per salvataggio e import, e visualizzazione leggermente piu chiara dei dati principali.
```

20. Aggiungere logging e gestione errori minima dei flussi manuali.
Prompt:

```text
Aggiungi logging basilare e gestione errori leggibile per avvio app, import CSV, inserimento organization e gestione contatti, senza complicare l'architettura.
```

21. Preparare un dataset demo realistico e verificare il flusso manuale.
Prompt:

```text
Crea un dataset demo piccolo ma realistico per il progetto melodema e verifica il flusso manuale completo: import, inserimento organization, modifica organization, inserimento contatti, modifica contatti e visualizzazione in dashboard.
```

### Fase 4 - Workbot essenziali

22. Implementare WB0 in versione base.
Prompt:

```text
Implementa WB0 Target Discovery in versione base non-automatica: deve ricevere keyword e area geografica, produrre una lista strutturata di candidate organizations e salvare il risultato in un formato riusabile. Niente scraping complesso per ora.
```

22bis. Aggiungere modifica ed eliminazione dei risultati salvati di WB0.
Prompt:

```text
Estendi WB0 Target Discovery con una gestione semplice dei risultati gia salvati: visualizzazione piu chiara dell'ultimo run, possibilita di modificare manualmente i dati delle candidate organizations gia inserite e possibilita di eliminare un run salvato o resettare latest.json. Mantieni tutto locale, leggibile e senza complicare l'architettura.
```

22tris. Estendere WB0 a ricerca assistita non fragile.
Prompt:

```text
Estendi WB0 Target Discovery con una prima ricerca assistita non fragile: l'utente deve poter inserire o selezionare fonti e query manuali, raccogliere candidate organizations in modo guidato e salvare il risultato strutturato. Nessuno scraping complesso o autonomo; human in the loop sempre attivo.
```

22 quater. Rendere WB0 utile come filtro operativo prima del database CIS.
Prompt:

```text
Estendi WB0 Target Discovery in modo che le candidate organizations non siano solo un archivio di ricerca, ma un vero filtro operativo prima dell'import nel database CIS. Aggiungi per ogni candidate una verifica minima e una decisione manuale, con campi semplici come stato, fit, sito confermato, note di qualificazione e decisione finale. Permetti di marcare una candidate come da importare nel CIS, mantenendo separati discovery e database operativo. Mantieni tutto locale, leggibile, human in the loop e senza automazioni fragili.
```

22 quinquies. Rifattorizzare il run di WB0 per ricerca via chatbot e futura automazione.
Prompt:

```text
Rifattorizza la struttura del run di WB0 Target Discovery per renderla piu veloce da usare nella ricerca manuale via chatbot e piu adatta a evoluzioni future automatiche. Sostituisci i parametri attuali troppo sovrapposti con una struttura piu chiara che distingua almeno: obiettivo ricerca, contesto progetto, territorio target, tipi di target, fonti da interrogare, prompt di ricerca, varianti di prompt o query usate, criteri di inclusione, criteri di esclusione, candidate organizations e note di verifica. Mantieni tutto locale, leggibile, human in the loop e compatibile con il ruolo di WB0 come filtro operativo prima del database CIS.
```

23. Implementare WB1 in versione base.
Prompt:

```text
Implementa WB1 Contact Hunter in versione semplice: dato un lead gia presente, permetti di arricchirlo con email, telefono, referente, ruolo, sito e social. Inizia da inserimento manuale o semiautomatico, senza automazioni fragili.
```

24. Implementare WB2 Lead Qualifier.
Prompt:

```text
Implementa WB2 Lead Qualifier usando regole semplici configurabili dal file lead_scoring.yaml. Deve produrre lead_score, lead_label, motivazioni, rischi e azioni suggerite.
```

25. Mostrare il punteggio lead nella dashboard.
Prompt:

```text
Collega il Lead Qualifier alla dashboard e mostra score, label e motivazioni nella pagina organization.
```

26. Implementare WB3 Strategy Builder.
Prompt:

```text
Implementa WB3 Strategy Builder in forma iniziale: per ogni lead qualificato suggerisci strategia di contatto, canale consigliato e motivo.
```

27. Implementare WB4 Outreach Drafter.
Prompt:

```text
Implementa WB4 Outreach Drafter per generare bozze di email partendo dai template del progetto e dai dati del lead. Le bozze devono essere sempre modificabili manualmente.
```

28. Salvare bozze e storico comunicazioni.
Prompt:

```text
Aggiungi il salvataggio delle bozze nel database usando messages e outreach_actions, e mostra lo storico nella pagina organization.
```

29. Implementare WB5 Follow-up Planner.
Prompt:

```text
Implementa WB5 Follow-up Planner in forma base: suggerisci quando ricontattare, con quale canale e con quale messaggio sintetico.
```

30. Implementare relationship memory.
Prompt:

```text
Implementa una prima versione di relationship_memory per salvare note relazionali, preferenze, esiti dei contatti e contesto utile per i follow-up.
```

### Fase 5 - Rifinitura e consolidamento

31. Rifinire UX minima della dashboard.
Prompt:

```text
Migliora la dashboard Flask mantenendo tutto semplice: navigazione chiara, home, organizations, dettaglio organization, campaigns e stato attivita.
```

32. Aggiungere logging e gestione errori.
Prompt:

```text
Aggiungi logging basilare e gestione errori leggibile per import, database, qualificazione e generazione bozze.
```

33. Preparare dati demo.
Prompt:

```text
Crea un dataset demo piccolo ma realistico per il progetto melodema, utile a testare end-to-end il flusso discovery > qualification > draft.
```

34. Eseguire il primo test end-to-end.
Prompt:

```text
Verifica e sistema il flusso completo minimo del CIS: creazione db, caricamento progetto melodema, inserimento lead, qualificazione, bozza outreach e visualizzazione in dashboard.
```

35. Documentare uso operativo.
Prompt:

```text
Crea docs/OPERATIONS.md pensato per un principiante: come avviare il progetto, creare il db, caricare un progetto, inserire lead, qualificare e generare bozze.
```

36. Preparare la fase 2 con LLM.
Prompt:

```text
Crea docs/PHASE2_LLM.md con un piano prudente per introdurre LLM locali o cloud in WB2, WB3 e WB4 senza rompere l'architettura attuale.
```

## Ordine consigliato

Se vuoi procedere in modo prudente, completa prima i passi da 1 a 15. A quel punto avrai una base reale: struttura software, database, configurazioni, app Flask e gestione manuale dei lead.

Prima di passare ai workbot, completa i passi da 16 a 21 per consolidare l'operativita manuale.

Solo dopo passa ai workbot da 22 a 30.

## Obiettivo intermedio consigliato

Il primo traguardo concreto da raggiungere e questo:

- avvio locale dell'app
- database creato correttamente
- progetto `melodema` configurato
- inserimento manuale di organizzazioni e contatti
- visualizzazione dati in dashboard

Quando questo funziona, il CIS smette di essere solo un'idea e diventa una base software reale.
