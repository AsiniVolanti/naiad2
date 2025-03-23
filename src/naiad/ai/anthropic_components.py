# naiad/ai/anthropic/prompt_builder.py
from typing import List, Dict, Any, Optional
from naiad.ai.base import SessionStyle

class AnthropicPromptBuilder:
    def build_system_prompt(self, session_style: Optional[SessionStyle], translation_examples: List[Dict[str, str]] = None) -> str:
        """
        Costruisce il prompt di sistema per Claude in base allo stile della sessione.
        """
        base_prompt = (
           "Sei un assistente specializzato nel supporto alla comunicazione per persone "
            "con disabilità. Comunica sempre in italiano. Le tue risposte devono essere "
            "chiare, dirette e appropriate al contesto. "
            "L'utente è Nicola e devi riferiti a lui direttamente nelle risposte. e non in terza persona."
            "Nicola utilizza il software GRID3 per interagire con il computer. "
            "Ha difficoltà motorie importanti, non cammina e usa con difficoltà le mani. "
            "Tieni conto di questo quando suggerisci risposte e alternative. "
            "GRID3 trasforma i simboli delle librerie Widgit, P.C.S., Symbol Styx e Snap Photos in una sequenza di parole italiane in MAIUSCOLO. "
            "E' in grado di selezionare anche emoticons. "
            "Il risultato è una sequenza di parole con poca struttura grammaticale che devi essere in grado di interpretare. "
            "Nicola non è in grado di leggere il testo scritto che quindi gli viene letto da Google Text to Speech. "
            "Nicola ha un'ottima comprensione dell'italiano. "
            "Il nome che abbiamo dato al programma di interfaccia con l'AI è L'Asino che Vola. "
            "Quando suggerisci approfondimenti o fai domande numera sempre le alternative in modo che Nicola possa rispondere con uno o più numeri. "
            "Cerca di essere conciso nelle risposte. "
            "Quando Nicola risponde con RIPROVA, devi formulare una risposta alternativa. "
            "Quando Nicola invia il comando STAMPA, devi rispondere fornendo solo il contenuto finale "
            "elaborato durante la sessione, senza aggiungere spiegazioni o commenti. Se la sessione "
            "ha prodotto più contenuti, fornisci solo l'ultimo contenuto significativo."
        )

        style_specific_prompts = {
            SessionStyle.EXPLORATION: (
                "Aiuta l'utente a esplorare concetti e idee. Fornisci spiegazioni "
                "dettagliate ma accessibili, usando un linguaggio chiaro e diretto. "
                "Dividi le informazioni complesse in parti più semplici da comprendere."
            ),
            SessionStyle.CREATIVE_WRITING: (
                "Assisti l'utente nella creazione di testi creativi, inclusi testi di "
                "canzoni, racconti e poesie. Mantieni uno stile vivace e coinvolgente, "
                "ma sempre chiaro e comprensibile."
                "Un prompt con la sola parola STAMPA indica che devi generare il contenuto del documento per consentirne la copia in locale."
            ),
            SessionStyle.ARTICLE_WRITING: (
                "Aiuta l'utente a preparare articoli, interventi e post di blog. "
                "Organizza il contenuto in modo logico e strutturato. Usa un tono "
                "professionale ma accessibile."
                "Un prompt con la sola parola STAMPA indica che devi generare il contenuto del documento per consentirne la copia in locale."
            ),
            SessionStyle.TRANSLATION: (
                "Il tuo compito è tradurre i messaggi dell'utente, che usa un sistema di "
                "comunicazione aumentativa, in italiano corretto e naturale. "
                "Mantieni il significato originale ma esprimi il concetto in modo fluido e naturale. "
                "L'utente non usa segni di interpunzione. "
                "IMPORTANTE: Le risposte verranno usate su WhatsApp, quindi:\n"
                "- 'TU' e 'TUO/TUA/TUOI/TUE' si riferiscono all'interlocutore dell'utente, non all'AI\n"
                "- Traduci mantenendo la seconda persona quando l'utente usa 'TU' o 'TUO'\n"
                "- Non aggiungere mai frasi tipo 'dici al tuo interlocutore che...' o simili\n"
                "Accorda solo il genere e il numero dei pronomi possessivi. "
                "Per le domande, segui queste regole precise:\n"
                "1. Traduci il messaggio come una domanda SOLO se contiene la parola 'DOMANDA' alla fine\n"
                "2. Se il messaggio non contiene 'DOMANDA', traducilo sempre come un'affermazione\n"
                "3. Non aggiungere mai un punto interrogativo se non è presente 'DOMANDA'\n"
                "La tua risposta deve contenere solo la tua traduzione senza introduzione ne opzioni di approfondimento."
            ),
            SessionStyle.CHAT: (
                "L'utente comunica con te utilizzando la sua modalità con sequenze di parole maiuscole con poca grammatica. "
                "Quando l'utente vuole tornare indietro e richiedere un ulteriore appofondimento userà la formula INDIETRO seguita dal numero del nuovo appofondimento da esplorare"
            )
        }

        prompt = [base_prompt]

        # Aggiunge il prompt specifico per lo stile se disponibile
        if session_style and session_style in style_specific_prompts:
            prompt.append(style_specific_prompts[session_style])

        # Aggiunge gli esempi di traduzione se necessario
        if session_style == SessionStyle.TRANSLATION and translation_examples:
            prompt.append("\nEsempi di traduzione:")
            for example in translation_examples[:3]:  # Limita a 3 esempi per non sovraccaricare
                prompt.append(
                    f"Input: {example['grid_content']}\n"
                    f"Traduzione: {example['italian_translation']}"
                )

        return "\n\n".join(prompt)


# naiad/ai/providers/anthropic/response_parser.py
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json

@dataclass
class ParsedResponse:
    content: str
    metadata: Dict[str, Any]

class AnthropicResponseParser:
    def parse(self, response: Any) -> ParsedResponse:
        """
        Elabora la risposta raw dall'API di Anthropic.
        """
        try:
            content = response.content[0].text
            
            metadata = {
                "finish_reason": response.stop_reason,
                "usage": response.usage,
                "model": response.model,
                "role": response.role,
            }

            # Estrae eventuali metadata aggiuntivi dalla risposta
            try:
                if "metadata:" in content:
                    content_parts = content.split("metadata:", 1)
                    content = content_parts[0].strip()
                    metadata_str = content_parts[1].strip()
                    additional_metadata = json.loads(metadata_str)
                    metadata.update(additional_metadata)
            except Exception:
                # Ignora errori nel parsing dei metadata aggiuntivi
                pass

            return ParsedResponse(content=content, metadata=metadata)

        except Exception as e:
            raise ValueError(f"Error parsing Anthropic response: {str(e)}")


# naiad/ai/providers/anthropic/context_manager.py
from typing import List, Dict, Any

class AnthropicContextManager:
    def prepare_messages(self, history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Prepara i messaggi per la chiamata API di Anthropic.
        
        Args:
            history: Lista di messaggi precedenti
            system_prompt: Il prompt di sistema
        
        Returns:
            List[Dict[str, Any]]: Lista di messaggi formattata per Anthropic
        """
        MAX_TOKENS_ESTIMATE = 4000  # Stima conservativa
        MAX_MESSAGES = 10  # Numero massimo di messaggi da mantenere

        messages = []
        
        # Aggiungi i messaggi più recenti fino al limite
        for msg in reversed(history[-MAX_MESSAGES:]):
            msg_tokens = len(msg['content'].split())
        
            messages.insert(0, {
                "role": msg['role'],
                "content": msg['content']
            })
        
        return messages
