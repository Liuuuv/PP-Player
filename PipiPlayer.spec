# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\olivi\\kDrive\\projets\\loisir\\music_player\\music_player\\assets', 'assets'), ('C:\\Users\\olivi\\kDrive\\projets\\loisir\\music_player\\music_player\\ai_music_data.json', '.'), ('C:\\Users\\olivi\\kDrive\\projets\\loisir\\music_player\\music_player\\downloads_path.txt', '.')]
binaries = []
hiddenimports = ['yt_dlp']
datas += collect_data_files('customtkinter')
tmp_ret = collect_all('pygame')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('mutagen')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('Pmw')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\olivi\\kDrive\\projets\\loisir\\music_player\\music_player\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['C:\\Users\\olivi\\kDrive\\projets\\loisir\\music_player\\pyi_hooks\\alias_init.py'],
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
    name='PipiPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\olivi\\kDrive\\projets\\loisir\\music_player\\music_player\\assets\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PipiPlayer',
)
