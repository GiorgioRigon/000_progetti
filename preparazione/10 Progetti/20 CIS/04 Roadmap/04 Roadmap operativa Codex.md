---
title: CIS - Roadmap operativa Codex
type: roadmap
project: CIS
status: attivo
created: 2026-03-14
updated: 2026-03-14
tags:
  - roadmap
  - codex
  - cis
  - sviluppo
---

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

### Fase 4 - Workbot essenziali

16. Implementare WB0 in versione base.
Prompt:

```text
Implementa WB0 Target Discovery in versione base non-automatica: deve ricevere keyword e area geografica, produrre una lista strutturata di candidate organizations e salvare il risultato in un formato riusabile. Niente scraping complesso per ora.
```

17. Implementare WB1 in versione base.
Prompt:

```text
Implementa WB1 Contact Hunter in versione semplice: dato un lead gia presente, permetti di arricchirlo con email, telefono, referente, ruolo, sito e social. Inizia da inserimento manuale o semiautomatico, senza automazioni fragili.
```

18. Implementare WB2 Lead Qualifier.
Prompt:

```text
Implementa WB2 Lead Qualifier usando regole semplici configurabili dal file lead_scoring.yaml. Deve produrre lead_score, lead_label, motivazioni, rischi e azioni suggerite.
```

19. Mostrare il punteggio lead nella dashboard.
Prompt:

```text
Collega il Lead Qualifier alla dashboard e mostra score, label e motivazioni nella pagina organization.
```

20. Implementare WB3 Strategy Builder.
Prompt:

```text
Implementa WB3 Strategy Builder in forma iniziale: per ogni lead qualificato suggerisci strategia di contatto, canale consigliato e motivo.
```

21. Implementare WB4 Outreach Drafter.
Prompt:

```text
Implementa WB4 Outreach Drafter per generare bozze di email partendo dai template del progetto e dai dati del lead. Le bozze devono essere sempre modificabili manualmente.
```

22. Salvare bozze e storico comunicazioni.
Prompt:

```text
Aggiungi il salvataggio delle bozze nel database usando messages e outreach_actions, e mostra lo storico nella pagina organization.
```

23. Implementare WB5 Follow-up Planner.
Prompt:

```text
Implementa WB5 Follow-up Planner in forma base: suggerisci quando ricontattare, con quale canale e con quale messaggio sintetico.
```

24. Implementare relationship memory.
Prompt:

```text
Implementa una prima versione di relationship_memory per salvare note relazionali, preferenze, esiti dei contatti e contesto utile per i follow-up.
```

### Fase 5 - Rifinitura e consolidamento

25. Rifinire UX minima della dashboard.
Prompt:

```text
Migliora la dashboard Flask mantenendo tutto semplice: navigazione chiara, home, organizations, dettaglio organization, campaigns e stato attivita.
```

26. Aggiungere logging e gestione errori.
Prompt:

```text
Aggiungi logging basilare e gestione errori leggibile per import, database, qualificazione e generazione bozze.
```

27. Preparare dati demo.
Prompt:

```text
Crea un dataset demo piccolo ma realistico per il progetto melodema, utile a testare end-to-end il flusso discovery > qualification > draft.
```

28. Eseguire il primo test end-to-end.
Prompt:

```text
Verifica e sistema il flusso completo minimo del CIS: creazione db, caricamento progetto melodema, inserimento lead, qualificazione, bozza outreach e visualizzazione in dashboard.
```

29. Documentare uso operativo.
Prompt:

```text
Crea docs/OPERATIONS.md pensato per un principiante: come avviare il progetto, creare il db, caricare un progetto, inserire lead, qualificare e generare bozze.
```

30. Preparare la fase 2 con LLM.
Prompt:

```text
Crea docs/PHASE2_LLM.md con un piano prudente per introdurre LLM locali o cloud in WB2, WB3 e WB4 senza rompere l'architettura attuale.
```

## Ordine consigliato

Se vuoi procedere in modo prudente, completa prima i passi da 1 a 14. A quel punto avrai una base reale: struttura software, database, configurazioni, app Flask e gestione manuale dei lead.

Solo dopo passa ai workbot da 16 a 24.

## Obiettivo intermedio consigliato

Il primo traguardo concreto da raggiungere e questo:

- avvio locale dell'app
- database creato correttamente
- progetto `melodema` configurato
- inserimento manuale di organizzazioni e contatti
- visualizzazione dati in dashboard

Quando questo funziona, il CIS smette di essere solo un'idea e diventa una base software reale.
