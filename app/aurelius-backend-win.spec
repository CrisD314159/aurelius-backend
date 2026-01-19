# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_all

torch_data = collect_all('torch')
trans_data = collect_all('transformers')
tok_data = collect_all('tokenizers')

datas = torch_data[0] + trans_data[0] + tok_data[0]
binaries = torch_data[1] + trans_data[1] + tok_data[1]
hiddenimports = torch_data[2] + trans_data[2] + tok_data[2]

hiddenimports += [
    'watchfiles',
    'multiprocessing',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.asyncio',      
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.h11_impl', 
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
]

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['uvloop'], # Forzamos la exclusión de uvloop
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='aurelius-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,             
    console=True,          
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='aurelius-backend',
)