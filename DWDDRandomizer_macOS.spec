# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ui_tkinter.py'],
    pathex=['.'],
    binaries=[],
    datas=[('public/dusk_transparent.png', 'public')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DWDDRandomizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, 
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True, 
    target_arch=None,
    codesign_identity=None, 
    entitlements_file=None, 
    icon="public/dusk_transparent.png", 
    version="version_info.txt"
)
coll = BUNDLE(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False, 
    upx_exclude=[],
    icon='public/dusk_transparent.ico'
    name='DWDDRandomizer.app',
)