---
title: CIS - Domande iniziali
type: discovery
project: CIS
status: attivo
created: 2026-03-13
updated: 2026-03-13
tags:
  - discovery
  - ai
  - sales
  - cis
---

# CIS - Domande iniziali

Tag: #discovery #ai #sales #cis

## Indice

- [[../00 CIS Home|CIS Home]]
- [[260313 Prompt Iniziale|Prompt iniziale]]
- [[../02 PRD/260313 CIS PRD|PRD v0.1]]

## 1. Modello commerciale del sistema

Il sistema deve supportare **che tipo di attività commerciale?**

Nel tuo caso vedo tre possibilità.

### Modello A - Procacciamento opportunità

Tu trovi opportunità per un'organizzazione.

Esempi:

- concerti per il coro
- clienti per consulenza certificazione

Il tuo lavoro è:

- trovare lead
- qualificare
- creare contatto
- eventualmente preparare la trattativa

### Modello B - Generazione contatti qualificati

Il sistema produce **lead qualificati** per un cliente.

Esempio:

azienda X vuole clienti -> tu generi contatti.

### Modello C - Gestione commerciale completa

Il sistema supporta anche:

- trattativa
- negoziazione
- preventivi
- follow up avanzato

### Domanda aperta

Quale modello deve supportare il sistema: `A`, `B`, `C` oppure `A+B`?

## 2. Struttura universale del sistema

Il sistema deve funzionare per **tipi di business diversi**.

Quindi dobbiamo capire cosa cambia tra un progetto e l'altro.

| elemento | cambia? |
| --- | --- |
| target cliente | si |
| fonti prospect | si |
| criteri qualificazione | si |
| email | si |
| workflow | quasi uguale |

Io immagino una struttura tipo:

```text
projects/
    melodema/
    consulenza_certificazione/
```

Dentro ogni progetto:

```text
project_config.yaml
lead_scoring.yaml
email_templates/
target_sources/
```

I workbot restano gli stessi.

### Domanda aperta

Preferisci che il sistema sia organizzato per:

- progetti
- tipi di industria
- clienti

## 3. Livello reale di automazione

Qui dobbiamo essere molto realistici.

### Livello 1 - Assistente commerciale

AI:

- trova prospect
- prepara email
- suggerisce follow-up

Tu:

- decidi tutto
- invii email
- gestisci CRM

### Livello 2 - Automazione parziale

AI:

- prepara email
- gestisce pipeline
- invia alcune comunicazioni

Tu:

- supervisioni
- intervieni nelle fasi chiave

### Livello 3 - Automazione alta

AI:

- ricerca
- contatto
- follow-up
- scheduling

Tu:

- supervisioni la strategia

### Domanda aperta

L'obiettivo iniziale consigliato resta il `Livello 1`. Confermare o ridefinire.
