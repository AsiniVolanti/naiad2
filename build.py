import os
import sys
import logging
from pathlib import Path
import subprocess
import argparse
from datetime import datetime

def setup_logging():
    """Configura il logging per il processo di build"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / f'build_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    return logging.getLogger('NAIAD_Build')

def get_project_root():
    """Ottiene il percorso root del progetto"""
    return Path(__file__).resolve().parent

def verify_project_structure(project_root: Path, logger) -> bool:
    """Verifica la presenza dei file necessari per il build"""
    logger.info("Verifica dei file necessari per il build...")
    
    required_files = {
        'src/naiad/core/main.py': project_root / 'src' / 'naiad' / 'core' / 'main.py',
        'assets/AsinoVolante.ico': project_root / 'assets' / 'AsinoVolante.ico',
        'naiad.spec': project_root / 'naiad.spec'
    }
    
    missing_files = []
    for name, path in required_files.items():
        if not path.exists():
            missing_files.append(name)
            logger.error(f"File richiesto mancante: {name}")
    
    if missing_files:
        logger.error("Verifica fallita - file mancanti")
        return False
        
    logger.info("Verifica completata con successo")
    return True

def run_command(cmd, logger, cwd=None):
    """Esegue un comando di sistema e gestisce l'output"""
    logger.info(f"Esecuzione comando: {' '.join(str(x) for x in cmd)}")
    try:
        # Usa subprocess.run invece di Popen per semplicità
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            check=False  # Non sollevare eccezioni per codici di uscita non zero
        )
        
        # Registra output standard
        for line in result.stdout.splitlines():
            if line and not line.startswith('WARNING:'):
                logger.info(line)
        
        # Registra errori
        for line in result.stderr.splitlines():
            if 'ERROR:' in line or 'CRITICAL:' in line:
                logger.error(line)
            elif line:
                logger.warning(line)
        
        # Gestisci il codice di uscita
        if result.returncode != 0:
            logger.error(f"Comando fallito con codice di uscita: {result.returncode}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
            
        return result
        
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del comando: {e}")
        raise

def build_naiad(args, logger):
    """Esegue il processo di build"""
    try:
        project_root = get_project_root()
        logger.info(f"Avvio build NAIAD da: {project_root}")
        
        # Verifica struttura del progetto
        if not verify_project_structure(project_root, logger):
            return False
            
        # Verifica PyInstaller
        try:
            import PyInstaller
            logger.info(f"PyInstaller versione: {PyInstaller.__version__}")
        except ImportError:
            logger.error("PyInstaller non trovato. Installare con: pip install pyinstaller")
            return False
        
        # Directory di output
        dist_dir = project_root / 'dist'
        spec_file = project_root / 'naiad.spec'
        
        # Esegui PyInstaller
        logger.info("Avvio build con PyInstaller...")
        cmd = [
            sys.executable,
            '-m',
            'PyInstaller',
            '--clean',
            '--noconfirm',
            '--log-level=DEBUG',  # Cambia da ERROR a DEBUG per informazioni dettagliate
            # Rimosso usando uno spec '--debug=all',         # Aggiunge debugging completo
            str(spec_file.resolve())
        ]
        
        run_command(cmd, logger, cwd=str(project_root))
        
        # Verifica risultato
        exe_path = dist_dir / 'NAIAD.exe'
        if not exe_path.exists():
            logger.error(f"Build completato ma executable non trovato in: {exe_path}")
            return False
            
        logger.info(f"Build completato con successo! Executable creato in: {exe_path}")
        return True
        
    except Exception as e:
        logger.error(f"Errore durante la build: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Build NAIAD')
    parser.add_argument('--version', default='1.0.0', help='Versione del build')
    parser.add_argument('--install-deps', action='store_true', help='Installa dipendenze')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    try:
        success = build_naiad(args, logger)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Errore fatale durante la build: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()