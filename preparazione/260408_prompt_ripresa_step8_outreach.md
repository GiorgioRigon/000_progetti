# Prompt ripresa CIS dopo chiusura roadmap 2 settimane

Sto riprendendo il progetto CIS esattamente da questo punto.

Prima di proporre modifiche o piani, usa anche `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md` come memoria operativa del progetto e mantieni sempre attivi questi vincoli:

- non cambiare il perimetro MVP senza dirlo esplicitamente
- mantieni approccio semplice e leggibile
- database unico CIS
- human in the loop sempre attivo
- se aggiungi decisioni o idee rilevanti, salvale anche in `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md`

Usa quando serve anche:

- `10 Progetti/20 CIS/05 Software/docs/OPERATIONAL_MANUAL.md`
- `10 Progetti/20 CIS/05 Software/docs/NEXT_STEP_OUTREACH_MINIMUM.md`
- `10 Progetti/20 CIS/05 Software/docs/OUT_OF_SCOPE_IDEAS.md`
- `10 Progetti/20 CIS/04 Roadmap/04 Roadmap operativa Codex.md`

## Stato da considerare gia verificato

- esiste il selettore del progetto attivo in UI
- i progetti attivi di riferimento sono almeno `melodema` ed `ethics`
- `WB0` e `WB1` leggono profili operativi per progetto
- `WB0` e `WB1` sono stati usati davvero sul progetto `ethics`
- esiste una qualificazione lead minima comune salvata nelle note `organization`
- `organizations` ha `project_key` e le viste sono filtrate per progetto attivo
- esiste una `Organizations Table` separata, semplice e leggibile
- il bug Windows sui filename lunghi dei run `WB0` e stato corretto
- la roadmap di 2 settimane sui profili `WB0` e `WB1` e da considerare chiusa

## Stato operativo da assumere

- `Vecomp`, `FEINAR Srl`, `Pettenon Cosmetics S.p.A. S.B.`, `San Marco Group` e `Piovan Group` sono state lavorate come prova reale sul progetto `ethics`
- `Pettenon`, `San Marco` e `Piovan` sono state rifinite anche con controllo qualita operativo
- lo Step 7 va considerato chiuso come consolidamento finale della roadmap di 2 settimane

## Decisione di progetto gia presa

Il prossimo passo sensato non e altra discovery e non e un'estensione del perimetro workbot.

Il gap MVP piu concreto da chiudere adesso e:

- bozza outreach modificabile
- salvataggio dello storico minimo della bozza

Questa decisione riallinea il lavoro alla roadmap principale, soprattutto ai passi:

- `27. Implementare WB4 Outreach Drafter`
- `28. Salvare bozze e storico comunicazioni`

## Cosa ti chiedo nella nuova sessione

1. ricostruisci rapidamente lo stato reale dai file essenziali
2. conferma il perimetro minimo del prossimo step senza allargare l'MVP
3. proponi solo l'implementazione minima utile per:
   - generare una bozza outreach modificabile dalla scheda `organization`
   - usare i template del progetto attivo
   - salvare la bozza nel database
   - mostrare uno storico minimo nella scheda `organization`
4. distingui chiaramente tra:
   - minimo necessario adesso
   - miglioramenti utili ma rinviabili
   - idee fuori perimetro MVP
5. se introduci decisioni rilevanti, salvale in `10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md`

## Promemoria operativo

- non confondere `WB1` con qualificazione lead
- evita redesign o ristrutturazioni ampie
- preferisci chiudere il flusso base MVP prima di aggiungere intelligenza o automazioni
- usa le tabelle gia esistenti (`messages`, `outreach_actions`) prima di proporre nuovi campi o nuovo schema
