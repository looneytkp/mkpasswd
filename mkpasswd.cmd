@echo off
powershell -ExecutionPolicy Bypass -File "%USERPROFILE%\.mkpasswd\mkpasswd.ps1" %*
