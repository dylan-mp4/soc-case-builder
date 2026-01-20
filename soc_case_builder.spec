# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    binaries=[],
    datas=[
        ('src/ui_flet/config', 'ui_flet/config'),
        ('src/resources', 'resources'),
        ('src/utils', 'utils'),
    ],
    hiddenimports=[
        'flet',
        'certifi',
        'websockets',
        'sqlite3',
        'charset_normalizer',
        'idna',
        'requests',
        'urllib3',
        'packaging',
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