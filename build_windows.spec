# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['launcher.py'],
    binaries=[],
    datas=[
        ('index.html', '.'),
        ('icon.ico',   '.'),
        ('bridge.py',  '.'),
    ],
    hiddenimports=collect_submodules('webview') + ['bridge'],
    excludes=['PyQt6', 'streamlit', 'pandas', 'numpy'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='na_avos',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
    onefile=True,
)
