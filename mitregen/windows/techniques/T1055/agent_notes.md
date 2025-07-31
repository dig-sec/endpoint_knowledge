[Windows OS]
- File: %systemroot%\System32\drivers\etc\hosts
- Access Type: Read/Write
- Data Format: Text
- Scope: Domain Controller
T1055 (PowerShell) is a PowerShell command that can be used to modify the host file. This technique involves adding entries in the host file, which can redirect certain domain names or IP addresses to another destination. 
By default, the hosts file resides in the System32 folder of the Windows operating system and contains the list of hosts and their corresponding IP address mappings. To access this file using PowerShell, you can use the following code:
```
$hostFile = Get-Content '%systemroot%\System32\drivers\etc\hosts'
$IPAddresses = $hostFile -match "([^#]+)"
ForEach ($IPAddress in $IPAddresses) {
 Write-Host "$($IPAddress) redirected to '$($IPAddress)'"
}
```
This code uses the `Get-Content` and `-match` methods to extract all IP addresses from the host file. The resulting list of IP addresses is then passed to the `ForEach-Object` loop, which displays each IP address with its corresponding redirected destination.
To modify this file, you can use the `Set-Content` method, which takes in a string as input and outputs it into the specified path. For example:
```
$newIP = "10.10.10.1"
$oldIP = $hostFile -match "([^#]+)" | ?{$_.Groups[2].Value -eq "$($newIP)"}
Set-Content '%systemroot%\System32\drivers\etc\hosts' -Value ""
Set-Content '%systemroot%\System32\drivers\etc\hosts' -Value "10.10.10.1 redirected to $($newIP)"
```
This code uses the `Find` method with a regex pattern to extract the IP address that needs to be modified from the host file. It then uses the same regex pattern to search for this specific IP address in the host file and replaces it with the new destination using the `-Value` parameter of `Set-Content`.
Note: The `Write-Host` command is used here only for demonstration purposes, as the output will be displayed on screen. To redirect the output to a specified file or console, use appropriate methods like `Out-File`, `Out-String`, etc.