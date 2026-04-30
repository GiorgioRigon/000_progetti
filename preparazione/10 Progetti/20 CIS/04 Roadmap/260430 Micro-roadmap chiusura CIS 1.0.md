---
title: CIS 1.0 - Micro-roadmap di chiusura
type: roadmap
project: CIS
status: attivo
created: 2026-04-30
updated: 2026-04-30
tags:
  - cis
  - roadmap
  - cis-1-0
  - wb3
  - wb5
---

# CIS 1.0 - Micro-roadmap di chiusura

## Scopo

Chiudere `CIS 1.0` nel modo piu rapido e ordinato possibile, senza allargare il perimetro.

Principio guida:

- `WB3` e `WB5` non vanno sviluppati come workbot evoluti
- vanno sviluppati come prototipi minimi ma reali
- devono gia interpretare il ruolo che avranno in `CIS 2.0`
- non devono introdurre nuova architettura agentica, automazioni esterne o dipendenze non necessarie

In pratica:

- in `CIS 1.0` chiudiamo il flusso
- in `CIS 2.0` evolveremo l'autonomia e l'orchestrazione

## Cosa significa qui "minimo sindacale"

Per `WB3` e `WB5`, "minimo sindacale" significa:

- interfaccia visibile in scheda `organization`
- input molto semplici
- output strutturato e salvabile
- logica iniziale rule-based o template-based
- nessuna pretesa di intelligenza avanzata
- utilita operativa immediata

Non significa:

- mock vuoti
- testo libero senza struttura
- funzioni solo documentate ma non usabili

## Obiettivo di chiusura CIS 1.0

Il `CIS 1.0` e chiuso quando il flusso minimo diventa:

- `WB0` trova
- `WB1` arricchisce
- qualificazione decide se vale la pena procedere
- `WB3` suggerisce come attaccare il lead
- `WB4` prepara la prima bozza
- `WB5` suggerisce il follow-up
- `relationship_memory` conserva il contesto minimo utile

## Micro-roadmap in 4 step

### Step 1 - WB3 prototipo minimo

Obiettivo:

- introdurre `WB3 Strategy Builder` come suggeritore minimo del prossimo approccio commerciale

Output minimo richiesto:

- canale consigliato
- motivo del canale
- angolo commerciale
- rischio o cautela
- prossimo passo consigliato

Logica iniziale consigliata:

- regole semplici basate su dati gia presenti
- tipo contatto disponibile
- ruolo del contatto
- fit/priorita
- presenza di email diretta o solo casella generale
- eventuali segnali `PdR125`, `HR`, `ESG`, governance

Perimetro da non superare:

- niente LLM obbligatorio
- niente automazione esterna
- niente strategy engine complesso

Criterio di completamento:

- dalla scheda `organization` posso generare e salvare una strategia minima leggibile

### Step 2 - WB5 prototipo minimo

Obiettivo:

- introdurre `WB5 Follow-up Planner` come suggeritore minimo del passo successivo dopo il primo contatto o in assenza di risposta

Output minimo richiesto:

- data o finestra follow-up
- canale consigliato
- micro-script o nota sintetica
- motivo del follow-up
- stato operativo successivo

Logica iniziale consigliata:

- regole semplici basate su:
- esistenza o meno di bozza outreach
- canale usato o previsto
- tipo contatto
- stato qualitativo del lead

Perimetro da non superare:

- niente sequenze automatiche
- niente invio
- niente calendari esterni
- niente reminder infrastrutturali complessi

Criterio di completamento:

- dalla scheda `organization` posso generare e salvare un follow-up minimo coerente

### Step 3 - Relationship memory minima ma vera

Obiettivo:

- rendere la memoria relazionale esplicita, visibile e usabile

Decisione pragmatica:

- non costruire ora un CRM complesso
- usare un modello minimo e leggibile
- salvare elementi che servono davvero a `WB3`, `WB4` e `WB5`

Contenuti minimi utili:

- preferenze di canale
- note sul tono
- esito contatto
- cautela commerciale
- ultimo passo fatto
- prossimo passo concordato o suggerito

Forma consigliata:

- se basta, usare inizialmente le tabelle gia esistenti con vista dedicata
- aggiungere struttura solo dove migliora davvero leggibilita e riuso

Criterio di completamento:

- la scheda `organization` mostra una memoria commerciale distinta dalle note generiche

### Step 4 - Consolidamento finale corto

Obiettivo:

- chiudere `CIS 1.0` senza lasciare attriti evidenti

Da fare:

- sistemare test rotti o disallineati
- coprire con test minimi `WB3` e `WB5`
- fare pulizia breve della UI dove serve
- chiarire la documentazione finale del perimetro `1.0`

Da non fare:

- redesign
- nuova architettura
- integrazioni esterne
- introduzione anticipata del runtime agenti

Criterio di completamento:

- il flusso end-to-end e coerente e verificabile

## Ordine operativo consigliato

1. `WB3`
2. `WB5`
3. `relationship_memory`
4. consolidamento e test

Questo ordine e il piu efficiente perche:

- `WB3` chiarisce la logica commerciale prima della memoria
- `WB5` completa il ciclo di contatto
- `relationship_memory` puo essere modellata meglio dopo aver visto cosa serve davvero ai due prototipi

## Stima pragmatica

Se difendiamo bene il perimetro:

- `WB3` minimo: piccolo
- `WB5` minimo: piccolo
- `relationship_memory` minima: medio
- consolidamento: piccolo-medio

Totale:

- chiusura rapida `CIS 1.0`: poche sessioni ben focalizzate

## Confine da non violare

Se durante questi step compare uno di questi desideri, stiamo gia entrando in `CIS 2.0`:

- agenti autonomi
- task queue
- orchestrazione multi-run
- cost accounting per modello
- canali esterni operativi
- LLM locali come componente strutturale
- automazioni web robuste

In quel caso bisogna fermarsi e spostare il lavoro nella roadmap `CIS 2.0`.

## Formula pratica

`CIS 1.0` deve chiudere il significato dei ruoli.

`CIS 2.0` si occupera di chiudere l'autonomia dei ruoli.

Questa e la distinzione giusta.
