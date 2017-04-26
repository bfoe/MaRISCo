@echo "-------------------------------------------------------"
@echo "| Running pyinstaller to build standalone for Windows |"
@echo "-------------------------------------------------------"
@echo .
@echo .
@echo off
C:\Python27\scripts\pyinstaller MaRISCo_Windows_build.spec
copy dist\MaRISCo.exe ..
rmdir /Q /S build
rmdir /Q /S dist
pause
