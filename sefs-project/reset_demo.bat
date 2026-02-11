@echo off
echo Resetting SEFS demo...
echo.

cd sefs_root

echo Moving files back to root...
for /r %%f in (*.txt *.pdf) do (
    if not "%%~dpf"=="%CD%\" (
        move "%%f" . >nul 2>&1
    )
)

echo Removing empty folders...
for /d %%d in (*) do (
    rmdir "%%d" >nul 2>&1
)

echo.
echo Done! Files are back in root directory.
echo Run START.bat to restart the system.
pause
