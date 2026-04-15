# Ethics Vicenza PdR125 Selection

Data: 2026-04-13

## Scopo

Tracciare in modo leggibile il lavoro di selezione svolto sul bacino `Vicenza` a partire dall'elenco ufficiale Accredia `UNI/PdR 125:2022`, per supportare:

- confronto interno con `ETH`
- pianificazione dei mesi 2-3-4
- distinzione tra universo analizzato, shortlist importata e batch operativo prioritario

## Fonti e passaggi

File sorgente usati:

- `accredia_veneto_pdr125_2022.csv`
- `accredia_veneto_pdr125_2022_shortlist_wb0_ethics_giu_dic_2026.csv`
- `accredia_veneto_pdr125_2022_shortlist_wb0_ethics_giu_dic_2026_vicenza_clean.csv`
- `accredia_veneto_pdr125_2022_vicenza_classificazione_ethics.csv`

Filtri applicati prima della classificazione:

- solo `Veneto`
- solo scadenza stimata tra `2026-06-01` e `2026-12-31`
- solo provincia `VI`
- esclusione di anomalie evidenti citta/provincia
- esclusione duplicati testuali e duplicati gia presenti in `ethics`

Nota metodologica:

- la `scadenza stimata` e stata ricavata come `data certificazione + 3 anni`
- la classificazione seguente e una preselezione euristica per uso operativo, non sostituisce `WB1`

## 3 organization gia presenti in ethics via WB0

Queste organization erano già state importate e lavorate a monte del presente batch:

| Organization | Citta | Stato operativo |
| --- | --- | --- |
| MU.BRE. COSTRUZIONI S.r.l. | Marostica | gia importata in `ethics` via `WB0` |
| CITY GREEN LIGHT S.p.A. | Vicenza | gia importata in `ethics` via `WB0` |
| EDILFLOOR S.p.A. | Sandrigo | gia importata in `ethics` via `WB0` |

## Universo Vicenza classificato: 34 organization

### Banda A

Lead piu adatti a un test operativo iniziale, per vicinanza temporale o plausibilità del gancio `E-docs`.

| Organization                             | Citta             | Scadenza stimata | Motivazione sintetica                                                                                                  |
| ---------------------------------------- | ----------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| BASTONE SALVATORE SRL                    | VICENZA           | 2026-06-16       | plausibile edilizia/cantiere dal nome; lead vicino temporalmente; utile per test settore operativo locale              |
| Serenissima Ristorazione S.p.A.          | VICENZA           | 2026-06-21       | settore diverso da costruzioni; organizzazione operativa strutturata e multi-sede, buon test fuori dal cluster tecnico |
| WINTIME S.P.A. - AGENZIA PER IL LAVORO   | VICENZA           | 2026-07-07       | HR/lavoro; settore diverso e potenzialmente sensibile ai processi PdR125, utile per diversificazione del test          |
| GEMMO S.P.A.                             | Arcugnano         | 2026-07-10       | profilo tecnico-impiantistico/infrastrutturale plausibile; buon fit con gestione operativa e documentale               |
| GDS LIGHTING S.r.l.                      | Cornedo Vicentino | 2026-10-09       | impianti/illuminazione plausibili dal nome; fit tecnico e lead in finestra utile                                       |
| GEOSINTEX S.r.l.                         | Sandrigo          | 2026-10-23       | profilo tecnico/materiali/geotecnica plausibile; buon fit con contesto costruzioni/infrastrutture                      |
| TONELLO ENERGIE S.R.L                    | Breganze          | 2026-11-27       | energia/impianti plausibili dal nome; buon mix settore tecnico e finestra temporale utile                              |
| VERALLIA ITALIA S.P.A.                   | Lonigo            | 2026-12-10       | manifattura strutturata; utile per test su azienda industriale con processi e documentazione diffusi                   |
| ACQUE DEL CHIAMPO S.p.A. Societa Benefit | Arzignano         | 2026-12-11       | utility/servizi ambientali plausibili; ottimo fit operativo e territoriale                                             |
| GRUPPO ADIGE BITUMI S.p.A.               | Sarcedo           | 2026-12-11       | materiali/infrastrutture stradali plausibili; forte coerenza con target tecnico-operativo                              |
| GUALA CLOSURES S.P.A                     | Breganze          | 2026-12-12       | manifattura strutturata; buon test industriale fuori dai settori classici                                              |
| ODOS SERVIZI S.r.l.                      | Vicenza           | 2026-12-22       | servizi operativi dal nome; buon candidato per test su azienda service locale                                          |
| Clerprem S.p.A.                          | CARRE'            | 2026-12-27       | manifattura; interessante per verificare il gancio su azienda industriale locale                                       |

### Banda B

Lead interessanti ma meno immediati, da seconda ondata o da verifica rapida prima dell'import.

| Organization                                          | Citta              | Scadenza stimata | Motivazione sintetica                                                                           |
| ----------------------------------------------------- | ------------------ | ---------------- | ----------------------------------------------------------------------------------------------- |
| INSIEME SOCIETA' COOPERATIVA SOCIALE A R.L.           | VICENZA            | 2026-07-21       | cooperativa sociale; settore diverso interessante ma da verificare meglio il bisogno operativo  |
| ALI S.p.A.                                            | Thiene             | 2026-07-26       | agenzia lavoro/servizi HR; possibile fit ma meno immediato del cluster operativo tecnico        |
| Forint S.p.a.                                         | Vicenza            | 2026-10-13       | societa strutturata ma settore non chiaro dal nome; interessante come test neutro               |
| Maggioli S.p.A.                                       | Thiene             | 2026-11-30       | azienda grande e strutturata; test interessante ma meno immediato del cluster tecnico locale    |
| EVIMED S.r.l.                                         | Vicenza            | 2026-12-01       | probabile ambito healthcare/servizi; buon elemento di diversificazione ma bisogno da verificare |
| B.T.V. S.P.A.                                         | Vicenza            | 2026-12-04       | societa operativa ma settore non chiaro dal nome; candidato neutro per seconda ondata           |
| ACQUE DEL CHIAMPO S.p.A. Societa Benefit - Depuratore | Lonigo             | 2026-12-11       | variante impiantistica della stessa azienda; utile ma secondaria rispetto alla capogruppo       |
| S.M.I. Technologies And Consulting S.r.l.             | Bassano Del Grappa | 2026-12-12       | profilo misto tech/consulting; interessante ma meno chiaro il bisogno operativo                 |
| CP International S.p.A.                               | CARRE'             | 2026-12-27       | societa industriale/commerciale plausibile ma meno leggibile dal nome                           |
| Studio Progetto Soc. Cooperativa Sociale              | CORNEDO VICENTINO  | 2026-12-27       | cooperativa sociale; test utile fuori dal cluster tecnico ma fit da verificare                  |
| ITALIAN EXHIBITION GROUP S.P.A                        | VICENZA            | 2026-12-28       | servizi/eventi strutturati; buon test di diversificazione ma meno prioritario dei fit tecnici   |

### Banda C

Lead lasciati fuori dalla prima ondata test.

| Organization | Citta | Scadenza stimata | Motivazione sintetica |
| --- | --- | --- | --- |
| NEXUMSTP S.P.A. SOCIETA' TRA PROFESSIONISTI | BRENDOLA | 2026-07-05 | profilo professionale/consulenziale; gancio E-docs meno immediato per questo test |
| Deloitte Consulting S.r.l. S.B. | Vicenza | 2026-07-20 | brand consulenziale grande e complesso; probabile ciclo commerciale piu lungo e fit operativo piu debole |
| OTB S.P.A | BREGANZE | 2026-10-03 | gruppo grande e branding forte; possibile valore ma non ideale per batch test rapido |
| BARZANO' & ZANARDO ROMA S.P.A. | VICENZA | 2026-11-22 | studio/servizi professionali; gancio piu debole e struttura meno adatta al test operativo |
| BARZANO' & ZANARDO S.P.A. | VICENZA | 2026-11-22 | studio/servizi professionali; gancio piu debole e struttura meno adatta al test operativo |
| LA SCALA SOCIETA' TRA AVVOCATI PER AZIONI | Vicenza | 2026-11-22 | studio legale; non prioritario per test E-docs operativo |
| Igeam Consulting S.r.l. | Vicenza | 2026-12-01 | consulenza; rischio basso fit come utilizzatore E-docs in questo test |
| EXPRIVIA S.p.A. | Vicenza | 2026-12-04 | gruppo tech/servizi complesso; non ideale per test rapido |
| BANCA CREDIFARMA S.P.A. | VICENZA | 2026-12-05 | banca; gancio operativo PdR125 meno immediato per questo batch |
| BVR Banca Veneto Centrale Credito Cooperativo Italiano - Societa Cooperativa | LONGARE | 2026-12-18 | istituto bancario; gancio meno diretto per questa fase |

## Shortlist operativa corrente

Batch di lavoro consigliato dopo il confronto operativo:

| Priorita | Organization | Nota operativa |
| --- | --- | --- |
| 1 | EDILFLOOR S.p.A. | caso gia importato; lead principale del cluster Sandrigo |
| 1b | GEOSINTEX S.r.l. | da trattare insieme a `EDILFLOOR`, non come caso totalmente separato |
| 2 | MU.BRE. COSTRUZIONI S.r.l. | caso costruzioni puro, molto coerente con il gancio |
| 3 | CITY GREEN LIGHT S.p.A. | caso impianti/verde/servizi urbani, gia importato |
| 4 | Clerprem S.p.A. | incluso anche per conoscenza diretta del contesto aziendale |
| 5 | ITALIAN EXHIBITION GROUP S.P.A | incluso anche per conoscenza diretta del contesto aziendale |
| 6 | ACQUE DEL CHIAMPO S.p.A. Societa Benefit | utility/servizi ambientali, caso strutturato e interessante |

## Decisioni emerse durante la selezione

- `ODOS SERVIZI S.r.l.` esclusa dalla shortlist operativa corrente per il tema sede centrale a Novara
- `GEOSINTEX S.r.l.` da lavorare insieme a `EDILFLOOR S.p.A.`
- la shortlist dei mesi 2-3-4 non deve essere mono-settore: serve testare il gancio `E-docs` su cluster diversi
- le 3 organization gia importate via `WB0` restano parte integrante del bacino selezionato

## Prossimo passo

Per ciascuna organization della shortlist operativa:

1. completare o rifinire `WB1`
2. confermare settore reale, sito, struttura del gruppo e canale di contatto
3. aggiornare `Qualificazione lead`
4. usare `WB4` solo dopo una verifica minima del contatto
