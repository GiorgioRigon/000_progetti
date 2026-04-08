# CIS Next Step - Outreach Minimum

Decisione operativa salvata dopo la chiusura della roadmap di 2 settimane sui profili `WB0` e `WB1`.

## Stato di partenza

- la roadmap di 2 settimane su `WB0` e `WB1` e da considerare chiusa
- il progetto `ethics` e stato usato davvero su lead reali
- il flusso minimo oggi verificato e:
  - progetto attivo
  - `WB0`
  - review
  - import
  - `WB1`
  - qualificazione lead
  - prossimo passo

## Decisione

Il prossimo passo sensato del progetto `CIS` non e altra discovery e non e un'estensione del perimetro workbot.

Il gap MVP piu concreto da chiudere adesso e:

- bozza outreach modificabile
- salvataggio dello storico minimo della bozza

Questa decisione riallinea il lavoro alla roadmap principale senza allargare l'MVP.

## Riferimento alla roadmap principale

I passi piu coerenti da riprendere sono:

- `27. Implementare WB4 Outreach Drafter`
- `28. Salvare bozze e storico comunicazioni`

Riferimento:

- `10 Progetti/20 CIS/04 Roadmap/04 Roadmap operativa Codex.md`

## Perimetro minimo del prossimo step

### Da fare

- generare dalla scheda `organization` una bozza outreach semplice e modificabile
- usare i dati gia presenti del lead e i template del progetto attivo
- salvare la bozza nel database usando le tabelle gia previste
- mostrare nella scheda `organization` uno storico minimo delle bozze o azioni collegate

### Da non fare

- invio automatico email o messaggi
- orchestrazione commerciale avanzata
- scoring o strategia piu complessi prima della bozza outreach
- nuove automazioni esterne
- redesign ampio della dashboard

## Ordine consigliato

1. definire il perimetro minimo di `WB4 Outreach Drafter`
2. implementare generazione bozza modificabile
3. aggiungere salvataggio in `messages` e `outreach_actions`
4. mostrare storico minimo nella scheda `organization`
5. verificare un flusso reale end-to-end su un lead `ethics`

## Razionale

- completa un pezzo centrale dell'MVP gia previsto
- sfrutta tabelle gia esistenti invece di aggiungere nuovo schema
- resta coerente con database unico `CIS`, approccio semplice e human in the loop
- evita di investire ora in workbot piu evoluti senza aver chiuso il flusso base di contatto
