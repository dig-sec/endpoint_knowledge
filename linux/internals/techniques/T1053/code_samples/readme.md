# Code Samples: T1053 Cron Job Manipulation

This folder contains code examples for creating and modifying cron jobs on Linux systems.

## Example: Add Cron Job
```bash
echo "* * * * * /path/to/malicious.sh" >> /etc/crontab
```

## Example: List Cron Jobs
```bash
crontab -l
```
