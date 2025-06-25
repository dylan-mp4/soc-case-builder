# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    binaries=[],
    datas=[
        ('src/resources/version.py', 'resources'),
        ('src/resources/__init__.py', 'resources'),
        ('src/ui/*.py', 'ui'),
        ('src/utils/*.py', 'utils'),
        ('src/assets', '_internal/assets')
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
    runtime_hooks=[],
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

# --- ADD THIS PATCH FOR RELIABLE IMPORTS IN BUNDLED MODE ---
# Ensure the resources and utils folders are at the top level of the bundle
# and add a runtime hook to set sys.path at runtime

# Create a runtime hook file to add the bundled directories to sys.path
with open('add_bundle_paths.py', 'w') as f:
    f.write(
        "import sys, os\n"
        "bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))\n"
        "for subdir in ['resources', 'utils', 'ui']:\n"
        "    path = os.path.join(bundle_dir, subdir)\n"
        "    if os.path.isdir(path) and path not in sys.path:\n"
        "        sys.path.insert(0, path)\n"
    )

# Add the runtime hook to the Analysis
a.runtime_hooks.append('add_bundle_paths.py')