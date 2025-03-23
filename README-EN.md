# NAIAD (Nick's AI Assistant for Dialogue) or The Flying Donkey

*Leggi questo in [Italiano](README.md)*

NAIAD (Nick's AI Assistant for Dialogue), known to friends as "The Flying Donkey," is an application designed to improve accessibility and communication for people with communication disabilities, with particular attention to users with cerebral palsy. The project integrates Anthropic's Claude AI to facilitate communication, interaction with technology, creative expression, and personal autonomy, offering new opportunities to connect with the world.

## Motivation

The project was born to assist Nicola, a person with cerebral palsy who communicates through GRID3 software using eye tracking. Nicola can select images to build sentences, but the sentence structure is limited by the sequence of images that convey single concepts. Although he cannot read written text and needs speech synthesis, Nicola has a perfect understanding of spoken Italian and possesses remarkable intelligence and sensitivity.

## Features

- Windows application that integrates with GRID3 communication software
- API access to a generative artificial intelligence model (Anthropic)
- Text-to-speech synthesis for natural communication
- Multiple interaction modes:
  - Concept exploration
  - Creative writing (songs, stories, poems)
  - Article writing
  - Translation into correct Italian
  - Social communication
- Session management and context awareness
- Customizable communication styles
- Clipboard integration for smooth interaction with GRID3
- Preparation of WhatsApp messages from the current session context

## Our First User Says:
"In November, I discovered The Flying Donkey, a program that has revolutionized my way of communicating. Finally, I can express myself using all the richness of the Italian language, with its nuances and expressions. The program helps me find the right words and build elegant sentences, allowing me to communicate with a more personal and refined style.

Last week, I wrote a post about the value of communication. Thanks to The Flying Donkey, I was able to express my thoughts with the precision and beauty they deserved, without limiting myself to simple and repetitive phrases. I also prepared a presentation for an online event, playing with metaphors and quotations that would have been precluded to me before. And in my daily messages, I can finally convey the tone and emotions I want to share.
I dream of a future where this program will evolve further, allowing me to transform my thoughts into increasingly complex creative projects. I imagine being able to edit short films directly with my mind, bringing to life the stories I've always wanted to tell." Nick

## How Claude is Integrated

Claude is the central component of NAIAD, used for:

1. **Enhanced Translation**: Transforms sequences of basic concepts into grammatically correct Italian, allowing the user to communicate more naturally.

2. **Concept Exploration**: Allows the user to delve into complex topics through assisted dialogue.

3. **Augmented Creativity**: Supports creative writing of stories, poems, and songs, giving voice to artistic expression.

4. **Article Writing**: Facilitates the creation of structured content for formal communication.

5. **Social Communication**: Helps prepare appropriate messages for messaging platforms.

Integration occurs through a Windows application developed in Python that interfaces with GRID3, using speech synthesis to allow the user to "listen" to Claude's responses without having to read the text.

## Results and Impact

The implementation of NAIAD has shown significant results:

- **Richer communication**: Nicola can express more complex and nuanced thoughts compared to what is possible with GRID3 alone.
  
- **Greater autonomy**: Reduced dependence on caregivers for daily communication.
  
- **Creative expression**: Possibility to create artistic content that was previously inaccessible.
  
- **Social participation**: Improvement in the quality of social interactions, including those on digital platforms.

## Technical Challenges Overcome

1. **Integration with GRID3**: We developed a seamless communication system between GRID3 and Claude.

2. **Prompt optimization**: We refined prompts to understand the particular input format derived from image-based communication.

3. **Efficient speech synthesis**: Implementation of an optimized TTS system for reading Claude's responses.

4. **Context persistence**: Effective session management to maintain continuity in conversations.

## Installation

### Prerequisites

- Windows operating system
- Python 3.8 or higher
- GRID3 software installed
- API keys needed for AI providers

### Configuration

1. Clone the repository:
```bash
git clone https://github.com/yourusername/naiad.git
cd naiad
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the default configuration:
```bash
cp src/naiad/config/default_config.yaml config.yaml
```

5. Edit `config.yaml` to add your API keys and customize settings.

### Executable Compilation

```bash
python build.py
```

## Usage

1. Start GRID3 and make sure it is properly configured
2. Start NAIAD
3. Use the designated key in GRID3 to send text to NAIAD
4. NAIAD will process the input and return the response through speech synthesis

## Configuration

The application can be configured through `config.yaml`. The main settings include:

- API keys for AI providers
- TTS settings
- Session preferences
- Communication modes

## How to Contribute

Contributions are welcome! Feel free to send a Pull Request.

## License

This project is released under the MIT license - see the [LICENSE](license.md) file for details.

## Acknowledgements

- Anthropic Claude for AI processing
- GRID3 software for augmentative communication
- All contributors and supporters of the project

## Development Notes

If you are contributing to the project, make sure to:

1. Follow PEP 8 conventions for Python code
2. Add unit tests for new features
3. Update documentation when necessary
4. Test changes in both development environment and compiled executable

The project uses:
- `pyinstaller` for creating the executable
- `pygame` for audio management
- `anthropic` for AI services
- `gtts` for speech synthesis
- `pyttsx3` for speech synthesis

For any doubts or clarifications, do not hesitate to open an Issue on GitHub.