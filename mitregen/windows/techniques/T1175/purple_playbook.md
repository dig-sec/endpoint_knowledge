# Purple Team Playbook: T1175 - Scheduled Task

## Objective
Test detection and response capabilities for this technique on Windows.

## Red Team Activities
### Setup
Prerequisites and environment setup:
- Install Windows with latest updates
- Create a new user account with administrator privileges
- Create a new scheduled task to run at a specific time or when the machine is idle

Execution Steps:
1. Add a scheduled task using Task Scheduler
2. Name it as "ScheduledTask" and select "Run whether user is logged on or not" option
3. Set the trigger condition to run every 5 minutes
4. In the action tab, add an executable file which has the command "cmd /c c:\program files (x86)\mimikatz\startup\powershell.exe -executionpolicy remotesigned -file c:\program files (x86)\mimikatz\startup\attack-scheduledtask-t1175.ps1"
5. Save the task and assign administrator privileges to it.

Expected Artifacts:
- Log entries showing the execution of scheduled tasks
- Network traffic logs showing the command line parameters being executed

## Blue Team Activities
Pre-Exercise:
- Configure endpoint detection and response solution for real-time monitoring and alert verification
- Set up rules and policies to identify potential malicious activities such as process creation, network communication, file access, etc.
- Enable logging and auditing capabilities for the scheduled tasks

During Exercise:
- Real-time monitoring and alert verification during the execution of the scheduled task
- Analyze log entries and network traffic to identify any suspicious activities or potential threats

Post-Exercise:
- Perform post-exercise analysis to identify any improvements in detection and response capabilities for future exercises
- Recommend changes to endpoint protection policies, rule sets, or other security controls to improve the detection and prevention of this technique.