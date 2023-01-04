@echo off
set PROXY=proxyhe.rd1.rf1:8080
set ROOT_DIR=D:\env_pdf
set PYTHON=C:\"Program Files"\Python\Python38\python.exe

%PYTHON% -m venv %ROOT_DIR%
call %ROOT_DIR%\Scripts\activate.bat

REM Path to the virtual environnement
set PYTHONENV=%ROOT_DIR%\Scripts\python.exe
REM Installing needed packages
%PYTHONENV% -m pip --proxy=%PROXY% install --upgrade pip
%PYTHONENV% -m pip --proxy=%PROXY% install -r %~dp0requirements.txt 
call %ROOT_DIR%\Scripts\deactivate.bat
