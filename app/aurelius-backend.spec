# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
import spacy

datas = []
binaries = []
hiddenimports = [
    'httptools', 
    'watchfiles', 
    'multiprocessing',
    # Critical uvicorn imports for lifespan
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
]

# Add spaCy model data
try:
    spacy_model_path = spacy.util.get_package_path('en_core_web_sm')
    datas.append((str(spacy_model_path), 'en_core_web_sm'))
    print(f"✓ Found spaCy model at: {spacy_model_path}")
except Exception as e:
    print(f"WARNING: en_core_web_sm not found: {e}")
    print("Install with: python -m spacy download en_core_web_sm")

hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('torchaudio')
hiddenimports += collect_submodules('transformers')
hiddenimports += collect_submodules('faster_whisper')
hiddenimports += collect_submodules('spacy')
hiddenimports += collect_submodules('en_core_web_sm')

tmp_ret = collect_all('language_tags')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('csvw')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('segments')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('phonemizer')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('kokoro')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('espeakng_loader')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect spaCy data
tmp_ret = collect_all('spacy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='aurelius-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    upx=True,
    upx_exclude=[],
    name='aurelius-backend',
)