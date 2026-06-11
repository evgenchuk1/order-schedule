@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
"C:\Users\etsip\AppData\Local\Programs\Python\Python312\python.exe" "C:\Users\etsip\order-schedule-repo\.github\scripts\notify.py" >> "C:\Users\etsip\order-schedule-repo\notify.log" 2>&1
