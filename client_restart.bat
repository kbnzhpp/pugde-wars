@echo off

:: Закрываем клиентский процесс
taskkill /F /IM main.exe 2>nul

:: Ждем секунду для полного закрытия
timeout /t 1 /NOBREAK > nul

:: Запускаем клиент без окна CMD
start /B main.exe

exit 