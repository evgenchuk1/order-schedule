@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
python "C:\Users\etsip\order-schedule-repo\.github\scripts\notify.py" >> "C:\Users\etsip\order-schedule-repo\notify.log" 2>&1
