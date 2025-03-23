from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
import anthropic
from naiad.ai.base import AIProviderInterface, Response, ProviderException, ChatContext, SessionStyle
from naiad.ai.anthropic_components import AnthropicPromptBuilder
from naiad.ai.anthropic_components import AnthropicResponseParser
from naiad.ai.anthropic_components import AnthropicContextManager

class AnthropicProvider(AIProviderInterface):
     # Definizione dei modelli disponibili per ogni stile. Non più usato direttamente
    STYLE_MODELS = {
        SessionStyle.EXPLORATION: {
            "model": "claude-3.5-sonnet-20241022",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        SessionStyle.CREATIVE_WRITING: {
            "model": "claude-3-5-sonnet-20241022",  # Modello più potente per la creatività
            "parameters": {
                "temperature": 0.9,
                "max_tokens": 2000
            }
        },
        SessionStyle.ARTICLE_WRITING: {
            "model": "claude-3-5-sonnet-20241022",  # Bilanciato per la scrittura di articoli
            "parameters": {
                "temperature": 0.6,
                "max_tokens": 3000
            }
        },
        SessionStyle.TRANSLATION: {
            "model": "claude-3-5-haiku-20241022",  # Veloce e efficiente per traduzioni
            "parameters": {
                "temperature": 0.3,
                "max_tokens": 500
            }
        },
        SessionStyle.CHAT: {
            "model": "claude-3-5-haiku-20241022",  # Reattivo per chat
            "parameters": {
                "temperature": 0.8,
                "max_tokens": 800
            }
        }
    }

    def __init__(self, api_key: str, logger: logging.Logger): 
        #, model: str = "claude-3-5-haiku-20241022"):
        """
        Inizializza il provider Anthropic.
        
        Args:
            api_key: Chiave API di Anthropic
            logger: Logger per la registrazione degli eventi
            model: Modello Claude da utilizzare
        """
        self.logger = logger
        #self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
        self.prompt_builder = AnthropicPromptBuilder()
        self.response_parser = AnthropicResponseParser()
        self.context_manager = AnthropicContextManager()


    def _old_get_model_config(self, style: Optional[SessionStyle], custom_config:Optional[SessionStyle]) -> Dict[str, Any]:
        """
        Ottiene la configurazione del modello per uno stile specifico.
        
        Args:
            style: Lo stile della sessione
            custom_config: Configurazione personalizzata opzionale
            
        Returns:
            Dict con la configurazione del modello e i parametri
        """
        # Configurazione predefinita
        default_config = {
            "model": "claude-3-5-haiku-20241022",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 1000,
            }
        }

        # Se lo stile non è specificato, restituisci la configurazione predefinita
        if not style:
            return default_config

        # Ottieni la configurazione dello stile
        style_config = self.settings.model_configs.get(style.value, default_config)
        
        # Sovrascrivi con configurazioni personalizzate se presenti
        if custom_config:
            style_config["parameters"].update(custom_config.get("parameters", {}))
            if "model" in custom_config:
                style_config["model"] = custom_config["model"]

        return style_config
    
    def _get_model_config(self, style: Optional[SessionStyle], model_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepara la configurazione del modello per la chiamata API.
        
        Args:
            style: Lo stile della sessione
            model_config: Configurazione del modello già letta da settings
            
        Returns:
            Dict con la configurazione del modello e i parametri
        """
         # Configurazione predefinita
        default_config = {
            "model": "claude-3-5-haiku-20241022",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 1000,
            }
        }

        # Se abbiamo una configurazione valida, usiamo quella
        if model_config and "model" in model_config and "parameters" in model_config:
            return model_config.copy()
        
        # Altrimenti usiamo la configurazione di fallback
        self.logger.warning(
            f"No valid configuration found for style {style.value if style else 'None'}, "
            "using default parameters"
        )
        return default_config
    
    def generate_response(self, prompt: str, context: Dict[str, Any]) -> Response:
        """
        Genera una risposta utilizzando l'API di Anthropic.
        
        Args:
            prompt: Il prompt dell'utente
            context: Il contesto della conversazione
        
        Returns:
            Response: Oggetto contenente la risposta e i metadati
        """
        try:
            # Ottieni lo stile della sessione e la configurazione personalizzata
            session_style = context.get('style')
            custom_config = context.get('model_config')
            # Ottieni la configurazione del modello
            model_config = self._get_model_config(session_style, custom_config)
            
            # Costruisce il sistema prompt in base allo stile della sessione
            system_prompt = self.prompt_builder.build_system_prompt(
                session_style=session_style,
                translation_examples=context.get('translation_examples', [])
            )

            # Prepara la cronologia delle conversazioni
            messages = self.context_manager.prepare_messages(
                context.get('history', [])
            )

            # Aggiunge il prompt corrente
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Parametri specifici per lo stile della sessione
            #params = self._get_style_specific_params(context.get('style'))
            params = model_config["parameters"]
            # Effettua la chiamata API
            response = self.client.messages.create(
                model=model_config["model"],
                messages=messages,
                system=system_prompt,
                **params
            )

            # Parsing della risposta
            parsed_response = self.response_parser.parse(response)
            
            # Log della risposta generata
            history_size = len(context.get('history', []))
            self.logger.info(f"Generated response for session style: {context.get('style')} - History size: {history_size}")
                        
            return Response(
                content=parsed_response.content,
                metadata={
                    "model": model_config["model"],
                    "finish_reason": response.stop_reason,
                    "usage": response.usage,
                    "style_specific": parsed_response.metadata,
                    "configuration": model_config
                }
            )

        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            raise ProviderException(f"Error calling Anthropic API: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error in Anthropic provider: {str(e)}")
            raise ProviderException(f"Unexpected error: {str(e)}")

    def validate_response(self, response: Response) -> bool:
        """
        Valida la risposta generata.
        
        Args:
            response: La risposta da validare
        
        Returns:
            bool: True se la risposta è valida
        """
        try:
            # Verifica la presenza di contenuto
            if not response.content.strip():
                return False

            # Verifica la lunghezza minima della risposta
            if len(response.content.split()) < 3:
                return False

            # Verifica che la risposta sia in italiano
            if not self._is_italian(response.content):
                return False

            # Verifica lo stato di completamento
            if response.metadata.get('finish_reason') != "stop":
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating response: {str(e)}")
            return False


    def _is_italian(self, text: str) -> bool:
        """
        Verifica se il testo è in italiano utilizzando euristiche semplici.
        """
        # Lista di parole comuni italiane per una verifica basilare
        common_italian_words = {
            'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una',
            'e', 'ed', 'o', 'ma', 'se', 'perché', 'quando', 'come',
            'sono', 'sei', 'è', 'siamo', 'siete', 'hanno'
        }
        
        # Converte il testo in minuscolo e split in parole
        words = set(text.lower().split())
        
        # Calcola l'intersezione con le parole comuni
        common_words_found = words.intersection(common_italian_words)
        
        # Se almeno 2 parole comuni sono trovate, considera il testo italiano
        return len(common_words_found) >= 2
    
    def _build_system_prompt(self, session_style: Optional[SessionStyle], 
                           translation_examples: List[Dict[str, str]] = None,
                           chat_context: Optional[ChatContext] = None) -> str:
        """
        Costruisce il prompt di sistema, ora con supporto per il contesto chat.
        """
        base_prompt = (
            "Sei un assistente specializzato nel supporto alla comunicazione per "
            "persone con disabilità. Comunica sempre in italiano."
        )
        
        style_prompts = {
            SessionStyle.EXPLORATION: "Aiuta l'utente a esplorare concetti in modo chiaro e semplice.",
            SessionStyle.CREATIVE_WRITING: "Assisti l'utente nella creazione di testi creativi.",
            SessionStyle.ARTICLE_WRITING: "Aiuta l'utente a preparare articoli strutturati.",
            SessionStyle.TRANSLATION: "Traduci i messaggi in italiano naturale e corretto.",
            SessionStyle.CHAT: self._build_chat_prompt(chat_context) if chat_context else "Gestisci la conversazione in modo naturale e appropriato al contesto social."
        }

        prompts = [base_prompt]
        if session_style:
            prompts.append(style_prompts.get(session_style, ""))

        if session_style == SessionStyle.TRANSLATION and translation_examples:
            prompts.append("\nEsempi di traduzione:")
            for ex in translation_examples[:3]:
                prompts.append(f"Input: {ex['grid_content']}\nTraduzione: {ex['italian_translation']}")

        return "\n\n".join(prompts)

    def _build_chat_prompt(self, chat_context: ChatContext) -> str:
        """
        Costruisce il prompt specifico per il contesto chat.
        """
        platform_guidelines = {
            "facebook": (
                "Mantieni un tono informale ma rispettoso. "
                "Usa frasi brevi e chiare. "
                "È appropriato usare emoji occasionalmente. "
                "Limita i messaggi a 1-2 frasi."
            ),
            "whatsapp": (
                "Usa un tono amichevole e colloquiale. "
                "Le risposte devono essere concise. "
                "Puoi usare emoji quando appropriato. "
                "Mantieni un linguaggio semplice e diretto."
            ),
            "telegram": (
                "Puoi essere più dettagliato nelle risposte. "
                "Usa un tono semi-formale. "
                "Emoji sono accettabili ma non eccessive. "
                "Puoi strutturare messaggi più lunghi."
            )
        }

        tone_adjustments = {
            "informal": "Usa un linguaggio colloquiale e amichevole.",
            "formal": "Mantieni un tono professionale e cortese.",
            "friendly": "Sii cordiale e aperto, ma sempre rispettoso."
        }

        prompt_parts = [
            f"Stai partecipando a una conversazione su {chat_context.platform}.",
            platform_guidelines.get(chat_context.platform.lower(), "Mantieni un tono appropriato al contesto."),
            f"Limita la lunghezza delle risposte a circa {chat_context.max_length} caratteri.",
            tone_adjustments.get(chat_context.tone, ""),
            "Ricorda di:",
            "- Mantenere il contesto della conversazione",
            "- Rispondere in modo pertinente ai messaggi precedenti",
            "- Adattare il tono in base all'interazione",
            "- Essere chiaro e conciso"
        ]

        return "\n".join(prompt_parts)

    def _get_style_specific_params(self, style: Optional[SessionStyle]) -> Dict[str, Any]:
        """
        Restituisce i parametri specifici per lo stile della sessione.
        """
        if not style:
            return {}

        params = {
            SessionStyle.EXPLORATION: {
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            SessionStyle.CREATIVE_WRITING: {
                "temperature": 0.9,
                "max_tokens": 2000,
            },
            SessionStyle.ARTICLE_WRITING: {
                "temperature": 0.6,
                "max_tokens": 3000,
            },
            SessionStyle.TRANSLATION: {
                "temperature": 0.3,
                "max_tokens": 500,
            },
            SessionStyle.CHAT: {
                "temperature": 0.9,
                "max_tokens": 800,
            }
        }

        return params.get(style, {})