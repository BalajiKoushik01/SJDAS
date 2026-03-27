# -*- mode: python ; coding: utf-8 -*-
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Use project-relative venv path for portability and accuracy
project_root = os.path.abspath(os.getcwd())
site_packages = os.path.join(project_root, 'venv', 'Lib', 'site-packages')

# Warm-up imports to resolve DLL collisions during Analysis (using venv)
if site_packages not in sys.path:
    sys.path.append(site_packages)

try:
    import torch
    import cv2
    import numpy as np
except Exception:
    pass

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sj_das/resources', 'sj_das/resources'),
        ('sj_das/assets', 'sj_das/assets'),
        ('sj_das/weaves', 'sj_das/weaves'),
        ('sj_das', 'sj_das'),
        ('sj_das/ui/digital_twin_view.py', 'sj_das/ui'),
        (os.path.join(site_packages, 'torch'), 'torch'),
        (os.path.join(site_packages, 'torchvision'), 'torchvision'),
        (os.path.join(site_packages, 'cv2'), 'cv2'),
        (os.path.join(site_packages, 'numpy'), 'numpy'),
        (os.path.join(site_packages, 'scipy'), 'scipy'),
        (os.path.join(site_packages, 'diffusers'), 'diffusers'),
        (os.path.join(site_packages, 'transformers'), 'transformers'),
        (os.path.join(site_packages, 'huggingface_hub'), 'huggingface_hub'),
    ],
    hiddenimports=[
        'diffusers', 'transformers', 'accelerate', 'safetensors',
        'huggingface_hub', 'PIL.Image', 'rembg', 'vobject',
        'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngine', 'PyQt6.QtPrintSupport',
        'PyQt6.QtWebChannel', 'PyQt6.QtPositioning',
        'PyQt6.QtQuick', 'PyQt6.QtQml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_env_patch.py'],
    excludes=['torch', 'torchvision', 'cv2', 'numpy', 'scipy'],
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
    name='SJDAS_Enterprise',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None, 
)
