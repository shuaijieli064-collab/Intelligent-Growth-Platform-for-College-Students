# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec - 大学生智能成长平台 GUI 打包配置.

请从项目根目录执行打包：
    cd <项目根目录>
    pyinstaller deploy/build.spec --clean --noconfirm
"""
from pathlib import Path

_PROJECT_ROOT = Path.cwd()

block_cipher = None

a = Analysis(
    [str(_PROJECT_ROOT / 'main.py')],
    pathex=[str(_PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(_PROJECT_ROOT / 'sql' / '*.sql'), 'sql'),
        (str(_PROJECT_ROOT / 'config.example.json'), '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.figure',
        'sklearn.linear_model',
        'sklearn.ensemble',
        'sklearn.preprocessing',
        'sklearn.model_selection',
        'sklearn.metrics',
        'pandas',
        'networkx',
        'pymysql',
        'scipy',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'pytest',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='大学生智能成长平台',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    icon=str(_PROJECT_ROOT / 'frontend' / 'public' / 'logo-icon.jpg'),
)
