# Detection Logic: T1059

## Windows
- Monitor process creation events for command interpreters (cmd.exe, powershell.exe, wscript.exe)
- Use Sysmon or EDR to alert on suspicious command-line arguments
- Correlate with user context and parent process
