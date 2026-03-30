---
title: CIS - Roadmap 2 settimane profili WB
type: roadmap
project: CIS
status: attivo
created: 2026-03-30
updated: 2026-03-30
tags:
  - roadmap
  - cis
  - wb0
  - wb1
  - profili-operativi
---

# CIS - Roadmap 2 settimane profili WB

Obiettivo pratico: rendere `WB0` e `WB1` riusabili in tempi brevi su piu contesti, in particolare sul progetto consulenza certificazione, mantenendo il perimetro MVP, il database unico CIS e il controllo umano sempre attivo.

## Confini da rispettare

- nessuna automazione esterna obbligatoria
- nessun cambio di perimetro MVP non dichiarato
- database unico `CIS`
- architettura semplice e leggibile
- workbot generici con input specifici per progetto o campagna
- output usabili subito per attivita manuale con chatbot o ricerca umana

## Esito atteso a fine 2 settimane

- `WB0` e `WB1` leggono un profilo operativo per progetto
- esistono almeno due profili reali: `melodema` e `consulenza_certificazione`
- i prompt preview diventano piu utili, dettagliati e trasferibili
- il flusso manuale e usabile per ricerca target e ricerca referenti nel dominio certificazione
- eventuali dati specifici per qualificazione certificazioni sono gestiti in modo semplice e sostenibile

## Settimana 1

### Step 1 - Introdurre il profilo operativo dei workbot

Obiettivo:

- definire una struttura minima per i profili `WB0` e `WB1`
- salvare i profili nei file di progetto
- usare i profili dentro i prompt preview esistenti

Output atteso:

- file profilo per progetto
- parser minimale lato app
- prompt preview `WB0` e `WB1` arricchiti dai profili

Vincolo:

- nessuna modifica al database in questo step

### Step 2 - Creare i primi due profili reali

Obiettivo:

- compilare un profilo `melodema`
- compilare un profilo `consulenza_certificazione`

Contenuti minimi:

- focus operativo
- target prioritari
- criteri inclusione ed esclusione
- segnali di buon fit
- ruoli prioritari
- fonti da controllare
- dati minimi obbligatori
- checklist verifica umana

Output atteso:

- due profili concreti e modificabili
- base pronta per test operativi reali

### Step 3 - Rifinire input e prompt di `WB1`

Obiettivo:

- migliorare il brief `WB1` per ricerca referente e contatti
- chiarire meglio cosa cercare e cosa salvare

Possibili interventi:

- campi piu chiari nella UI
- prompt preview piu guidato
- distinzione piu esplicita tra dati organizzazione, dati referente e note di verifica

Output atteso:

- `WB1` piu usabile per lavoro manuale immediato

## Settimana 2

### Step 4 - Rifinire input e prompt di `WB0`

Obiettivo:

- migliorare il brief `WB0` per discovery target in ambiti diversi
- rendere piu chiara la fase di filtro operativo prima dell'import nel CIS

Possibili interventi:

- migliore formulazione del prompt preview
- campi piu chiari per candidati e criteri
- miglior allineamento tra profilo operativo e review manuale

Output atteso:

- `WB0` piu riusabile nel caso coro e nel caso consulenza

### Step 5 - Gestire i dati minimi di qualificazione certificazione

Obiettivo:

- decidere come tracciare in modo semplice i dati utili alla qualificazione lead nel dominio certificazioni

Scelta preferita:

- prima valutare salvataggio semplice e leggibile in note strutturate
- aggiungere pochi campi dedicati solo se servono davvero subito

Esempi dati:

- interesse verso `PdR125`
- stato certificazione noto o ipotizzato
- altre certificazioni rilevanti
- note di qualificazione

Output atteso:

- soluzione minima ma usabile, senza introdurre complessita non necessaria

### Step 6 - Prova operativa reale sul progetto consulenza certificazione

Obiettivo:

- usare davvero il CIS sul caso piu urgente
- verificare attriti, mancanze e punti da correggere

Test minimo:

- definizione campagna
- `WB0` per trovare target
- import nel CIS
- `WB1` per trovare referente e contatti
- salvataggio dei dati utili alla qualificazione

Output atteso:

- sistema utilizzabile davvero
- lista corta di correzioni ad alto impatto

### Step 7 - Consolidamento finale

Obiettivo:

- correggere gli attriti emersi nei test
- fissare le decisioni stabili nella memoria del progetto

Output atteso:

- `docs/DEVELOPMENT_NOTES.md` aggiornato
- profili e prompt puliti
- flusso manuale pronto per uso operativo immediato

## Ordine di esecuzione consigliato

1. Step 1
2. Step 2
3. Step 3
4. Step 4
5. Step 5
6. Step 6
7. Step 7

## Criterio pratico di successo

Questa roadmap ha successo se entro due settimane il CIS consente di:

- lavorare su almeno due domini diversi senza riscrivere i workbot
- generare brief utili e coerenti per lavoro manuale
- trovare target e referenti in modo ordinato
- salvare i risultati nel database unico `CIS`
- mantenere controllo umano e semplicita architetturale
