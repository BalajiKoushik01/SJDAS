@echo off
echo ==================================================
echo      SJ-DAS World-Class Textile Designer
echo ==================================================
echo.
echo [INFO] Activating Virtual Environment...
call venv\Scripts\activate.bat

echo [INFO] Setting Environment Variables...
set QT_API=pyqt6

echo [INFO] Verification Check (PyQt6)...
venv\Scripts\python.exe -c "import PyQt6; print('PyQt6 OK')" 
if errorlevel 1 (
    echo [ERROR] PyQt6 missing. Repairing...
    venv\Scripts\python.exe -m pip install PyQt6
)

echo [INFO] Verification Check (FluentWidgets)...
venv\Scripts\python.exe -c "import qfluentwidgets; print('FluentWidgets OK')"
if errorlevel 1 (
    echo [ERROR] FluentWidgets missing or incompatible.
    echo [INFO] Re-installing PyQt6-Fluent-Widgets...
    venv\Scripts\python.exe -m pip install --force-reinstall --no-deps PyQt6-Fluent-Widgets PyQt6-Frameless-Window
)

echo [INFO] Launching Application...
venv\Scripts\python.exe launcher.py
pause
