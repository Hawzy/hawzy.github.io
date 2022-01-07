---
title: New-Blogpost - Upgrading a PowerShell function to add parameters
tags:
- 100DaysOfCode
- Powershell
- Github
- Jekyll
- 2022
categories:
- Blog
comments: true
---

In my previous post I created a basic PowerShell function that creates a folder with the current date.  Today I'm going to add a small bit of functionality to allow me to choose to create a folder for future (or past) days.

## Adding Paramaters

First we update the param block to be
`param([int]$AddDays = 0)`. This says the function will now accept an integer via a parameter called `-AddDays` which defaults to 0 if no number is chosen.

## Adding Days

Initially I tried just modifying my previous line to include the .AddDays method `$date = (get-date -Format yyyy-MM-dd).AddDays($AddDays)` This failed with the error message:

 **InvalidOperation: Method invocation failed because [System.String] does not contain a method named 'AddDays'.**

 This happens because when get-date is run with the -format parameter it outputs a string which is no longer a datetime object.  But we can get around this by rejiggering the code to be `$date = (get-date).AddDays($AddDays).ToString('yyyy-MM-dd')` when we do it this way, the days are added before it is formatted as a string object.

## Final Script

 ```powershell
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
- 2022
categories:
- Blog
comments: true
---"

    New-Item -ItemType File -Value $filedata -Path ".\$date\$date-blogpost.md"

    code ".\$date\$date-blogpost.md"
}
 ```

## Conclusion

Now I can create future folder structures by running the command `New-Blogpost -AddDays 1` or even in the past by using negative numbers. That wraps up my 100 days of code blog day 3.
