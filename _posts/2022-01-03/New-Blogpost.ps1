function New-Blogpost {
    param([int]$AddDays = 0)
    
    $date = (get-date).AddDays($AddDays).ToString('yyyy-MM-dd')

    New-Item -ItemType directory -Path ".\$date"

$filedata = 
"---
title: Basic PowerShell function to create folder
tags:
- 100DaysOfCode
- Powershell
comments: true
---
"

    New-Item -ItemType File -Value $filedata -Path ".\$date\$date-blogpost.md"

    code ".\$date\$date-blogpost.md"
}