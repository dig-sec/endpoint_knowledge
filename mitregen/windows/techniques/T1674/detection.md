Sure, here are some detection rules for MITRE ATT&CK technique T1674 (Windows):

1. Registry key changes related to the "runas" command and the "netstartup" group policy object (GPO). Any changes made to these keys should be investigated as a potential indicator of T1674 activity on Windows machines.
2. Changes in the Windows registry related to the "services" key, specifically the "startup" value for any services associated with T1674 techniques or tools.
3. Any new processes created by services associated with T1674 techniques should be monitored and investigated for suspicious behavior.
4. Changes in the Windows event logs related to security-related events (such as "Account Logon", "System Events", "Event Forwarding", etc.) that may indicate the use of T1674 tools or techniques.
5. Any new user accounts created on a Windows machine, particularly if they have been created with a high level of privilege (i.e., "administrator" account) should be investigated for suspicious activity related to T1674.