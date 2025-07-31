# Code Samples: T1059 Command and Scripting Interpreter

This folder contains code examples demonstrating the use of command and scripting interpreters on Windows systems. These samples help illustrate technique T1059 for research, detection, and automation purposes.

## Example: Running a Command with PowerShell

```powershell
# Execute a simple command
Get-Process
```

## Example: Running a Command with CMD

```batch
REM List running tasks
TASKLIST
```

## Example: Using WScript

```vbscript
Set WshShell = WScript.CreateObject("WScript.Shell")
WshShell.Run "notepad.exe"
```
