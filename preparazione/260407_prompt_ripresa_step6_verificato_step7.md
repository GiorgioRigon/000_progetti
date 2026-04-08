# Prompt ripresa CIS da Step 6 verificato verso Step 7

Sto riprendendo il progetto CIS esattamente da questo punto.

Prima di proporre modifiche o piani, usa anche `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md` come memoria operativa del progetto e mantieni sempre attivi questi vincoli:

- non cambiare il perimetro MVP senza dirlo esplicitamente
- mantieni approccio semplice e leggibile
- database unico CIS
- human in the loop sempre attivo
- se aggiungi decisioni o idee rilevanti, salvale anche in `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md`

## Stato da considerare gia verificato

- esiste il selettore del progetto attivo in UI
- i progetti attivi di riferimento sono almeno `melodema` ed `ethics`
- `consulenza_certificazione` e stato rinominato in `ethics`
- `WB0` e `WB1` leggono profili operativi per progetto
- `WB1` e stato rifinito con prompt/input piu guidati
- `WB0` e stato rifinito con prompt preview e review piu guidati
- esiste una qualificazione lead minima comune, salvata nelle note `organization`
- `organizations` ha `project_key` e la lista `Organizations` e filtrata per progetto attivo
- le organization storiche vanno considerate appartenenti a `melodema`
- esiste una `Organizations Table` separata, semplice e leggibile
- la home e piu stretta, le pagine operative sono piu larghe, la tabella e la piu larga
- il bug Windows sui filename lunghi dei run `WB0` e stato corretto troncando lo slug del filename
- la decisione sul bug Windows e stata annotata in `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md`

## Stato operativo Step 6 da considerare raggiunto

- lo Step 6 sul progetto `ethics` e stato usato davvero su lead reali
- il run `WB0` di `ethics` e stato salvato correttamente
- le candidate `WB0` del progetto `ethics` sono state ripulite nei file run JSON
- sono state reviewate e importate nel CIS queste 5 organization:
  - `Vecomp`
  - `Pettenon Cosmetics S.p.A. S.B.`
  - `San Marco Group`
  - `Piovan Group`
  - `FEINAR Srl`
- `Vecomp` e stata lavorata nella scheda organization
- il flusso pratico `WB1` e stato chiarito in modo operativo
- `Vecomp` e stata completata manualmente in modo accettabile per Step 6:
  - dati organization presenti
  - contatti esplorativi presenti
  - blocco `WB1` presente
  - qualificazione lead presente
- `FEINAR Srl` e stata lavorata in modo minimo ma accettabile per Step 6:
  - sito, email generale e telefono presenti
  - social ufficiali presenti
  - 2 contatti nominativi presenti
  - qualificazione lead presente
  - manca o e debole la parte `WB1 note`, ma per Step 6 il caso e stato considerato comunque sufficiente come prova operativa reale

## Stato pratico da assumere adesso

- Step 6 e da considerare sostanzialmente verificato sul progetto `ethics`
- il focus probabile della prossima sessione e Step 7, ma prima va sempre ricostruito rapidamente lo stato reale dai file essenziali
- non partire subito con modifiche al codice
- prima chiarisci se conviene fare solo consolidamento operativo, piccole correzioni UX/testuali o minime modifiche di Step 7 coerenti con MVP

## Cosa ti chiedo nella nuova sessione

1. ricostruisci rapidamente lo stato reale dai file essenziali e conferma se Step 6 puo dirsi chiuso
2. dimmi qual e il perimetro minimo e sensato di Step 7 senza allargare l'MVP
3. distingui chiaramente tra:
   - correzioni minime necessarie emerse dall'uso reale
   - miglioramenti utili ma rinviabili
   - idee fuori perimetro MVP
4. se proponi modifiche:
   - devono restare minime
   - devono essere coerenti con database unico, human in the loop e approccio semplice
   - vanno annotate in `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md` se introducono decisioni rilevanti
5. se non serve modificare codice subito, guidami invece sul prossimo uso operativo del CIS nel modo piu concreto possibile

## Promemoria operativo

- usa come memoria anche `10 Progetti/20 CIS/05 Software/docs/OPERATIONAL_MANUAL.md` quando utile
- non confondere `WB1` con qualificazione lead: il primo serve ad arricchire il lead, la seconda a decidere il passo commerciale
- evita redesign o ristrutturazioni ampie
- preferisci chiarire il flusso reale prima di toccare il software
