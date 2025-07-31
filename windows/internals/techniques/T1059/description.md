# Technique T1059: Command and Scripting Interpreter

## Overview
- Category: Execution
- Platform: Windows
- MITRE ID: T1059

## Technical Details
Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries. These interfaces and languages provide ways of interacting with computer systems and are a common feature across many different platforms. Most systems come with some built-in command-line interface and scripting capabilities, for example, macOS and Linux distributions include some flavor of Unix Shell while Windows installations include the Command shell and PowerShell.

## Adversary Use Cases
Attackers use command and scripting interpreters to:
- Execute malicious commands and scripts
- Download and execute additional payloads
- Perform reconnaissance and enumeration
- Establish persistence mechanisms
- Move laterally through networks

## Platform-Specific Implementation
On Windows systems, common interpreters include:
- **Command Prompt (cmd.exe)**: Traditional Windows command interpreter
- **PowerShell**: Advanced scripting environment with .NET integration
- **Windows Script Host (WSH)**: Supports VBScript and JScript execution
- **Batch files**: Script files executed by cmd.exe

## Detection Considerations
Monitor for execution of interpreters and unusual command-line activity including:
- Suspicious command-line arguments
- Encoded or obfuscated commands
- Network connections initiated by interpreters
- Execution of scripts from unusual locations