# Procedura import Melodema

Questa procedura serve per caricare i lead Melodema nel `CIS` senza creare doppioni inutili e senza mischiare i casi puliti con quelli ancora ambigui.

## File da usare

### 1. Import principale

File:

- `projects/melodema/melodema_cis_import.csv`

Contenuto:

- base pulita principale
- `318` righe

Uso:

- importare per primo

### 2. Import supplementare

File:

- `projects/melodema/melodema_cis_import_supplement_medium.csv`

Contenuto:

- `5` lead recuperati dalla review alta priorita
- abbastanza solidi da entrare nel database

Uso:

- importare solo dopo il file principale

### 3. Queue attach manuale

File:

- `projects/melodema/melodema_attach_existing_queue_medium.csv`

Contenuto:

- `6` casi che non vanno importati come nuove organization
- servono per aggiungere contatti e note a organization gia presenti

Uso:

- non importare come CSV
- lavorare manualmente dopo gli import

## Ordine corretto

1. importare `melodema_cis_import.csv`
2. controllare il risultato
3. importare `melodema_cis_import_supplement_medium.csv`
4. controllare il risultato
5. lavorare `melodema_attach_existing_queue_medium.csv`

## Step 1 - Import principale

Importa:

- `projects/melodema/melodema_cis_import.csv`

Controlli subito dopo l'import:

- la lista organizations si apre senza errori
- compaiono sia `comune` sia `proloco`
- i record con contatto nominativo mostrano anche il contatto associato
- non ci sono organization palesemente vuote

Controlli a campione consigliati:

- `Comune di Arzignano`
- `Comune di Thiene`
- `Pro Loco di Brendola`
- `Pro Loco di Arcugnano`

Se trovi un doppione evidente:

- non reimportare subito
- annota il caso
- correggi prima il CSV o la scheda nel CIS

## Step 2 - Import supplementare

Importa:

- `projects/melodema/melodema_cis_import_supplement_medium.csv`

Lead attesi:

- `Comune di Levico Terme`
- `Comune di Pergine Valsugana`
- `Opera Don Calabria`
- `Abbazia o Unita Pastorale S. Agostino - Il Retrone`
- `Fidas Vicenza`

Controlli subito dopo l'import:

- le 5 organization compaiono nel database
- citta e regione sono corrette, in particolare per i due comuni trentini
- i contatti sono stati creati quando presenti
- le note riportano che si tratta di supplemento da review

## Step 3 - Lavorare la attach queue

Apri:

- `projects/melodema/melodema_attach_existing_queue_medium.csv`

Per ogni riga fai questa sequenza:

1. cerca nel CIS `existing_organization_name`
2. apri la scheda organization
3. aggiungi il contatto suggerito se non esiste gia
4. aggiungi una nota breve che riporti il `raw_name` come venue o contesto originario
5. non creare una nuova organization se la riga e chiaramente da agganciare a quella esistente

Formato nota consigliato:

```text
Venue/contesto storico: <raw_name>. Contatto recuperato da review Melodema: <nome contatto>. Motivo aggancio: <decision_rationale>.
```

## Casi della attach queue

I casi attesi sono questi:

- `Comune di Altavilla Vicentina`
- `Pro Loco di Brogliano`
- `Comune di Dueville`
- `Comune di Noventa Vicentina`

Per `Comune di Altavilla Vicentina` ci sono piu righe:

- non creare organization aggiuntive per `Villa Valmarana Morosini`
- tratta `Villa Valmarana Morosini` come venue o contesto evento

Per `Comune di Dueville`:

- non creare una organization autonoma per `Teatro Comunale Busnelli`
- tienilo come venue nelle note del Comune

Per `Comune di Noventa Vicentina`:

- non creare una organization autonoma per `Duomo`
- tienilo come venue nelle note del Comune

## Regole da rispettare

- i file `attach_existing_queue` non si importano
- se il contatto e gia presente, aggiorna la scheda invece di duplicarlo
- se il luogo e solo venue, non trasformarlo automaticamente in organization
- se il soggetto reale resta ambiguo, rimane in review

## Quando fermarsi

La fase import e chiusa quando:

- il file principale e importato
- il supplemento `medium` e importato
- la attach queue `medium` e lavorata
- i casi ancora dubbi restano fuori dal database operativo oppure in review separata

## Output atteso

Alla fine di questa procedura dovresti avere:

- una base organizations Melodema ampia e pulita
- contatti gia caricati per i casi migliori
- meno ambiguita fra `comune`, `proloco`, `parrocchia`, `venue`
- una review residua piu piccola e piu gestibile
