# app.spec — one-file build including ./task.db and ./screen_data
# Build with: pyinstaller app.spec

import os

block_cipher = None

# Collect all files under ./screen_data into datas, preserving folder structure
datas = []  # put task.db next to your executable at runtime
for root, _, files in os.walk('screen_data'):
    for f in files:
        src = os.path.join(root, f)
        rel = os.path.relpath(root, 'screen_data')
        dest = os.path.join('screen_data', rel) if rel != '.' else 'screen_data'
        datas.append((src, dest))
print("Included data files:")
for src, dest in datas:
    print(f"  {src} -> {dest}")
a = Analysis(
    ['main.py'],          # <- your entry script here
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-file build: include binaries/zipfiles/datas directly in EXE; no COLLECT step
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AjinDeckit',           # <- desired exe name (without .exe)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # default temp dir for onefile extraction
    console=True,         # set to False if you want a windowed app (no console)
)
