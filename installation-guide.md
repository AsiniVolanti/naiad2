# Guida all'Installazione Manuale di NAIAD

Questa guida spiega come installare manualmente NAIAD configurando l'ambiente Python, compilando l'eseguibile e impostando la struttura delle directory necessarie.
Sul PC dell'utente finale occorrerà eseguire solo i passaggi dal 3 in poi.

## Prerequisiti

- Windows 10 o superiore
- Python 3.8 o superiore
- Connessione internet per scaricare le dipendenze
- Chiave API Anthropic (Claude) per le funzionalità di AI

## 1. Configurazione dell'Ambiente Python

### Installazione di Python

1. Scarica Python 3.8 o superiore dal sito ufficiale: https://www.python.org/downloads/windows/
2. Durante l'installazione, assicurati di selezionare:
   - "Add Python to PATH"
   - "Install pip"
   - "Install for all users" (consigliato)

### Creazione di un Ambiente Virtuale (opzionale ma consigliato)

```bash
# Crea una directory per il progetto
mkdir C:\NAIAD2-Project
cd C:\NAIAD-Project

# Clona il repository o estrai i file sorgente in questa directory
# git clone <url-repository> .

# Crea un ambiente virtuale
python -m venv venv

# Attiva l'ambiente virtuale
venv\Scripts\activate
```

### Installazione delle Dipendenze

Con l'ambiente virtuale attivato, installa tutte le dipendenze dal file requirements.txt:

```bash
# Installa le dipendenze principali
pip install -r requirements.txt

# Installa PyInstaller per la compilazione dell'eseguibile
pip install pyinstaller
```

## 2. Compilazione dell'Eseguibile NAIAD.exe

Nella directory del progetto, esegui:

```bash
# Esegui lo script di build
python build.py
```

Lo script `build.py` utilizzerà PyInstaller per creare l'eseguibile NAIAD.exe nella cartella `dist\NAIAD\`.

## 3. Preparazione delle Directory di Sistema

### Creazione della Struttura di Directory

Esegui i seguenti comandi con privilegi amministrativi:

```bash
# Crea la directory principale in ProgramData
mkdir "C:\ProgramData\NAIAD"

# Crea le sottodirectory necessarie
mkdir "C:\ProgramData\NAIAD\comm"
mkdir "C:\ProgramData\NAIAD\db"
mkdir "C:\ProgramData\NAIAD\artifacts"
mkdir "C:\ProgramData\NAIAD\logs"
mkdir "C:\ProgramData\NAIAD\assets"
mkdir "C:\ProgramData\NAIAD\assets"

# Imposta i permessi appropriati
icacls "C:\ProgramData\NAIAD" /grant Users:(OI)(CI)F /T
```

### Installazione dell'Eseguibile in Program Files

```bash
# Crea la directory in Program Files
mkdir "C:\Program Files\NAIAD"

# Copia l'eseguibile e i file necessari
xcopy /E /I "dist\NAIAD\*" "C:\Program Files\NAIAD\"

# Copia gli assets nella directory ProgramData
xcopy /E /I "assets\*" "C:\ProgramData\NAIAD\assets\"
```

## 4. Configurazione dell'Applicazione

### Creazione del File di Configurazione

Crea un file `config.yaml` nella directory `C:\ProgramData\NAIAD\config` con il seguente contenuto:

```yaml
api:
  anthropic:
    api_key: "chiave-api-qui"
    models:
      exploration:
        model: "claude-3-5-sonnet-20241022"
        parameters:
          temperature: 0.7
          max_tokens: 1000
          
      creative_writing:
        model: "claude-3-5-sonnet-20241022"
        parameters:
          temperature: 0.9
          max_tokens: 2000
          
      article_writing:
        model: "claude-3-5-sonnet-20241022"
        parameters:
          temperature: 0.6
          max_tokens: 3000
          
      translation:
        model: "claude-3-5-haiku-20241022"
        parameters:
          temperature: 0.3
          max_tokens: 500
          
      chat:
        model: "claude-3-5-haiku-20241022"
        parameters:
          temperature: 0.8
          max_tokens: 800
  openai:
    api_key: ''
  perplexity:
    api_key: ''
logging:
  file: naiad.log
  level: INFO
tts:
  language: it
  provider: local
  rate: 140
```

**Importante:** Sostituisci `"chiave-api-qui"` con la tua chiave API personale di Anthropic.

## 5. Verifica dell'Installazione

Per verificare che NAIAD sia installato correttamente:

1. Avvia NAIAD.exe
2. Si dovrebbe aprire una finestra che mostra la lista degli artefatti e delle sessioni salvate

## Risoluzione dei Problemi

### NAIAD non si avvia

- Verifica che il percorso di installazione sia corretto
- Verifica che i requisiti di sistema siano soddisfatti
- Controlla i log in `C:\ProgramData\NAIAD\logs\`

### NAIAD non riceve testo da GRID3

- Verifica che il comando in GRID3 sia configurato correttamente
- Assicurati che il testo sia copiato nella clipboard prima di chiamare NAIAD
- Controlla che nella directory `C:\ProgramData\NAIAD\comm\` vengano creati i file trigger

### La sintesi vocale non funziona

- Verifica che il volume del sistema sia attivo
- Controlla che non ci siano altre applicazioni che utilizzano l'audio
- Riavvia NAIAD per reinizializzare il sistema TTS
- Prova a modificare il provider TTS nel file config.yaml

### Errori di connessione AI

- Verifica che la chiave API sia stata inserita correttamente nel file config.yaml
- Controlla la connessione internet
- Assicurati che il provider AI (Anthropic) sia attivo e funzionante

## Disinstallazione Manuale

Per rimuovere manualmente NAIAD:

1. Chiudi NAIAD se è in esecuzione
2. Elimina la directory `C:\Program Files\NAIAD\`
3. Elimina la directory `C:\ProgramData\NAIAD\` (se desideri rimuovere anche i dati salvati)
