# Estensioni realizzate a Gennaio 2025

## Sospensione e riattivazione sessioni

Consente di salvare e riattivare una sessione per ogni stile definito.
Funziona anche rivavviando il PC.

### chat-suspend.cmd
Questo comando salva la sessione associata allo stile corrente in modo da poterla riprendere successivamente. 

Su GRID3 sarà attivata da un pulsante che deve solo invocare il nuovo comando.

### chat-resume.cmd
Questo comando ricarica la sessione associata allo stile corrente.
Per cui si seleziona lo stile di sessione si seleziona il nuovo pulsante di ripresa sessione interrotta.

## Salvataggio contenuti generati dall'Asino
Durante una chat è possibile chiedere all'Asino di generare il risultato della sessione, nella forma di un documento, una storia, un articolo, una canzone,...
Il documento verrà salvato in una cartella apposita. E' possibile successivamente riascolatare gli artefatti così salvati.

### artifact-print.cmd
Il comando attivato da un pulsante GRID3, invia all'AI un prompt "STAMPA". Questo fa si che la risposta contenga il documento costruito nel corso della sessione.
Prima di selezionare il pulsante "STAMPA", Nick può inserire una serie di simboli con GRID3 che verranno utilizzati come nome del file di testo che verrà salvato.

### artifact-list.cmd
Questo comando, attivato da pulsante GRID3, genera una lista dei documenti salvati nella cartella dedicata, e genera un vocale con il numero dell'artefatto e la sequenza di simboli con cui è stato salvato.

### artifact-read.cmd
Scrivendo con grid3 un numero e selezionado questo pulsante il documento corrispondente viene letto.

### Gestione multi-modello
Ogni stile di sessione ha la possibilità di definire l'utilizzo di un modello specifico.

## Da fare:

### Gestione config
Sembra che config legga solo api ma non gli altri campi.
Nel codice appare troppe volte la definizione di default e va semplificato.

### Log rotanti
Introdurre log giornalieri con rotazione 1 mese

### Artifact senza titolo
Non si può usare il nome attribuito automaticamente in assenza di codice. Eventualmente mi limito alle prime 5 parole.



