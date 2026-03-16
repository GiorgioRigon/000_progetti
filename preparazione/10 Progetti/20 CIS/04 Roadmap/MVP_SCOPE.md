---
title: CIS MVP Scope
type: scope
project: CIS
status: draft
created: 2026-03-16
updated: 2026-03-16
tags:
  - mvp
  - scope
  - cis
---

# CIS MVP Scope

Tag: #mvp #scope #cis

## Contesto

Questo documento definisce il perimetro della prima versione del Commercial Intelligence System (CIS), ricavato dai PRD del progetto.

Il principio guida dell'MVP e semplice:

- costruire una base software locale utile davvero
- mantenere il controllo umano completo
- privilegiare dati, struttura e workflow chiari prima di aggiungere automazioni piu avanzate

## Obiettivi dell'MVP

L'MVP deve permettere a un singolo utente di:

- gestire un progetto commerciale configurabile
- raccogliere e salvare organizzazioni e contatti in modo strutturato
- qualificare manualmente o con regole semplici i lead
- preparare bozze di comunicazione personalizzabili
- consultare tutto in una dashboard locale minimale

Obiettivi pratici:

- ridurre il tempo di raccolta e organizzazione dei lead
- migliorare la qualita della selezione
- conservare memoria minima delle relazioni
- rendere riusabile il sistema su piu progetti

## Utente target

Utente principale dell'MVP:

- professionista singolo o piccola attivita che svolge ricerca commerciale qualificata

Profilo operativo:

- usa il sistema in locale
- decide manualmente tutte le azioni esterne
- vuole un assistente interno, non un sistema autonomo

Esempi coerenti con il PRD:

- ricerca concerti per un coro
- ricerca clienti per consulenza
- scouting di partner o opportunita mirate

## Funzionalita incluse

### 1. Gestione base del progetto

L'MVP include:

- struttura per progetti separati
- configurazioni dedicate per progetto
- almeno un progetto esempio utilizzabile

File attesi per progetto:

- `project_config.yaml`
- `lead_scoring.yaml`
- `target_sources.yaml`
- `communication_style.yaml`
- cartella `email_templates/`

### 2. Database locale

L'MVP include:

- database SQLite locale
- schema iniziale per organizzazioni, contatti, campagne, azioni, messaggi e memoria relazionale
- script semplice di inizializzazione database

### 3. Gestione dati commerciali essenziali

L'MVP include:

- inserimento manuale di organizzazioni
- inserimento manuale di contatti
- associazione contatti-organizzazioni
- import base da CSV, se sostenibile senza complessita eccessiva

### 4. Dashboard locale minimale

L'MVP include:

- homepage locale
- elenco organizzazioni
- pagina dettaglio organizzazione
- visualizzazione delle informazioni principali del lead

Stack previsto:

- Python
- Flask
- HTML templates

### 5. Qualificazione lead semplice

L'MVP include:

- scoring iniziale basato su regole configurabili
- assegnazione di uno score
- etichetta del lead
- motivazioni e rischi sintetici
- azione suggerita

### 6. Supporto alla comunicazione

L'MVP include:

- generazione di bozze di outreach
- uso di template per progetto
- modifica manuale delle bozze prima di qualsiasi utilizzo
- salvataggio dello storico minimo delle bozze

### 7. Memoria commerciale essenziale

L'MVP include:

- note relazionali base
- esiti dei contatti
- promemoria o suggerimenti di follow-up semplici

## Funzionalita escluse

Queste funzioni non fanno parte della prima versione:

- invio automatico di email o messaggi
- contatto automatico dei prospect
- pipeline commerciale completa
- gestione offerte o preventivi
- negoziazione assistita avanzata
- scheduling automatico
- call assistant completo
- scraping complesso e fragile su larga scala
- automazioni ad alto volume
- supporto multiutente
- autenticazione complessa
- integrazioni esterne avanzate con CRM, email provider o calendari
- uso obbligatorio di LLM locali o cloud nella prima release

## Vincoli dell'MVP

I vincoli da rispettare sono:

- human in the loop sempre attivo
- local first per dati e interfaccia
- architettura semplice e leggibile
- modularita per supportare piu progetti in futuro
- priorita ai dati e alla tracciabilita rispetto all'automazione

## Criterio di completamento

L'MVP puo considerarsi completato quando sono vere tutte queste condizioni:

1. Esiste una applicazione locale avviabile con homepage funzionante.
2. Il database SQLite viene creato correttamente da uno script dedicato.
3. Esiste almeno un progetto configurato, ad esempio `melodema`.
4. L'utente puo inserire e consultare organizzazioni e contatti.
5. Il sistema puo assegnare una qualificazione base a un lead tramite regole semplici.
6. Il sistema puo generare e salvare una bozza di comunicazione modificabile manualmente.
7. La dashboard mostra almeno home, elenco organizzazioni e dettaglio organizzazione.
8. Nessuna azione esterna viene eseguita automaticamente.

## Definizione pratica di successo

Una dimostrazione minima di successo dell'MVP e questa:

- avvio dell'app locale
- creazione del database
- caricamento di un progetto
- inserimento o import di alcuni lead
- visualizzazione dei lead in dashboard
- qualificazione base di almeno un lead
- generazione di una bozza di outreach
- salvataggio dello storico minimo

Se questo flusso funziona da inizio a fine, l'MVP ha raggiunto il suo scopo.
