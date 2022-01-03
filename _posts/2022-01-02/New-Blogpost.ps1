function New-Blogpost {
    param()
    
    $date = get-date -Format yyyy-MM-dd

    New-Item -ItemType directory -Path ".\$date"

$filedata = 
"---
title: New Blog Title
tags:
- 100DaysOfCode
- PowerShell
comments: true
---"

    New-Item -ItemType File -Value $filedata -Path ".\$date\$date-blogpost.md"

    code ".\$date\$date-blogpost.md"
}