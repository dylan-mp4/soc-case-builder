# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# --- Custom code: create a runtime hook file before Analysis ---
with open('add_bundle_paths.py', 'w') as f:
    f.write(
        "import sys, os\n"
        "bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))\n"
        "for subdir in ['resources', 'utils', 'ui']:\n"
        "    path = os.path.join(bundle_dir, subdir)\n"
        "    if os.path.isdir(path) and path not in sys.path:\n"
        "        sys.path.insert(0, path)\n"
    )

a = Analysis(
    ['src/main.py'],
    binaries=[],
    datas=[
        ('src/resources', 'resources'),
        ('src/ui', 'ui'),
        ('src/utils', 'utils'),
        ('src/assets', 'assets')
    ],
    hiddenimports=[
        'certifi',
        'charset_normalizer',
        'idna',
        'PyQt6',
        'PyQt6.Qt6',
        'PyQt6.sip',
        'PyQt6.QtSvgWidgets',
        'requests',
        'urllib3',
        'altgraph',
        'packaging',
        'pefile',
        'pyenchant',
        'pywin32-ctypes',
        'setuptools',
        'pyenchant',
        'enchant',
        'enchant.checker',
        'enchant.tokenize',
        're',
        'flask',
        'flask_cors'
    ],
    hookspath=[],
    runtime_hooks=['add_bundle_paths.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='soc_case_builder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='soc_case_builder',
)