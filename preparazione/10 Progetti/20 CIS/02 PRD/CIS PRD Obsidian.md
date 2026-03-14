---
title: CIS PRD Obsidian v0.2
type: prd
project: CIS
status: draft
version: "0.2"
created: 2026-03-13
updated: 2026-03-13
tags:
  - prd
  - ai
  - sales
  - agents
  - cis
---

# Commercial Intelligence System PRD

Tag: #prd #ai #sales #agents #cis

## Indice

- [[../00 CIS Home|CIS Home]]
- [[260313 CIS PRD|PRD v0.1]]
- [[../01 Discovery/260313 Prompt Iniziale|Prompt iniziale]]
- [[../01 Discovery/260313 Domande|Domande iniziali]]

## Sommario sezioni

- [[#1 Visione]]
- [[#2 Obiettivi]]
- [[#3 Principi fondamentali]]
- [[#4 Ambito funzionale]]
- [[#5 Struttura del progetto]]
- [[#6 Architettura del sistema]]
- [[#7 Architettura dei Workbot]]
- [[#8 Architettura LLM]]
- [[#9 Database]]
 - [[#10 Interfaccia utente]]
 - [[#11 Fonti dati]]
 - [[#12 Struttura del progetto software]]
 - [[#13 Privacy]]
 - [[#14 Roadmap di sviluppo]]
 - [[#15 Obiettivo finale]]

## Documento dei requisiti di prodotto

Version: 0.2  
Author: Giorgio

## 1 Visione

Il Commercial Intelligence System (CIS) è una piattaforma locale assistita da AI progettata per supportare attività commerciali di ricerca ad alta qualità e lead generation.

Il sistema si concentra su:

- numero ridotto di lead
- analisi approfondita
- alta rilevanza
- outreach personalizzato

L'AI prepara. L'umano decide.

## 2 Obiettivi

Obiettivo principale:

Generare contatti commerciali altamente qualificati.

Esempi:

- opportunità di concerti per un coro
- clienti per consulenza
- partnership
- eventi culturali

Obiettivi secondari:

- ridurre il tempo di ricerca
- migliorare la qualità dei lead
- mantenere memoria delle relazioni
- supportare la preparazione delle comunicazioni
- suggerire strategie di contatto

## 3 Principi fondamentali

Qualità prima della quantità.

Campagna tipica:

30-100 lead.

Espandibile a:

300-500 lead con automazione.

Human in the loop.

L'AI non invia mai messaggi automaticamente.

I dati vengono prima dell'AI.

Il database è il nucleo del sistema.

Architettura modulare.

Supporto a più progetti commerciali.

## 4 Ambito funzionale

Modello iniziale:

Lead Generation qualificata.

Funzioni del sistema:

1. identificare opportunità  
2. raccogliere contatti  
3. valutare i lead  
4. preparare la comunicazione

Modulo futuro:

Gestione commerciale.

Funzionalità possibili:

- tracciamento delle negoziazioni
- proposte
- sales pipeline
- reporting

## 5 Struttura del progetto

Esempio cartella `projects`:

```text
projects/
    melodema/
    consulting_certification/
```

Ogni progetto contiene:

```text
project_config.yaml
lead_scoring.yaml
target_sources.yaml
communication_style.yaml
email_templates/
```

## 6 Architettura del sistema

Quattro livelli.

- Human Orchestrator
- Workbot Layer
- Data Layer
- Local Web Interface

## 7 Architettura dei Workbot

- WB0 Target Discovery
- WB1 Contact Hunter
- WB2 Lead Qualifier
- WB3 Strategy Builder
- WB4 Outreach Drafter
- WB5 Follow-up Planner
- WB6 Call Assistant
- WB7 CRM Memory Manager

## 8 Architettura LLM

Architettura ibrida.

Cloud LLM:

- system design
- debugging
- generazione di codice

Local LLM:

- classificazione
- summarization
- drafting
- scoring

## 9 Database

SQLite database.

Main tables:

- organizations
- contacts
- campaigns
- outreach_actions
- messages
- relationship_memory
- assets

## 10 Interfaccia utente

Dashboard locale.

Stack:

- Python
- Flask
- HTML

Schermate:

- Home
- Organizations
- profilo organizzazione

## 11 Fonti dati

Le fonti previste includono:

- siti web
- directory
- pagine pubbliche di contatto
- portali locali di eventi
- storico interazioni CRM

## 12 Struttura del progetto software

Struttura indicativa dell'applicazione:

```text
app/
data/
workbots/
templates/
static/
```

## 13 Privacy

I dati sensibili dovrebbero restare in locale quando possibile.

L'uso di Local LLM è preferibile per:

- drafting su dati privati
- classificazione interna
- elaborazione della memoria relazionale

## 14 Roadmap di sviluppo

Ordine suggerito:

1. modello dati
2. configurazione del progetto
3. workflow di lead discovery
4. qualificazione dei contatti
5. supporto al drafting
6. local dashboard

## 15 Obiettivo finale

Costruire un sistema operativo commerciale riusabile che supporti più progetti di outreach ad alta qualità, mantenendo sempre il controllo umano.
