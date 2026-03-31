Sto riprendendo il progetto CIS esattamente da questo punto. Prima di proporre modifiche, usa anche `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md` come memoria operativa del progetto e mantieni i vincoli attivi:

- non cambiare il perimetro MVP senza dirlo esplicitamente
- mantieni approccio semplice e leggibile
- database unico CIS
- human in the loop sempre attivo
- se aggiungi decisioni o idee rilevanti, salvale anche in `docs/DEVELOPMENT_NOTES.md`

Stato da considerare gia verificato:

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
- il prossimo step della roadmap e lo Step 6: prova operativa reale sul progetto `ethics`

Stato operativo raggiunto nella sessione precedente:

- abbiamo avviato davvero lo Step 6 su `ethics`
- era emerso un bug su Windows nel salvataggio dei run `WB0` causato da filename troppo lunghi
- il bug e stato corretto troncando lo slug del filename dei run `WB0`
- la decisione e stata annotata in `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md`
- il run `WB0` di `ethics` e stato salvato correttamente
- le candidate `WB0` sono state ripulite direttamente nei file run JSON del progetto `ethics`
- sono state reviewate e importate nel CIS queste 5 organization del progetto `ethics`:
  - `Vecomp`
  - `Pettenon Cosmetics S.p.A. S.B.`
  - `San Marco Group`
  - `Piovan Group`
  - `FEINAR Srl`

Punto esatto di interruzione:

- ho lavorato `Vecomp` dentro la scheda organization
- `WB1` su `Vecomp` e stato usato almeno in parte, ma il flusso non mi e ancora del tutto chiaro
- `FEINAR Srl` non e ancora stata lavorata
- dobbiamo riprendere da qui, chiarendo molto bene il flusso pratico `WB1` e completando lo Step 6 senza allargare il perimetro MVP

Quello che ti chiedo nella nuova sessione:

1. ricostruisci rapidamente lo stato reale dai file essenziali e conferma il punto di ripartenza
2. spiegami in modo molto pratico il flusso `WB1` dentro la scheda organization:
   - cosa va nel prompt preview
   - cosa devo cercare fuori dal CIS
   - cosa salvo nel form `WB1`
   - differenza tra dati organization, referente, note WB1 e qualificazione lead
3. ripartiamo da `Vecomp`:
   - verifica con me cosa e gia stato compilato
   - dimmi se manca qualcosa per considerare `Vecomp` completata
4. poi guidami su `FEINAR Srl` passo passo
5. infine aiutami a chiudere lo Step 6 con una mini-verifica finale:
   - cosa ha funzionato
   - cosa ha creato attrito
   - quali correzioni minime conviene fare nello Step 7

Importante:

- non partire subito con modifiche al codice
- prima chiarisci il flusso operativo e fammi riprendere il lavoro da `Vecomp` e `FEINAR Srl`
- se proponi modifiche, devono restare minime e coerenti con MVP, database unico e human in the loop
