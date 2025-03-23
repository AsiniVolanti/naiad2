# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import PyInstaller.config

# Ottieni il percorso root del progetto
project_root = Path('.')

block_cipher = None

# Configurazione dei dati UI da includere
ui_datas = [
    (str(project_root / 'src' / 'naiad' / 'ui' / 'templates'), 'ui/templates'),
    (str(project_root / 'src' / 'naiad' / 'ui' / 'static' / 'css'), 'ui/static/css'),
    (str(project_root / 'src' / 'naiad' / 'ui' / 'static' / 'js'), 'ui/static/js'),
    (str(project_root / 'src' / 'naiad' / 'ui' / 'static' / 'img'), 'ui/static/img'),
]

# Dati esistenti
core_datas = [
    (str(project_root / 'examples'), 'examples'),
    (str(project_root / 'assets' / 'AsinoVolante.ico'), 'assets'),
]

# Combina tutti i dati
all_datas = core_datas + ui_datas

# Configurazione Analysis
a = Analysis(
    [str(project_root / 'src' / 'naiad' / 'core' / 'main.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=all_datas,
   hiddenimports=[
        # Core dependencies
        'win32timezone',
        'keyboard',
        'yaml',
        'anthropic',
        'openai',
        'asyncio',
        'logging.handlers',
        'gtts',
        'pygame',
        'pyperclip',
        'win32com.client',
        
        # Webview dependencies
        'webview',
        'webview.platforms.winforms',
        'pythoncom',
        'win32api',
        'win32con',
        'win32gui',
        'clr',
        'System',
        'System.Windows.Forms',
        'System.Drawing',
        
        # Additional runtime dependencies
        'importlib.metadata',
        'pkg_resources',
        'packaging',
        'packaging.version',
        'packaging.requirements',
        'packaging.markers',
        'packaging.specifiers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['System.Windows.Forms', 'System.Drawing'], 
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Configurazione PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Configurazione EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NAIAD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False per nascondere la console in produzione
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'AsinoVolante.ico'),
    version='file_version_info.txt',  # Informazioni sulla versione del file
)

# Collection per l'installer
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NAIAD',
)