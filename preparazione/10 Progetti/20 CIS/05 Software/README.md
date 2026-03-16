# CIS Software

Scheletro iniziale del progetto software del Commercial Intelligence System (CIS).

Questa cartella contiene la struttura base del progetto e la preparazione minima dell'ambiente Python.

## Struttura

```text
app/
templates/
static/
data/
projects/
tests/
docs/
```

## Scopo delle cartelle

- `app/`: codice applicativo Flask
- `templates/`: template HTML
- `static/`: file statici
- `data/`: database locale e file dati
- `projects/`: configurazioni dei progetti commerciali
- `tests/`: test automatici
- `docs/`: documentazione tecnica e operativa

## Ambiente Python minimale

Dipendenze iniziali:

- `Flask`
- `sqlite3` incluso nella libreria standard di Python, quindi non richiede installazione separata

### Avvio locale su Linux o macOS

```bash
cd "10 Progetti/20 CIS/05 Software"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Avvio locale su Windows PowerShell

```powershell
cd "10 Progetti/20 CIS/05 Software"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Verifica minima

Per controllare che Flask sia installato:

```bash
python -c "import flask, sqlite3; print(flask.__version__)"
```
