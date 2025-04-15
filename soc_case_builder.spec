# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['d:/Dev/soc-case-builder'],
    binaries=[],
    datas=[
        ('src/resources/version.py', 'resources'),
        ('src/resources/__init__.py', 'resources'),
        ('src/ui/*.py', 'ui'),
        ('src/utils/*.py', 'utils')
        ('assets', 'assets')
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
        're'
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