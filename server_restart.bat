@echo off

:: Закрываем серверный процесс

taskkill /F /IM server.exe 2>nul

:: Ждем секунду для полного закрытия
timeout /t 1 /NOBREAK > nul

:: Запускаем сервер без окна CMD
start /B server.exe

exit 