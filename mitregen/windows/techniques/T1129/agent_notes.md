Technique Name: Credentials Dumping
Description: This technique involves accessing credentials from a user and using them to log into the system or gain further access to data, applications, or services. It can also be used to dump local or domain accounts' passwords in cleartext.

In Windows environment, there are multiple ways to dump credential information such as by leveraging keyloggers or by taking advantage of vulnerabilities like Kerberos protocol weaknesses that allow unauthenticated authentication. 

Keyloggers: Keylogger software can be used to capture and record keystrokes, mouse movements, and other user actions on a system. These logs are then transferred to the attacker's device for later analysis and use. In Windows environment, keylogger can be installed by installing third-party applications that run without user permission and collect all activity from the victim's computer.

Kerberos Vulnerabilities: Kerberos is a network protocol used by many modern operating systems to secure authentication. Attackers can exploit vulnerabilities in this protocol, such as KRACK, to extract credentials from the system without any user interaction.

Other Methods: There are other ways to dump credentials from Windows environment like using PowerShell cmdlets, accessing credential hashes stored in LSASS memory or through third-party applications that can be installed on a compromised system to collect and dump passwords.