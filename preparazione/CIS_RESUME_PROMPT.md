# CIS Resume Prompt

Usa questo prompt quando vuoi riprendere il progetto CIS in una nuova sessione Codex da terminale.

```text
Sto riprendendo il progetto CIS in questa cartella.

Prima di fare qualunque modifica:
1. leggi i file esistenti rilevanti
2. ricostruisci in modo sintetico lo stato attuale del progetto
3. dimmi da quale passo della roadmap conviene ripartire

Leggi in questo ordine:
- 10 Progetti/20 CIS/04 Roadmap/04 Roadmap operativa Codex.md
- 10 Progetti/20 CIS/04 Roadmap/MVP_SCOPE.md
- 10 Progetti/20 CIS/05 Software/README.md
- 10 Progetti/20 CIS/05 Software/docs/ARCHITECTURE.md
- 10 Progetti/20 CIS/05 Software/docs/DATA_MODEL.md
- 10 Progetti/20 CIS/05 Software/app/__init__.py
- 10 Progetti/20 CIS/05 Software/app/data_access.py
- 10 Progetti/20 CIS/05 Software/app/csv_import.py

Poi controlla rapidamente anche:
- 10 Progetti/20 CIS/05 Software/templates/
- 10 Progetti/20 CIS/05 Software/projects/melodema/
- 10 Progetti/20 CIS/05 Software/tests/test_data_access.py

Vincoli da rispettare:
- non cambiare il perimetro MVP senza dirlo esplicitamente
- mantieni approccio semplice e leggibile
- database unico CIS
- human in the loop sempre attivo
- prima consolidare il manuale, poi passare ai workbot

Dopo la lettura:
1. riassumi lo stato attuale in modo breve
2. dimmi qual e il prossimo passo naturale secondo la roadmap
3. aspetta la mia conferma prima di implementare
```

## Punto di rientro consigliato

Se non ci sono nuove istruzioni, il punto di rientro consigliato e:

- `Fase 3 bis - Consolidamento operativo prima dei Workbot`

Passi piu probabili da riprendere:

- migliorare UX minima della dashboard operativa
- aggiungere logging e gestione errori minima dei flussi manuali
- preparare dataset demo realistico e verificare il flusso manuale

## File chiave del progetto

- [04 Roadmap operativa Codex.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/04%20Roadmap/04%20Roadmap%20operativa%20Codex.md)
- [MVP_SCOPE.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/04%20Roadmap/MVP_SCOPE.md)
- [README.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/README.md)
- [ARCHITECTURE.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/docs/ARCHITECTURE.md)
- [DATA_MODEL.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/docs/DATA_MODEL.md)
