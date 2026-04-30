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

## Avvio dell'app locale

Dalla cartella del progetto:

```bash
cd "10 Progetti/20 CIS/05 Software"
.venv/bin/python run.py
```

Poi apri nel browser:

```text
http://127.0.0.1:5000
```

## Avvio rapido su Windows

Se usi il `venv` Windows gia presente nella cartella, puoi avviare il `CIS` senza riscrivere i comandi ogni volta.

Metodo consigliato da Esplora file o da PowerShell:

```text
AVVIA_CIS.bat
```

Oppure:

```text
start_cis.bat
```

Se invece vuoi lanciare direttamente lo script PowerShell:

```powershell
.\start_cis.ps1
```

attenzione:

- `start_cis.bat` e `AVVIA_CIS.bat` usano gia `powershell -ExecutionPolicy Bypass`
- quindi in genere non richiedono `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- `start_cis.ps1` eseguito direttamente in una sessione PowerShell puo invece essere bloccato dalla policy corrente
- in quel caso serve prima:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

poi:

```powershell
.\start_cis.ps1
```

Questi launcher:

- usano `.venv\Scripts\python.exe`
- inizializzano `data\cis.sqlite3` se manca
- aprono il browser su `http://127.0.0.1:5000`
- avviano il server Flask locale
