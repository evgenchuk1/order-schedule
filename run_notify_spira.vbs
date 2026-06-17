Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "cmd /c set PYTHONIOENCODING=utf-8 && " & Chr(34) & "C:\Users\etsip\AppData\Local\Programs\Python\Python312\python.exe" & Chr(34) & " " & Chr(34) & "C:\Users\etsip\order-schedule-repo\.github\scripts\notify_spira.py" & Chr(34), 0, True
Set shell = Nothing
