@echo off
cd /d %~dp0

if "%~1"=="" (
  call python elements-rpc.py sign
) else (
  call python elements-rpc.py sign -i "%~1"
)

pause
