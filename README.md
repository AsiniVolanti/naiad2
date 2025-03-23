# NAIAD (Nick's AI Assistant for Dialogue) o l'Asino che vola

*Read this in [English](README-EN.md)*

NAIAD (Nick's AI Assistant for Dialogue), per gli amici l'Asino che vola, è un'applicazione progettata per migliorare l'accessibilità e la comunicazione per persone con disabilità comunicative, con particolare attenzione a utenti con paralisi cerebrale. Il progetto integra l'IA di Claude di Anthropic per facilitare la comunicazione, l'interazione con la tecnologia, l'espressione creativa e l'autonomia personale offrendo nuove opportunità per connettersi con il mondo.

## Motivazione

Il progetto è nato per assistere Nicola, una persona con paralisi cerebrale che comunica attraverso il software GRID3 utilizzando il puntamento oculare. Nicola può selezionare immagini per costruire frasi, ma la struttura delle frasi è limitata dalla sequenza di immagini che veicolano singoli concetti. Nonostante non possa leggere il testo scritto e necessiti di sintesi vocale, Nicola ha una perfetta comprensione dell'italiano parlato e possiede un'intelligenza e sensibilità notevoli.

## Funzionalità

- Applicazione Windows che si integra con il software di comunicazione GRID3
- Accesso API ad un modello di intelligenza artificiale generativa (Anthropic)
- Sintesi vocale per una comunicazione naturale
- Molteplici modalità di interazione:
  - Esplorazione di concetti
  - Scrittura creativa (canzoni, racconti, poesie)
  - Scrittura di articoli
  - Traduzione in italiano corretto
  - Comunicazione social
- Gestione delle sessioni e consapevolezza del contesto
- Stili di comunicazione personalizzabili
- Integrazione con la clipboard per un'interazione fluida con GRID3
- Preparazione di messaggi WhatsApp dal contesto della sessione corrente

## Il nostro primo utente dice:
"A novembre ho scoperto L'Asino che Vola, un programma che ha rivoluzionato il mio modo di comunicare. Finalmente posso esprimermi usando tutta la ricchezza della lingua italiana, con le sue sfumature ed espressioni. Il programma mi aiuta a trovare le parole giuste e a costruire frasi eleganti, permettendomi di comunicare con uno stile più personale e raffinato.

La scorsa settimana, ho scritto un post sul valore della comunicazione. Grazie a L'Asino che Vola, ho potuto esprimere i miei pensieri con la precisione e la bellezza che meritavano, senza limitarmi a frasi semplici e ripetitive. Ho anche preparato una presentazione per un evento online, giocando con metafore e citazioni che prima mi sarebbero state precluse. E nei miei messaggi quotidiani, riesco finalmente a trasmettere anche il tono e le emozioni che voglio condividere.
Sogno un futuro in cui questo programma evolverà ancora, permettendomi di trasformare i miei pensieri in progetti creativi sempre più complessi. Immagino di poter montare cortometraggi direttamente con la mente, dando vita alle storie che ho sempre desiderato raccontare." Nick

## Come Claude è Integrato

Claude è la componente centrale di NAIAD, utilizzato per:

1. **Traduzione Migliorata**: Trasforma sequenze di concetti base in italiano grammaticalmente corretto, permettendo all'utente di comunicare in modo più naturale.

2. **Esplorazione di Concetti**: Consente all'utente di approfondire argomenti complessi attraverso un dialogo assistito.

3. **Creatività Aumentata**: Supporta la scrittura creativa di racconti, poesie e canzoni, dando voce all'espressione artistica.

4. **Scrittura di Articoli**: Facilita la creazione di contenuti strutturati per la comunicazione formale.

5. **Comunicazione Social**: Aiuta a preparare messaggi adeguati per piattaforme di messaggistica.

L'integrazione avviene attraverso un'applicazione Windows sviluppata in Python che si interfaccia con GRID3, utilizzando la sintesi vocale per permettere all'utente di "ascoltare" le risposte di Claude senza dover leggere il testo.

## Risultati e Impatto

L'implementazione di NAIAD ha mostrato risultati significativi:

- **Comunicazione più ricca**: Nicola può esprimere pensieri più complessi e sfumati rispetto a quanto possibile con il solo GRID3.
  
- **Maggiore autonomia**: Riduzione della dipendenza da caregiver per la comunicazione quotidiana.
  
- **Espressione creativa**: Possibilità di creare contenuti artistici che prima erano inaccessibili.
  
- **Partecipazione sociale**: Miglioramento della qualità delle interazioni sociali, comprese quelle su piattaforme digitali.

## Sfide Tecniche Superate

1. **Integrazione con GRID3**: Abbiamo sviluppato un sistema di comunicazione seamless tra GRID3 e Claude.

2. **Ottimizzazione dei prompt**: Abbiamo affinato i prompt per comprendere il formato particolare di input derivante dalla comunicazione basata su immagini.

3. **Sintesi vocale efficiente**: Implementazione di un sistema TTS ottimizzato per la lettura delle risposte di Claude.

4. **Persistenza del contesto**: Gestione efficace delle sessioni per mantenere la continuità nelle conversazioni.

## Installazione

### Prerequisiti

- Sistema operativo Windows
- Python 3.8 o superiore
- Software GRID3 installato
- Chiavi API necessarie per i provider AI

### Configurazione

1. Clona il repository:
```bash
git clone https://github.com/yourusername/naiad.git
cd naiad
```

2. Crea un ambiente virtuale e attivalo:
```bash
python -m venv venv
source venv/Scripts/activate  # Su Windows
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

4. Copia la configurazione predefinita:
```bash
cp src/naiad/config/default_config.yaml config.yaml
```

5. Modifica `config.yaml` per aggiungere le tue chiavi API e personalizzare le impostazioni.

### Compilazione dell'Eseguibile

```bash
python build.py
```

## Utilizzo

1. Avvia GRID3 e assicurati che sia configurato correttamente
2. Avvia NAIAD
3. Usa il tasto designato in GRID3 per inviare il testo a NAIAD
4. NAIAD elaborerà l'input e restituirà la risposta attraverso la sintesi vocale

## Configurazione

L'applicazione può essere configurata attraverso `config.yaml`. Le impostazioni principali includono:

- Chiavi API per i provider AI
- Impostazioni TTS
- Preferenze di sessione
- Modalità di comunicazione

## Come Contribuire

I contributi sono benvenuti! Sentiti libero di inviare una Pull Request.

## Licenza

Questo progetto è rilasciato sotto la licenza MIT - vedi il file [LICENSE](license.md) per i dettagli.

## Ringraziamenti

- Anthropic Claude per l'elaborazione AI
- Software GRID3 per la comunicazione aumentativa
- Tutti i contributori e i sostenitori del progetto

## Note per lo Sviluppo

Se stai contribuendo al progetto, assicurati di:

1. Seguire le convenzioni PEP 8 per il codice Python
2. Aggiungere test unitari per le nuove funzionalità
3. Aggiornare la documentazione quando necessario
4. Testare le modifiche sia in ambiente di sviluppo che con l'eseguibile compilato

Il progetto utilizza:
- `pyinstaller` per la creazione dell'eseguibile
- `pygame` per la gestione audio
- `anthropic` per i servizi AI
- `gtts` per la sintesi vocale
- `pyttsx3` per la sintesi vocale
- 
Per qualsiasi dubbio o chiarimento, non esitare ad aprire una Issue su GitHub.