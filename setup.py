import os
from pathlib import Path
import shutil
import subprocess

# Directory base del progetto
base_dir = Path(__file__).resolve().parent

# Directory richieste per il progetto
required_dirs = [
    'src/naiad/core',
    'src/naiad/ai',
    'src/naiad/utils',
    'src/naiad/config',
    'src/naiad/ui',  # Directory per i componenti UI
    'src/naiad/ui/templates',  # Template HTML
    'tests',
    'docs',
    'assets',
    'examples',
    'logs'
]

# Crea le directory necessarie
for dir_path in required_dirs:
    Path(base_dir / dir_path).mkdir(parents=True, exist_ok=True)

# Lista dei file requirements
requirements = {
    'requirements.txt': '''# Core dependencies
pywin32==306
keyboard==0.13.5
pyyaml==6.0.1
python-dotenv==1.0.0
anthropic==0.8.1
httpx==0.25.2
aiohttp==3.9.1
asyncio==3.4.3
structlog==24.1.0
colorama==0.4.6
pyinstaller==6.3.0

# UI dependencies
pywebview==4.4.1
jinja2==3.1.3
tailwindcss==3.4.1
'''
}

def setup_tailwind():
    """Configura Tailwind CSS"""
    tailwind_config = '''module.exports = {
        content: ["./src/naiad/ui/templates/**/*.html"],
        theme: {
            extend: {},
        },
        plugins: [],
    }'''
    
    # Crea il file di configurazione Tailwind
    with open(base_dir / 'tailwind.config.js', 'w', encoding='utf-8') as f:
        f.write(tailwind_config)
    
    # Crea il file CSS di input
    css_input_dir = base_dir / 'src/naiad/ui/static/css'
    with open(css_input_dir / 'input.css', 'w', encoding='utf-8') as f:
        f.write('@tailwind base;\n@tailwind components;\n@tailwind utilities;')

def setup_ui_assets():
    """Copia gli assets necessari per l'UI"""
    # Directory degli assets
    assets_dir = base_dir / 'assets'
    ui_assets_dir = base_dir / 'src/naiad/ui/static'
    
    # Assicurati che le directory esistano
    assets_dir.mkdir(exist_ok=True)
    ui_assets_dir.mkdir(exist_ok=True)
    
    # Copia gli assets se necessario
    # TODO: Aggiungere la copia degli assets quando saranno disponibili

def main():
    """Funzione principale di setup"""
    # Crea le directory
    for dir_path in required_dirs:
        Path(base_dir / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Creata directory: {dir_path}")

    # Crea i file requirements
    for filename, content in requirements.items():
        with open(base_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Creato file: {filename}")

    # Setup Tailwind
    setup_tailwind()
    print("Configurazione Tailwind completata")

    # Setup UI assets
    setup_ui_assets()
    print("Setup assets UI completato")

    print("\nStruttura del progetto creata con successo!")
    print("\nPer completare l'installazione:")
    print("1. Installa le dipendenze: pip install -r requirements-dev.txt")
    print("2. Installa Tailwind CLI: npm install -D tailwindcss")
    print("3. Genera il CSS: npx tailwindcss -i ./src/naiad/ui/static/css/input.css -o ./src/naiad/ui/static/css/output.css --watch")


if __name__ == '__main__':
    main()

