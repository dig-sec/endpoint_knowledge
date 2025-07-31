The MITRE ATT&CK technique T1055 is "Registry Run Keys and Values". It involves modifying the Registry by creating and deleting keys, changing values, and modifying their permissions. 

Here are some rules for detecting T1055 on Windows systems:

1. Any changes to the system Registry should be monitored and logged for further investigation.
2. Detection of unauthorized attempts to create or modify Registry keys or values in critical areas of the system should trigger an alert.
3. Monitoring of registry key permissions to identify unexpected modifications to read-only keys, such as those related to security settings or boot configuration files.
4. Anomalies in user account control (UAC) settings may be indicative of T1055 activity, and should trigger an alert.
5. Monitoring of Registry hives with high-risk values, such as System, Security, System Configuration, Local Services, System Events, Software Installation, and Start Menu.
6. Detection of Registry keys and values that have been deleted or moved to non-critical locations should be considered suspicious activity.
7. Any attempts to modify the Registry in a scripted manner with tools like REGEDIT may also indicate T1055 activity, and should trigger an alert.