@echo off
chcp 65001 >nul
echo Запуск сервера. Якщо ключ ще не встановлено, виконайте:
echo   set OPENAI_API_KEY=sk-proj-ваш_ключ
echo а потім знову запустіть run_server.bat або: python manage.py runserver
echo.
python manage.py runserver %*
