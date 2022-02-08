---
title: Adding functions for Windows to PowerShell Profile 
tags:
 - 100DaysOfCode
 - PowerShell
 - "PowerShell Profile"
categories:
- Blog
comments: true
header:
  teaser: "/assets/images/teasers/powershell-prompt.png"
---
For Day 15 of 100 Days of code, I wanted to build out my PowerShell Profile a little bit more, and focus on Windows Administration
## PowerShell Functions

```PowerShell
function get-windows-build {
	Get-CimInstance -Class Win32_OperatingSystem
}
function get-path {
	($Env:Path).Split(";")
}
function get-serial-number {
    Get-CimInstance -ClassName Win32_Bios | select-object serialnumber
  }

function edge {
    & "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
  }

function get-free-space {
    Get-CimInstance -Class Win32_LogicalDisk |
Select-Object -Property Name, @{
    label='FreeSpace'
    expression={($_.FreeSpace/1GB).ToString('F2')}
  }
}
```
## Conclusion

For Day 15, in my PowerShell Profile, I created a new file called windows.ps1 put it in my `$ProifileDir` with these functions and load it via my PowerShell Profile.

```PowerShell
foreach ( $includeFile in ("azure", "defaults", "openssl", "dev", "windows") ) {
    Unblock-File $profileDir\$includeFile.ps1
. "$profileDir\$includeFile.ps1"
}
```