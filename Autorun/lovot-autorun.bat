@echo off
cd "C:\Users\RNUC11PAHi70000\Documents\Program Lovot\Lovot_Pemkot"
cmd /c "Set-ExecutionPolicy Unrestricted -Scope Process"
cmd /c "venv-lovot/Scripts/activate/"
cmd /c "python App/Gemini/main.py"