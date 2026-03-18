# CIS Resume Prompt WB0

Usa questo prompt quando vuoi riprendere il progetto CIS in una nuova sessione Codex da terminale, a partire dallo stato attuale di `WB0`.

```text
Sto riprendendo il progetto CIS da questo punto.

Prima di fare qualunque modifica:
1. leggi i file esistenti rilevanti
2. usa anche docs/DEVELOPMENT_NOTES.md come memoria operativa del progetto
3. ricostruisci in modo sintetico lo stato attuale
4. dimmi da quale passo conviene ripartire

Leggi in questo ordine:
- 10 Progetti/20 CIS/04 Roadmap/04 Roadmap operativa Codex.md
- 10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md
- 10 Progetti/20 CIS/04 Roadmap/MVP_SCOPE.md
- 10 Progetti/20 CIS/05 Software/docs/ARCHITECTURE.md
- 10 Progetti/20 CIS/05 Software/docs/DATA_MODEL.md
- 10 Progetti/20 CIS/05 Software/app/__init__.py
- 10 Progetti/20 CIS/05 Software/app/wb0_target_discovery.py
- 10 Progetti/20 CIS/05 Software/app/data_access.py
- 10 Progetti/20 CIS/05 Software/templates/wb0_target_discovery.html
- 10 Progetti/20 CIS/05 Software/tests/test_wb0_target_discovery.py

Vincoli da rispettare:
- non cambiare il perimetro MVP senza dirlo esplicitamente
- mantieni approccio semplice e leggibile
- database unico CIS
- human in the loop sempre attivo
- usa docs/DEVELOPMENT_NOTES.md come memoria operativa del progetto
- se aggiungi decisioni o idee rilevanti, salvale anche li

Contesto attuale da ricordare:
- WB0 e stato sviluppato fino al ruolo di filtro operativo prima del database CIS
- il run di WB0 e stato rifattorizzato per uso manuale via chatbot
- in docs/DEVELOPMENT_NOTES.md ci sono note future su WB0
- il prossimo passo naturale della roadmap e WB1, salvo mia diversa indicazione

Dopo la lettura:
1. riassumi lo stato attuale in modo breve
2. dimmi il prossimo passo naturale
3. aspetta la mia conferma prima di implementare
```

## Punto di rientro consigliato

Se non ci sono nuove istruzioni, il punto di rientro consigliato e:

- `Fase 4 - Workbot essenziali`

Passi piu probabili da riprendere:

- implementare `WB1 Contact Hunter`
- consolidare o rifinire `WB0` solo se emergono nuove esigenze operative
- usare `docs/DEVELOPMENT_NOTES.md` per memorizzare idee e decisioni future

## File chiave del progetto

- [04 Roadmap operativa Codex.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/04%20Roadmap/04%20Roadmap%20operativa%20Codex.md)
- [DEVELOPMENT_NOTES.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/docs/DEVELOPMENT_NOTES.md)
- [MVP_SCOPE.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/04%20Roadmap/MVP_SCOPE.md)
- [ARCHITECTURE.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/docs/ARCHITECTURE.md)
- [DATA_MODEL.md](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/docs/DATA_MODEL.md)
- [__init__.py](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/app/__init__.py)
- [wb0_target_discovery.py](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/app/wb0_target_discovery.py)
- [wb0_target_discovery.html](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/templates/wb0_target_discovery.html)
- [test_wb0_target_discovery.py](/mnt/c/000_progetti/preparazione/10%20Progetti/20%20CIS/05%20Software/tests/test_wb0_target_discovery.py)
