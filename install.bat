REM @echo off

cd %userprofile%
python -m venv %userprofile%\guienv

powershell -command "& {Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force}"

call %userprofile%\guienv\Scripts\activate

pip install matplotlib numpy pandas opencv-python



