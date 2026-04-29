# CIS Preventivi Module Proposal

Proposta di mini-architettura per un modulo `Preventivi` dentro il CIS.

## Obiettivo

Aggiungere al CIS un modulo locale per:

- raccogliere i dati necessari a preparare un preventivo
- salvare listini e pacchetti per progetto
- calcolare una prima bozza economica
- produrre un preventivo modificabile e tracciabile

Il modulo deve restare coerente con i principi gia adottati nel CIS:

- local first
- human in the loop
- stesso stack tecnico (`Python`, `Flask`, `SQLite`, `HTML`)
- stessa grafica e stessa navigazione del sistema
- riuso multi-progetto senza riscrivere il software per ogni caso

## Posizionamento nel CIS

Il modulo `Preventivi` non va pensato come estensione specifica di `ethics`, ma come componente generale del CIS.

La logica corretta e questa:

- motore comune del modulo dentro `app/`, `templates/`, `data/`
- configurazioni e listini specifici dentro `projects/<project_key>/`
- schede raccolta dati diverse per progetto, ma gestite dallo stesso flusso applicativo

Questo consente di usare lo stesso modulo per:

- `ethics`, con scheda `PdR125 / E-docs / E-KPI`
- `melodema`, con scheda eventi, repertorio, formazione, trasferte o altri elementi commerciali
- futuri progetti con logiche ancora diverse

## Principio di modellazione

Il modulo non deve imporre un unico schema rigido di campi valido per tutti i progetti.

Conviene separare:

1. dati comuni a ogni preventivo
2. configurazioni di progetto
3. dati specifici della singola opportunita

### 1. Dati comuni strutturati

Campi che ha senso tenere sempre strutturati:

- progetto attivo
- organization collegata
- titolo opportunita
- stato preventivo
- referente commerciale
- data richiesta
- data scadenza preventivo
- valuta
- imponibile
- sconto
- totale finale
- note interne
- note cliente
- versione

### 2. Configurazioni di progetto

Per ogni progetto conviene salvare:

- listino base
- pacchetti standard
- regole di prezzo
- testi standard
- condizioni commerciali
- eventuali campi richiesti nella scheda

Questa parte va fuori dal database centrale quando possibile, in file leggibili e modificabili a mano.

Esempi utili:

- `projects/ethics/quotation_config.yaml`
- `projects/ethics/price_list.yaml`
- `projects/melodema/quotation_config.yaml`
- `projects/melodema/price_list.yaml`

### 3. Dati specifici della scheda

I dati raccolti nella scheda non vanno tutti promossi subito a colonne SQL.

Per la prima versione conviene salvare:

- un nucleo minimo di colonne strutturate
- una scheda dettagliata in formato flessibile, per esempio JSON

Questo evita di irrigidire troppo il sistema su `ethics` e rende possibile avere schede molto diverse per `melodema`.

## Modello dati proposto

Per una prima implementazione sono sufficienti quattro nuove entita logiche.

### `quote_intakes`

Scheda raccolta dati prima del preventivo.

Campi minimi:

- `id`
- `project_key`
- `organization_id`
- `title`
- `status` (`draft`, `qualified`, `ready_for_quote`, `archived`)
- `intake_schema_key`
- `intake_data_json`
- `summary`
- `created_at`
- `updated_at`

Uso:

- contiene la scheda compilata
- puo partire da un template diverso per ogni progetto
- puo esistere anche senza preventivo gia emesso

### `quotes`

Testata del preventivo.

Campi minimi:

- `id`
- `project_key`
- `organization_id`
- `quote_intake_id`
- `quote_number`
- `title`
- `status` (`draft`, `internal_review`, `ready_to_send`, `sent`, `won`, `lost`)
- `currency`
- `subtotal_amount`
- `discount_amount`
- `total_amount`
- `valid_until`
- `version_label`
- `assumptions`
- `internal_notes`
- `client_notes`
- `created_at`
- `updated_at`

### `quote_line_items`

Righe economiche del preventivo.

Campi minimi:

- `id`
- `quote_id`
- `line_type` (`service`, `software`, `setup`, `training`, `travel`, `discount`, `custom`)
- `code`
- `title`
- `description`
- `quantity`
- `unit`
- `unit_price`
- `line_total`
- `sort_order`
- `pricing_source`
- `created_at`
- `updated_at`

### `quote_versions`

Snapshot testuale o JSON delle versioni emesse.

Campi minimi:

- `id`
- `quote_id`
- `version_label`
- `snapshot_json`
- `created_at`

Uso:

- conserva lo stato del preventivo in momenti chiave
- evita di perdere storico quando si ricalcola o si ritocca il documento

## Configurazione per progetto

Il cuore della riusabilita non e nel database, ma nella configurazione per progetto.

Per ogni `project_key` conviene introdurre:

### `quotation_config.yaml`

Serve a definire:

- nome commerciale del modulo
- tipi di scheda disponibili
- campi obbligatori
- pacchetti standard suggeriti
- condizioni standard
- regole di numerazione
- testo introduttivo e finale del preventivo

### `price_list.yaml`

Serve a definire:

- voci di listino
- codici
- unita di misura
- prezzi base
- fasce dimensionali
- regole di attivazione
- limiti di sconto

### `intake_schemas/*.yaml`

Serve a definire le schede dati.

Esempi:

- `projects/ethics/intake_schemas/pdr125_edocs.yaml`
- `projects/melodema/intake_schemas/evento_coro.yaml`

Ogni schema puo descrivere:

- sezioni
- campi
- tipo input
- opzioni selettive
- obbligatorieta
- aiuti testuali

## Flusso operativo consigliato

Flusso minimo dentro CIS:

1. selezione del progetto attivo
2. apertura organization gia esistente oppure creazione nuova opportunita
3. compilazione scheda `Preventivo`
4. salvataggio intake
5. generazione proposta economica da pacchetto o da righe manuali
6. revisione umana di importi, sconti, note e condizioni
7. salvataggio versione
8. marcatura stato: `ready_to_send` o `sent`

## UX minima

Schermate iniziali sufficienti:

- elenco preventivi del progetto attivo
- dettaglio intake
- editor preventivo
- vista stampabile o esportabile

Ingressi utili dalla UI gia esistente:

- pulsante `Nuovo preventivo` dalla scheda `organization`
- sezione `Preventivi` nel menu principale
- collegamento tra organization e storico preventivi

## Caso `ethics`

La scheda gia salvata in `30 Risorse/2026-04-21_scheda_dati_preventivo_su_misura_pdr125_e_docs_e_kpi.md` e una buona base per il primo `intake schema`.

Per `ethics` la prima configurazione puo prevedere:

- pacchetti `Start PdR125`, `Rinnovo Ordinato`, `Mantenimento Ordinato`, `Assistenza Audit`, `Pilota E-docs`, `Solo Consulenza`
- righe separate per consulenza, setup, caricamento iniziale, formazione, supporto ravvicinato
- regole di fascia basate su numero occupati, numero sedi, numero organizzazioni coinvolte, numero utenti, carico documentale e fabbisogno KPI

Per `ethics` conviene anche distinguere:

- parte software
- parte consulenza
- parte servizi iniziali
- eventuali spese vive escluse

## Caso `melodema`

`Melodema` conferma perche serve un motore comune ma configurabile.

Un preventivo `melodema` potrebbe dipendere da fattori come:

- tipo evento
- durata
- organico
- repertorio
- trasferte
- prove aggiuntive
- attrezzature
- formazione o laboratorio

Questi campi non hanno nulla a che fare con `ethics`, ma possono convivere bene nello stesso modulo se la scheda e configurabile per progetto.

## Rapporto con Excel

Excel puo essere utile come strumento ponte, ma non dovrebbe diventare il sistema principale.

Uso consigliato di Excel:

- import iniziale del listino
- export di controllo
- simulazioni temporanee

Uso sconsigliato di Excel:

- archivio master dei preventivi
- unica fonte di verita di schede, prezzi e versioni
- logica principale di calcolo

Se il cuore resta in Excel, CIS perderebbe continuita tra lead, organization, contatti, qualificazione, storico commerciale e proposta economica.

## Strategia di implementazione

Ordine pragmatico consigliato:

### Fase 1

MVP `Preventivi` solo per `ethics`, ma gia dentro architettura multi-progetto.

Obiettivo:

- scheda intake
- salvataggio preventivo
- righe manuali
- totali
- collegamento a organization

### Fase 2

Configurazione `price_list.yaml` e pacchetti standard `ethics`.

Obiettivo:

- precompilare il preventivo da regole semplici
- ridurre il lavoro manuale

### Fase 3

Secondo profilo progetto su `melodema`.

Obiettivo:

- verificare che il modello regga anche su un dominio commerciale molto diverso

### Fase 4

Export pulito del preventivo.

Obiettivo:

- stampa HTML
- eventuale PDF in fase successiva

## Decisione architetturale proposta

La soluzione raccomandata e:

- non costruire un sistema preventivi esterno come fonte primaria
- usare CIS come base applicativa comune
- rendere `Preventivi` un modulo del CIS
- mantenere dati comuni strutturati e dati specifici in schema configurabile per progetto

In sintesi:

`un solo motore software, molti profili progetto`
