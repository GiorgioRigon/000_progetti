---
title: Roadmap progetto Melodema
type: roadmap
project: CIS
subproject: melodema
status: draft
created: 2026-04-25
updated: 2026-04-25
tags:
  - cis
  - roadmap
  - melodema
  - outreach
---

# Roadmap progetto Melodema

## Obiettivo

Costruire in 6-8 settimane una base lead pulita, qualificata e utilizzabile per una campagna commerciale verso enti e organizzazioni che possono ospitare o promuovere concerti del coro Melodema.

## Principio guida

Prima si normalizza la memoria storica, poi si espande il bacino.

Se si parte subito dalla ricerca di nuovi lead senza ripulire i dati esistenti, il rischio e accumulare altri doppioni, perdere storico utile e rallentare la qualifica.

## Unita logica da usare nel CIS

Per Melodema non basta ragionare in termini di singolo ente isolato.

Nei piccoli e medi comuni esiste spesso un `ecosistema locale di evento` in cui:

- il Comune finanzia o concede patrocinio
- la biblioteca funge da ufficio cultura operativo
- la parrocchia organizza direttamente
- la proloco coordina l'evento con supporto locale
- una associazione locale gestisce la parte pratica

Quindi uno stesso territorio puo richiedere piu interlocutori distinti e non va forzato dentro una sola organization.

### Organization

L'`organization` deve rappresentare il soggetto che puo concretamente diventare interlocutore commerciale o contenitore operativo del concerto.

Tipi iniziali consigliati:

- comune
- quartiere o circoscrizione
- parrocchia
- proloco
- associazione culturale
- associazione benefica
- fondazione
- biblioteca
- ente organizzatore

Regola pratica:

- usare il `comune` come organization quando il contatto e centralizzato o il Comune programma direttamente
- usare `quartiere` o `circoscrizione` solo nelle citta dove la programmazione culturale e davvero decentrata
- usare `parrocchia`, `proloco`, `associazione` come organization autonome quando organizzano eventi in proprio
- usare `biblioteca` come organization autonoma quando di fatto gestisce programmazione, ufficio cultura o calendario eventi

### Regola centrale per piccoli e medi comuni

Per `Comune X` possono coesistere legittimamente piu organization diverse:

- `Comune di X`
- `Biblioteca comunale di X`
- `Parrocchia di X`
- `Pro Loco di X`
- `Associazione culturale Y di X`

Queste non sono doppioni se hanno un ruolo organizzativo distinto.

Il territorio comune resta condiviso, ma l'interlocutore commerciale puo cambiare da caso a caso.

### Quando creare una nuova organization nello stesso comune

Creare una nuova `organization` se vale almeno una di queste condizioni:

- ha una propria email o telefono ufficiale
- ha un proprio sito o pagina istituzionale riconoscibile
- organizza eventi in autonomia o semi-autonomia
- compare come promotore, organizzatore o referente pubblico
- gestisce un calendario, una rassegna o una stagione distinta
- storicamente e stata il vero punto di accesso commerciale

Non creare una nuova organization separata se si tratta solo di:

- un singolo contatto interno a un ente gia censito
- un ufficio senza identita pubblica distinta
- una persona che cambia ruolo dentro la stessa struttura

### Contact

Il `contact` e il referente operativo o decisionale:

- assessore alla cultura
- ufficio cultura
- biblioteca
- parroco
- referente eventi
- presidente proloco
- responsabile raccolta fondi

### Relationship memory

Qui va salvato lo storico non strutturato ma commercialmente utile:

- concerto gia fatto
- contatto gia tentato
- risposta ricevuta
- periodo migliore per proporre
- preferenze sul tipo di repertorio o sul formato evento

## Tassonomia operativa minima

### `organization_type`

Valori iniziali consigliati:

- comune
- biblioteca
- parrocchia
- proloco
- associazione_culturale
- associazione_benefica
- fondazione
- diocesi
- santuario
- teatro_auditorium
- ente_organizzatore
- quartiere_circoscrizione

### `role_in_event`

Questo campo oggi puo stare nelle note o nel foglio master; in futuro potra diventare strutturato.

Valori consigliati:

- finanzia
- patrocina
- organizza
- co_organizza
- ospita
- programma
- segnala
- facilita_contatto

Regola pratica:

- una stessa organization puo avere piu ruoli
- se il ruolo non e certo, scrivere `probabile_organizza` o annotarlo in forma testuale

### `contact_role`

Ruoli da usare in modo coerente:

- assessore_cultura
- ufficio_cultura
- biblioteca_eventi
- parroco
- segreteria_parrocchiale
- presidente_proloco
- segreteria_proloco
- presidente_associazione
- direzione_artistica
- responsabile_eventi
- contatto_generale

### Territorio di riferimento

Ogni organization deve avere almeno:

- `city`
- `region`

Quando utile, aggiungere nelle note:

- frazione
- quartiere
- ambito pastorale
- diocesi di riferimento

## Convenzione di modellazione consigliata

Per Melodema conviene ragionare su due livelli:

1. `territorio`
2. `organization operative presenti nel territorio`

Il territorio ti dice dove vuoi entrare.

Le organization ti dicono chi devi contattare davvero.

In pratica:

- il Comune non e sempre il lead principale
- il Comune puo essere solo uno dei nodi dell'ecosistema locale
- la priorita commerciale va assegnata al soggetto che realisticamente organizza o apre la porta

## Roadmap per fasi

## Fase 1 - Censimento sorgenti e regole

Durata: 3-5 giorni

Output:

- elenco di tutti i file sorgente
- classificazione per affidabilita
- decisione sulle regole di deduplica
- vocabolario minimo dei tipi di organization
- convenzione esplicita per i casi con piu organization nello stesso comune

Attivita:

- raccogliere tutti gli Excel, CSV, note e rubriche usate negli ultimi anni
- assegnare a ogni sorgente una etichetta: affidabile, parziale, storico sporco
- definire chiavi pratiche per identificare i duplicati:
  - nome organization normalizzato
  - comune o citta
  - email
  - telefono
  - sito
- definire un dizionario iniziale dei tipi organization
- definire i ruoli evento minimi: finanzia, organizza, ospita, supporta
- decidere quali campi storici sono indispensabili e quali opzionali
- definire il criterio che separa organization autonoma da semplice contatto interno

Campi minimi consigliati:

- organization_name
- organization_type
- city
- region
- website
- organization_email
- organization_phone
- source
- organization_notes
- role_in_event
- related_territory
- contact_full_name
- contact_role
- contact_email
- contact_phone

## Fase 2 - Foglio master di normalizzazione

Durata: 1 settimana

Output:

- un file master unico da cui importare nel CIS
- prima deduplica consolidata

Attivita:

- creare un foglio master intermedio, non direttamente il database
- strutturare il master in modo che piu organization possano convivere nello stesso comune
- importare tutte le sorgenti nel master mantenendo la colonna `source_file`
- aggiungere colonne operative:
  - `raw_name`
  - `canonical_name`
  - `duplicate_group`
  - `organization_type`
  - `role_in_event`
  - `territory_key`
  - `parent_context`
  - `data_confidence`
  - `has_history`
  - `needs_manual_review`
- consolidare manualmente i duplicati piu evidenti
- mantenere una riga per organization e una logica chiara per i contatti multipli

Regola aggiuntiva:

- `Comune di X` e `Pro Loco di X` non sono duplicati solo perche condividono la stessa localita
- `Parrocchia di X` e `Biblioteca di X` vanno separate se hanno ruolo operativo distinto

Regola importante:

- non perdere il dato sporco originale
- normalizzare in nuove colonne, non sovrascrivere subito

## Fase 3 - Import storico nel CIS

Durata: 3-4 giorni

Output:

- primo database Melodema popolato
- organizations e contacts gia separati
- storico minimo salvato come note o relationship memory

Attivita:

- mappare il foglio master al formato CSV di import del CIS
- importare un primo batch piccolo di test
- verificare doppioni, encoding, campi vuoti, contatti orfani
- verificare che organization diverse nello stesso comune non vengano fuse per errore
- importare poi il batch completo pulito
- salvare le informazioni storiche piu utili nel campo `notes` o in `relationship_memory`

Ordine consigliato:

1. test con 20-30 organization
2. correzione mapping
3. import completo
4. controllo a campione

## Fase 4 - Qualifica lead Melodema

Durata: 1-2 settimane

Output:

- lead etichettati `hot`, `warm`, `cold`, `exclude`
- coda prioritaria per la campagna

Attivita:

- definire criteri pratici di fit per Melodema
- aggiungere o raffinare note di qualifica per ogni organization
- usare prima la memoria storica, poi la ricerca esterna
- distinguere chiaramente fra:
  - ente plausibile ma senza contatto
  - ente con contatto ma fit debole
  - ente con storico positivo
  - ente da escludere

Criteri iniziali suggeriti:

- fit artistico con musica corale o programmazione culturale
- sostenibilita geografica
- presenza di rassegne, eventi, feste patronali, raccolte fondi, stagioni culturali
- qualita del contatto disponibile
- presenza di relazione pregressa
- ruolo reale nell'ecosistema locale: chi decide, chi organizza, chi facilita

## Fase 5 - Arricchimento semi-automatico

Durata: continua, con primo sprint di 1 settimana

Output:

- lead prioritari con contatti migliori e note piu ricche

Attivita:

- usare `WB1` sui lead gia promettenti, non su tutto il database
- cercare per primi i 3-4 ruoli piu utili per tipo organization
- salvare email generale quando manca il nominativo, ma segnalarlo
- annotare la fonte del contatto e il livello di affidabilita

Priorita ricerca contatti:

- comuni: assessore cultura, ufficio cultura, eventi, biblioteca
- parrocchie: parroco, segreteria, responsabile eventi
- proloco: presidente, segreteria, contatti ufficiali
- associazioni: presidente, direzione artistica, raccolta fondi

Ordine consigliato nei piccoli e medi comuni:

1. identificare chi organizza davvero
2. verificare se il Comune paga, patrocina o ospita soltanto
3. cercare il referente del soggetto operativo prima del referente politico
4. salvare anche i soggetti secondari che possono sbloccare il contatto

## Fase 6 - Segmentazione campagna

Durata: 3-5 giorni

Output:

- 3-5 segmenti commerciali distinti
- messaggi e timing piu pertinenti

Segmenti possibili:

- piccoli comuni
- comuni medi con assessorato cultura
- parrocchie
- proloco
- associazioni per eventi benefit

Per ogni segmento definire:

- proposta di valore
- tipo di evento piu plausibile
- periodo dell'anno migliore
- tono del messaggio
- CTA iniziale

## Fase 7 - Pre-campagna

Durata: 1 settimana

Output:

- shortlist finale dei lead attaccabili subito
- bozze email pronte
- follow-up pianificati

Attivita:

- selezionare i lead `hot` e i migliori `warm`
- generare bozze email con `WB3`
- preparare una routine di follow-up semplice
- decidere soglia massima di lead per ondata iniziale

Volume consigliato:

- prima ondata: 20-40 lead ben qualificati
- seconda ondata: altri 20-40 dopo i primi riscontri

## Automazioni da fare per prime

Le prime automazioni utili non sono quelle di outreach, ma quelle di pulizia dati.

Priorita:

1. import da CSV con mapping stabile
2. rilevazione duplicati per nome + citta + email + telefono
3. normalizzazione tipi organization
4. coda di review manuale per record ambigui
5. scoring iniziale automatico con review umana finale

## Regole operative

- nessun invio automatico
- nessun import massivo senza batch test
- i lead senza fonte chiara restano in review
- lo storico concerti va preservato anche se incompleto
- i contatti generici non vanno scartati, ma marcati come deboli
- non fondere organization diverse solo perche appartengono allo stesso comune
- distinguere sempre fra chi finanzia, chi organizza e chi ospita

## Priorita pratica delle prossime 2 settimane

1. censire tutti i file sorgente reali del progetto Melodema
2. definire il foglio master unico
3. stabilire le regole di deduplica
4. fare un primo import test nel CIS
5. correggere il mapping
6. importare il primo nucleo pulito
7. qualificare il primo blocco di lead ad alta probabilita

## Definizione di successo della fase iniziale

La fase iniziale e riuscita quando hai:

- un archivio unico
- duplicati sotto controllo
- storico recuperato in forma leggibile
- almeno 30-50 organization qualificate in modo serio
- una shortlist pronta per la prima campagna

## Prossimo deliverable consigliato

Il prossimo deliverable concreto non dovrebbe essere ancora una campagna, ma questo:

`melodema_master_import.csv`

Deve diventare il ponte fra i fogli sparsi di oggi e il database CIS di domani.
