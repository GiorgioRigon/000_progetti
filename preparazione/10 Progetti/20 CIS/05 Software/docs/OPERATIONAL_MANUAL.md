# CIS Operational Manual

Manuale operativo pratico da usare dopo il completamento della roadmap di due settimane sui profili `WB0` e `WB1`.

## Scopo

Questo manuale serve per usare il `CIS` in modo semplice, ripetibile e controllato su progetti diversi, ad esempio:

- `melodema`
- `ethics`
- altri progetti futuri

Il principio resta sempre lo stesso:

- il database `CIS` e unico
- i workbot sono generici
- la specializzazione sta nei profili di progetto o campagna
- il controllo umano resta sempre attivo

## Regole operative da non saltare

- non usare il `CIS` per eseguire azioni esterne automatiche
- non importare nel database dati troppo incerti o non verificabili
- usare `WB0` per filtrare prima di scrivere nel `CIS`
- usare `WB1` per arricchire lead gia presenti nel `CIS`
- salvare sempre note brevi e leggibili quando un dato e dubbio o solo parzialmente confermato

## Flusso operativo standard

1. scegliere il progetto attivo
2. controllare o aggiornare il profilo operativo del progetto
3. preparare il lavoro con `WB0`
4. fare review manuale dei target
5. importare nel `CIS` solo i target promettenti
6. arricchire i lead importati con `WB1`
7. salvare i dati utili alla qualificazione
8. decidere il passo commerciale successivo

## 1. Scegliere il progetto attivo

Prima di iniziare, chiarire sempre:

- quale progetto stai lavorando
- quale campagna stai lavorando
- quale obiettivo vuoi ottenere oggi

Esempi:

- `melodema`: trovare enti che programmano concerti
- `ethics`: trovare aziende o organizzazioni con segnali di interesse verso `PdR125` o temi affini

## 2. Controllare il profilo operativo

Apri il file del progetto:

- `projects/<progetto>/workbot_profiles.json`

Verifica almeno questi punti.

Per `WB0`:

- focus operativo
- target prioritari
- segnali di buon fit
- segnali di esclusione
- campi minimi da raccogliere

Per `WB1`:

- obiettivo del contatto
- ruoli prioritari
- fonti da controllare
- dati minimi richiesti
- checklist di verifica

Se il profilo non e adatto alla campagna attuale:

- correggilo prima di partire
- mantieni le modifiche semplici e leggibili
- evita di inserire logiche troppo astratte o troppo generiche

## 3. Usare WB0 per trovare target

Apri `WB0` e compila il run.

Campi da compilare con attenzione:

- obiettivo ricerca
- contesto progetto
- territorio target
- tipi di target
- fonti da interrogare
- prompt base
- criteri di inclusione
- criteri di esclusione

Poi usa il `prompt preview` come brief operativo per:

- ricerca manuale diretta
- lavoro assistito con chatbot

Durante la ricerca:

- raccogli solo target plausibili
- evita duplicati
- preferisci dati verificabili
- aggiungi una nota breve sul motivo del fit

## 4. Fare review dei target WB0

Prima di importare nel database:

- rileggi ogni candidate
- conferma se il sito e affidabile
- assegna un primo giudizio di fit
- scrivi una nota di qualificazione sintetica
- decidi se scartare, tenere in osservazione o importare

Usa il database solo per target che hanno almeno queste condizioni:

- identita chiara
- minimo contesto verificabile
- fit ragionevole con il progetto

## 5. Importare nel CIS

Importa nel database solo i target selezionati.

Dopo l’import:

- controlla subito la scheda organization
- verifica che nome, territorio, sito e note siano sensati
- correggi eventuali errori manualmente

Se il target non e abbastanza chiaro:

- non forzare l’import
- lascialo nel run `WB0` finche non hai abbastanza evidenze

## 6. Usare WB1 per trovare referenti

Apri la scheda della organization e usa `WB1`.

Il `prompt preview WB1` serve come brief per:

- trovare il referente migliore
- raccogliere email e telefono
- verificare sito e social ufficiali
- annotare i segnali utili alla qualificazione

Ordine consigliato:

1. verificare il sito ufficiale
2. cercare pagina contatti, team o management
3. cercare ruoli coerenti con il profilo
4. trovare il miglior canale verificabile
5. salvare solo dati con una nota minima di verifica

Se non trovi un referente nominativo:

- salva almeno email generale e telefono affidabile
- annota nelle note che il referente non e stato identificato

## 7. Salvare i dati di qualificazione

Per il progetto `ethics`, oltre ai dati di contatto, salva anche gli elementi utili a capire se il lead e buono.

Esempi:

- interesse esplicito verso `PdR125`
- interesse indiretto verso parita di genere, `ESG`, `CSR`, diversity, compliance
- presenza di ruoli `HR`, `ESG`, governance o direzione coerenti
- eventuali altre certificazioni o policy rilevanti
- nota sintetica sul perche il lead sembra promettente oppure debole

Regola pratica:

- prima salva in modo semplice e leggibile
- aggiungi struttura solo quando serve davvero

## 8. Decidere il passo successivo

Dopo `WB1`, ogni lead deve finire in uno di questi stati pratici:

- pronto per contatto
- da qualificare meglio
- da tenere monitorato
- da scartare

Non lasciare lead in stato ambiguo senza una nota breve che spieghi il perche.

## Routine consigliata di lavoro

### Routine breve giornaliera

- aprire il progetto attivo
- controllare il profilo operativo
- fare un run `WB0` o avanzare un run esistente
- importare solo i target migliori
- fare `WB1` su 3-10 organization gia promettenti
- chiudere la sessione lasciando note pulite

### Routine settimanale

- rileggere i profili del progetto
- correggere i prompt che hanno funzionato male
- aggiornare criteri inclusione o esclusione
- controllare duplicati o note confuse
- annotare in `docs/DEVELOPMENT_NOTES.md` decisioni rilevanti

## Buone pratiche

- scrivere poco ma in modo utile
- preferire note verificabili a impressioni vaghe
- non complicare il profilo operativo se bastano poche regole chiare
- usare `WB0` come filtro e non come import diretto cieco
- usare `WB1` come arricchimento mirato e non come raccolta casuale

## Errori da evitare

- usare prompt molto belli ma troppo generici
- importare lead solo perche sembrano interessanti a prima vista
- mischiare dati certi, ipotesi e idee future senza distinguerli
- accumulare note lunghe ma poco utili
- modificare il profilo di progetto senza poi verificare l’impatto sul lavoro reale

## Checklist finale per ogni lead

- organization verificata
- sito verificato o assenza del sito annotata
- fit iniziale espresso in modo chiaro
- referente o miglior contatto disponibile salvato
- email e telefono salvati se trovati
- note di verifica presenti
- eventuali segnali di qualificazione salvati
- decisione operativa successiva chiara

## Quando aggiornare i profili

Aggiorna `workbot_profiles.json` quando:

- cambi dominio o tipo di target
- i prompt preview iniziano a produrre risultati deboli
- emergono ruoli piu utili da cercare
- cambiano i segnali di buon fit
- il progetto entra in una fase commerciale diversa

Non aggiornarlo per micro-variazioni irrilevanti. Mantieni il profilo stabile finche ti aiuta davvero a lavorare meglio.

## Promemoria finale

Il `CIS` non deve sostituire il giudizio operativo. Deve renderlo piu ordinato, piu coerente e piu riusabile tra progetti diversi.
