---
title: CIS - Progetto coro
type: use-case
project: CIS
status: attivo
created: 2026-03-13
updated: 2026-03-13
tags:
  - use-case
  - sales
  - music
  - choir
  - cis
---

# CIS - Progetto coro

Tag: #use-case #sales #music #choir #cis

## Indice

- [[../00 CIS Home|CIS Home]]
- [[../01 Discovery/260313 Prompt Iniziale|Prompt iniziale]]
- [[../02 PRD/260313 CIS PRD|PRD v0.1]]

## Sintesi

Non serve un agente AI generico, ma una micro-azienda commerciale orchestrata da te, con pochi workbot specializzati, un database leggero, una pipeline chiara e una interfaccia semplice.

Il cuore del sistema, almeno nella fase 1, deve fare tre cose:

- trovare enti plausibili
- raccogliere contatti utili
- preparare bozze di email personalizzate

Tutto il resto viene dopo.

## Visione del sistema

Il progetto può essere pensato come `Melodema Outreach Engine`, composto da quattro livelli:

1. dati
2. workbot
3. orchestratore umano
4. interfaccia semplice

La regola madre dovrebbe essere:

> nessun workbot invia nulla autonomamente.

I bot preparano, classificano, suggeriscono, aggiornano. Tu decidi.

## Architettura base dei workbot

### WB0 - Target Discovery

Scopo: costruire una lista iniziale di enti potenzialmente interessanti.

Output:

- elenco enti candidati con punteggio iniziale

### WB1 - Contact Hunter

Scopo: trovare i contatti utili per ogni ente.

Output:

- scheda contatto strutturata e normalizzata

### WB2 - Lead Qualifier

Scopo: capire se l'ente è davvero adatto a Melodema.

Output:

- punteggio lead
- motivazione sintetica
- etichetta: caldo, tiepido, freddo, da escludere

### WB3 - Outreach Drafter

Scopo: creare la prima email a freddo, personalizzata.

Output:

- oggetto
- email
- eventuale nota per telefonata successiva

### WB4 - Follow-up Planner

Scopo: suggerire il momento e il tipo di follow-up.

Output:

- data consigliata
- canale consigliato
- bozza follow-up
- stato lead aggiornato

### WB5 - Call Prep & Call Summary

Scopo: aiutarti prima e dopo le telefonate.
