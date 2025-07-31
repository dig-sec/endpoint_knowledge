# Technique T1064: SyncToast Notification

## Overview
Category: User Interface and Desktop
Platform: Windows
MITRE ID: T1064

Synchronized Toast notifications are a type of notification that appears on the taskbar in Windows. They can be used to display important information or reminders, such as system alerts or weather updates. Adversaries may use this technique to deliver malicious content without raising suspicion from users.

## Technical Details
Synchronized Toast notifications are displayed using the SyncToast API in Windows. The API allows developers to create and display synchronized toasts that automatically update when they need to be updated, such as when new email arrives or a weather forecast is refreshed. Adversaries can exploit this feature by creating malicious toasts that appear on users' taskbars without the user knowing. These toasts are designed to look like legitimate notifications and may contain links or other content that can be used for phishing attacks, data exfiltration, or other malicious activities.

## Adversary Use Cases
Attackers may use Synchronized Toast notifications to deliver malware or exploit vulnerabilities in Windows. For example, an attacker could create a malicious toast that appears on the taskbar and prompts users to install a fake security update. When the user clicks the button to install the update, it triggers a script that downloads and runs a malicious program.

Attackers may also use Synchronized Toast notifications as a way to deliver command-and-control (C2) messages or other communications with compromised systems. For example, an attacker could create a synchronized toast that appears on the taskbar and prompts users to visit a website or click a link. The website or link may contain malicious code that gives the attacker control over the system, allowing them to execute commands or steal data.

## Platform-Specific Implementation
The SyncToast API is available on Windows 7 and later versions of the operating system. Adversaries can use it by creating a toast message with a unique ID that will be displayed in the taskbar notification area (TNA). The toast message can contain any content, including links or other executable code. When the TNA is displayed, it automatically updates based on whatever data the attacker has specified, such as new email messages or weather forecasts.

## Detection Considerations
There are several indicators that may suggest a malicious synchronized toast has been delivered:
1. Unexpected and unexpectedly large changes to TNA content (e.g., sudden appearance of a new toast)
2. Incorrect or misleading information presented in the TNA
3. Unusual behavior associated with clicking on a link or executing code within the TNA
4. An increase in system resource usage, such as CPU or memory utilization, that is not associated with normal system activity
5. Unusual network traffic patterns, including outbound connections to external domains or IP addresses

Defenders can monitor these indicators and use security tools to detect and block suspicious synchronized toasts before they are delivered to users. Additionally, organizations can implement policies that prevent the installation of untrusted software and restrict access to sensitive data on company devices.