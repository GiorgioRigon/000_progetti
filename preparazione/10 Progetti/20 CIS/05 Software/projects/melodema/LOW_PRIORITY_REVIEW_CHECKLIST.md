# Checklist review low priority Melodema

Questa checklist serve per smaltire i casi `low` rimasti dopo:

- import principale
- import supplementare `medium`
- attach queue `medium`

L'obiettivo non e analizzare tutto in profondita, ma prendere una decisione pratica veloce e coerente.

## File di partenza

Usa questi file:

- `projects/melodema/melodema_review_queue.csv`
- `projects/melodema/melodema_review_high_priority_prequalified.csv`

Se serve contesto aggiuntivo:

- `projects/melodema/Melodema_mega_file.xlsx`

## Esiti ammessi

Ogni riga deve finire in uno di questi esiti:

- `crea organization`
- `aggancia a organization esistente`
- `mantieni in review`
- `scarta`

Non lasciare righe in uno stato intermedio non dichiarato.

## Regola guida

Se non e chiaro chi organizza davvero, non inventare una organization.

Meglio:

- tenere la riga in review
- oppure agganciarla a un soggetto certo gia esistente

piuttosto che creare entita sbagliate.

## Procedura rapida per ogni riga

### 1. Identifica il soggetto reale

Chiediti:

- e un `Comune`?
- e una `Pro Loco`?
- e una `Parrocchia`?
- e una `Associazione`?
- e solo un luogo o venue?

Se la riga descrive solo un luogo:

- non creare organization solo per il luogo
- usa il luogo come nota o contesto

### 2. Identifica il miglior interlocutore

Chiediti:

- il contatto e comunale?
- il contatto e religioso?
- il contatto e associativo?
- e solo una persona in CC?
- e un contatto generale senza ruolo?

Se il contatto non identifica il soggetto:

- non usarlo da solo per creare una nuova organization

### 3. Cerca nel CIS se il territorio esiste gia

Prima di creare una nuova organization controlla se hai gia:

- `Comune di <X>`
- `Pro Loco di <X>`
- `Parrocchia di <X>`
- `Associazione <Y>`

Se il nodo territoriale o organizzativo esiste gia:

- privilegia `aggancia a organization esistente`

### 4. Applica la decisione

#### `crea organization`

Usa questo esito solo se:

- il soggetto e riconoscibile
- ha un ruolo operativo plausibile
- non e gia presente in modo equivalente

Esempi tipici:

- una parrocchia con parroco o unita pastorale chiara
- una associazione nominata esplicitamente
- una fondazione o ente organizzatore identificabile

#### `aggancia a organization esistente`

Usa questo esito se:

- email e contatti rimandano chiaramente a un ente gia presente
- il luogo e solo il contenitore dell'evento
- il soggetto reale e il Comune o la Pro Loco gia censiti

Esempi tipici:

- teatro con email comunale
- chiesa con contatto proloco
- venue con assessore cultura

#### `mantieni in review`

Usa questo esito se:

- il soggetto reale non e chiaro
- il contatto e troppo debole
- la riga mescola luogo, persona e organizzatore senza distinguerli

#### `scarta`

Usa questo esito se:

- non c'e un soggetto identificabile
- non c'e un contatto utile
- il dato non aggiunge valore rispetto a quanto gia presente

## Domande di controllo

Per ogni riga, rispondi rapidamente a queste domande:

1. il soggetto organizzatore e chiaro?
2. il contatto punta a un ente preciso?
3. il luogo e diverso dall'organizzatore?
4. esiste gia una organization equivalente nel CIS?
5. questa riga aggiunge un contatto utile oppure solo rumore?

Se almeno tre risposte restano dubbie:

- non creare una nuova organization

## Criteri di priorita anche nei low

Anche dentro i `low`, lavora prima:

- righe con email valida
- righe con telefono valido
- righe con soggetto plausibile ma incompleto

Lascia per ultimi:

- contatti in CC
- note senza organization
- venue senza soggetto operativo

## Note standard da usare

### Se agganci a ente esistente

```text
Contesto storico Melodema: <venue o raw_name>. La riga e stata agganciata a <organization> perche il soggetto operativo plausibile e questo ente.
```

### Se crei organization nuova

```text
Lead derivato da review low priority Melodema. Soggetto creato dopo verifica manuale del ruolo organizzativo plausibile.
```

### Se mantieni in review

```text
Review sospesa: non e ancora chiaro se il soggetto corretto sia <A>, <B> oppure il solo venue.
```

### Se scarti

```text
Scartato in review low priority: dato troppo ambiguo o non sufficientemente utile rispetto ai lead gia presenti.
```

## Casi tipici Melodema

### Caso 1

`Teatro` o `Sala` con email del Comune

Decisione tipica:

- `aggancia a organization esistente`

### Caso 2

`Chiesa` con nota che cita `Parrocchia` o `Unita Pastorale`

Decisione tipica:

- `crea organization`

solo se il soggetto religioso e davvero riconoscibile.

### Caso 3

`Chiesa` o `venue` con nota che cita `Pro Loco`, `Avis`, `Fidas`, `associazione`

Decisione tipica:

- `aggancia` o `crea organization`

in base a quanto e esplicito il soggetto associativo.

### Caso 4

Solo nome persona o solo luogo

Decisione tipica:

- `mantieni in review`
- oppure `scarta`

## Definizione di chiusura

La review low priority e chiusa quando:

- ogni riga ha un esito esplicito
- i casi utili sono stati agganciati o creati correttamente
- i casi ambigui residui sono pochi e motivati
- non restano venue trasformati in organization per errore

## Regola finale

Per Melodema il modello giusto non e:

- un luogo = una organization

Il modello giusto e:

- un territorio
- uno o piu soggetti organizzativi plausibili
- uno o piu contatti

Questa checklist serve proprio a difendere questa regola anche nei casi sporchi.
