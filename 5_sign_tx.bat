@echo off
cd /d %~dp0

if "%~1"=="" (
  call pipenv run sign
) else (
  call pipenv run sign -i "%~1"
)

pause
