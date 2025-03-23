# NAIAD

NAIAD (Nick's AI Assistant for Dialogue) è un progetto innovativo che sfrutta l'intelligenza artificiale per migliorare l'accessibilità e la comunicazione per le persone con disabilità comunicative. Progettato per adattarsi alle esigenze individuali, NAIAID facilita il dialogo, l'interazione con la tecnologia e l'autonomia personale, offrendo nuove opportunità per connettersi con il mondo.

## Motivazione
Ho un amico, Nicola, affetto da paralisi cerbrale. Non riesce a parlare e riesce a comunicare solo  attraverso un laptop con installato GRID3 che gli consente di selezionare immagini con il puntamento oculare per costruire delle frasi in italiano. Tuttavia la struttura della frase lascia a desiderare essendo costruita da una sequenza di immagini che veicolano singoli concetti. La sua disabilità gli impedisce il riconoscimento del linguaggio scritto che pertanto deve essergli passato attraverso sintesi vocale. D'altra parte ha una perfetta comprensione dell'italiano parlato. Per finire Nicola ha importanti disabilità motorie che gli impediscono di camminare, e gli consentono movimenti con la mano destra controllati con grande sforzo. Nicola è super-curioso, intelligente ed ha una sensibilità molto superiore alla media, Questo gli consente di arrivare al nocciolo dei problemi e di trovare strade per arrivare al cuore della gente. Vorrei che riuscisse ad allargare la propria capacità comunicativa con il mondo attraverso il supporto delle nuove tecnologie di AI generativa.  
Navigare in Internet, informarsi in modo approfondito sui suoi tanti interessi,  scrivere i testi di canzoni, comporre articoli e interventi pubblici su gli argomenti più diversi, comunicare con i suoi amici attraverso canali social. Questo è un esempio che vorrei potesse fare in modo soddisfacente ed autonomo attraverso questo strumento software, da installare sul suo computer di ausilio alla comunicazione.

## Requisiti

### Requisiti funzionali
[RQ1] NAIAD è una applicazione Windows che deve avviarsi alla connessione di un utente, su un laptop su cui gira il programma di comunicazione aumentata GRID3. 

[RQ2] Questa applicazione deve contattare diversi fornitori di AI Generativa (anthropic, openAI, perplexity) per supportare Nicola (d'ora in poi l'utente) nell'interagire con i compiti che questi strumenti mettono a disposizione e per consentirgli di tenere comunicazioni in italiano corretto con tutti. 

[RQ3] Da GRID3, alla pressione di un tasto specifico, la stringa generata dall'utente viene copiata nella clipboard di Windows e viene lanciato un comando per indicare a NAIAD, la presenza di un prompt per le AIGenerative. La risposta verrà raccolta da NAIAD via web e copiata nella clipboard prima di segnalare a GRID3 (ad esempio con la pressione virtuale del tasto F2) il completamento della transazione. Questo apre la possibilità di utilizzare il sintetizzatore vocale di GRID3 per leggere la risposta all'utente e consentirgli di proseguire nella sessione di chat. 

[RQ3.1] Una alternativa interessante, potrebbe essere quella di copiare nella clipboard la risposta della AI ma anche di avviare ad uno speaker configurabile, l'audio generato da un sintetizzatore vocale di qualità, interno al PC o accessibile via web, direttamente dall'applicazione. Questo aprirebbe la possibilità di selezionare la migliore sintesi vocale, con intonazioni e toni di voce gradevoli, molto necessari per chi ha accesso solo al parlato come canale di input.

[RQ4] L'utente deve essere in grado di selezionare i compiti che vuole siano affidati all'AI generativa nel corso di una sessione. Tra queste ci saranno: 
- esplorazione di concetti
- scrittura creativa di testi di canzoni, racconti o poesie
- preparazione interventi, articoli, blog post su argomenti di interesse dell'utente
- trasposizione dei prompt scritti in GRID3 in italiano corrente per facilitare la comprensione del pensiero dell'utente anche a chi non è abituato a rapportarsi con lui.
[RQ4.1] L'utente deve poter gestire le sessioni di lavoro , richiedendo correzioni a prompt precedenti, di poter riascoltare una risposta o memorizzarla in modo permanente con un titolo.
[RQ5] Uno dei compiti fondamentali, sarà quello di trasporre il pensiero dell'utente espresso nel prompt GRID3 in un pensiero in italiano corretto.
[RQ5.1] Il sistema disporra di una serie di esempi di comunicazione GRID3->Italiano per favorire la comprensione al primo colpo da parte della AI generativa.
[RQ5.2] Nuovi esempi di comunicazione di successo potranno essere memorizzati nel set di contesto su richiesta dell'utente o meglio ancora in base alla presenza di emoticon specifici o alla pressione di un tasto sulla griglia di GRID3.
[RQ6] Dovranno essere predisposti diversi possibili stili di sessione, che consentiranno a NAIAD di configurare il contesto e la scelta della AI da contattare.
[RQ7] I comandi per la configurazione della sessione potranno essere predisposti sempre in un prompt GRID3 e inoltrati a NAIAD attraverso la pressione di un tasto diverso sulla griglia.

### Requisiti implementazione
[RQ8] L'applicazione avrà bisogno di accedere alla clipboard di Windows e ai suoi speaker, inoltre dovrà essere in grado di inviare la pressione virtuale di tasti per interagire con GRID3.

[RQ9] L'applicazione dovrà disporre di una parte "server" attiva in background (come servizio Windows o come Task schedulato all'avvio)

[RQ10] L'applicazione dovrà disporre di una parte persistente (locale o remota) per memorizzare i contesti, gli esempi di comunicazione con successo, le chat salvate.

[RQ11] Dovendo arrivare a supportare l'utente non solo nella scrittura ma anche nella comunicazione verbale occorre che le prestazioni siano ottimizzate in modo da minimizzare l'aggiunta di latenza rispetto alle diverse interazioni via web con le AI di supporto.

[RQ12] Lo stack tecnologico deve offrire prestazioni elevate, facilità di setup e installazione, velocità di sviluppo.

[RQ13] Svilupperemo l'applicazione usando Python
