# Project Transfer Pack For Codex WSL

Questo documento ti aiuta a trasferire un progetto nato nel browser dentro una cartella locale gestibile bene con Codex da terminale.

## Obiettivo

Portare in locale il minimo contesto necessario per permettere a Codex di:

- capire rapidamente il progetto
- non perdere decisioni gia prese
- evitare di ricominciare da zero
- riprendere sviluppo, refactor o debugging in modo ordinato

## Cartella consigliata

Dentro la cartella del nuovo progetto crea almeno questi file:

```text
README.md
PROJECT_CONTEXT.md
NEXT_STEPS.md
```

Se hai gia codice:

```text
app/
src/
docs/
tests/
```

## File 1 - README.md

Serve a descrivere in 10 righe cosa e il progetto.

Template:

```md
# Nome progetto

## Obiettivo
Descrizione breve del problema che il progetto risolve.

## Stato attuale
Cosa esiste gia e cosa funziona davvero.

## Stack
Tecnologie principali.

## Avvio locale
Comandi minimi per avviare il progetto.
```

## File 2 - PROJECT_CONTEXT.md

Serve a trasferire la memoria del progetto dal browser al filesystem.

Template:

```md
# Project Context

## Visione
Cosa sto costruendo e per chi.

## Decisioni gia prese
- decisione 1
- decisione 2
- decisione 3

## Vincoli
- vincolo 1
- vincolo 2

## Cosa funziona gia
- funzione 1
- funzione 2

## Problemi aperti
- problema 1
- problema 2

## Cose da non fare
- punto 1
- punto 2
```

## File 3 - NEXT_STEPS.md

Serve a dire a Codex dove riprendere.

Template:

```md
# Next Steps

## Priorita attuale
Descrivi il passo che vuoi fare adesso.

## Ordine consigliato
1. passo 1
2. passo 2
3. passo 3

## Criterio di completamento
Come capisco che questo blocco e finito.
```

## Se hai una chat GPT nel browser

Copia nel filesystem almeno questi elementi:

- obiettivo del progetto
- architettura discussa
- decisioni gia prese
- problemi ancora aperti
- prossimi passi
- eventuali prompt o snippet importanti

Non serve copiare tutta la chat. Serve estrarre il contenuto utile.

## Strategia pratica di trasferimento

1. Crea la cartella del progetto in WSL o nel filesystem che vuoi usare.
2. Inserisci dentro `README.md`, `PROJECT_CONTEXT.md` e `NEXT_STEPS.md`.
3. Se esiste gia codice, copialo nella stessa cartella.
4. Se esistono export, note o prompt utili, salvali in `docs/` o `notes/`.
5. Apri una nuova sessione Codex in quella cartella.
6. Chiedi a Codex di leggere prima i file rilevanti e ricostruire il contesto.

## Prompt consigliato per iniziare un nuovo progetto trasferito

```text
Sto trasferendo in locale un progetto sviluppato in precedenza nel browser.

Prima di fare modifiche:
1. leggi i file esistenti rilevanti
2. ricostruisci in breve obiettivo, stato attuale, vincoli e prossimi passi
3. dimmi se manca contesto importante

Leggi almeno:
- README.md
- PROJECT_CONTEXT.md
- NEXT_STEPS.md

Se trovi codice o documentazione tecnica, leggi solo i file strettamente rilevanti.

Dopo la lettura:
1. riassumi lo stato del progetto
2. proponi il prossimo passo naturale
3. aspetta la mia conferma prima di implementare
```

## Regole che riducono la confusione tra progetti

- usa una cartella separata per ogni progetto
- usa una sessione Codex separata per ogni progetto
- salva sempre una roadmap o un file `NEXT_STEPS.md`
- non affidarti alla memoria della chat: affidati ai file del progetto

## Checklist rapida prima di iniziare con Codex

- ho una cartella dedicata al progetto
- ho salvato il contesto in file `.md`
- ho salvato il codice se gia esiste
- so qual e il prossimo passo concreto
- posso dire a Codex quali file leggere per primi
