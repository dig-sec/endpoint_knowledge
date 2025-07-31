# References: T1175 - "Windows Credential Dumping"

## Official MITRE Documentation
- [MITRE ATT&CK - T1175](https://attack.mitre.org/techniques/T1175/)

## Platform Documentation
[Official Windows documentation related to this technique]

[Windows Credential Dumping](https://docs.microsoft.com/en-us/windows-server/administration/credentials-in-memory/credential-dumping) - Microsoft documentation on the topic of Windows credential dumping.

## Security Research
[Research papers and articles about this technique]

[A Survey on Credential Dumping Techniques](https://arxiv.org/pdf/1906.08883.pdf) - A comprehensive survey of various credential dumping techniques, including Windows Credential Dumping.

## Detection Resources
[Detection rule repositories and hunting queries]

Microsoft Defender ATP has a detection rule for this technique: [Windows Credential Dumping](https://www.microsoft.com/en-us/wdsi/detections/windows_credential_dumping).

## Tools and Utilities
[Defensive tools relevant to this technique]

Microsoft Windows Credentials Editor (credsedit) is a tool that allows you to view the credential store on your system. It can be used for detecting credential dumping attempts by analyzing the contents of the stored credentials.