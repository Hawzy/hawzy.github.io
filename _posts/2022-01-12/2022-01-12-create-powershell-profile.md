---
title: Creating a PowerShell Profile Repository
tags:
- 100DaysOfCode
- PowerShell
- PowerShell Profile
- Github
categories:
- Blog
comments: true
---
For day 11 of 100 Days of Code, I'm going to create a new repo to host my PowerShell Profile.  The profile gets auto-loaded when you launch the PowerShell Console depending on your user context.  So I'm going to populate it with useful commands, modules, configs, themes and cmdlets so that whenever I set up a new computer I can copy down my settings and be ready to go.  You can see the location of the different profile types by running `$profile | select *`

## Resources

Couple links and profiles that had some good stuff in them.

* [https://github.com/mikemaccana/powershell-profile](https://github.com/mikemaccana/powershell-profile)
* [https://thesmashy.medium.com/helpful-functions-for-your-powershell-profile-9fece679f4d6](https://thesmashy.medium.com/helpful-functions-for-your-powershell-profile-9fece679f4d6)
* [https://github.com/stevencohn/WindowsPowerShell](https://github.com/stevencohn/WindowsPowerShell)

## Create Github Repo

1. `mkdir C:\github\powershell-profile'
2. `git init`
3. code C:\github\powershell-profile\profile.ps1 && code C:\github\powershell-profile\readme.md

## Structure

I think this is a great way to keep organized, seperate each function by type, and then load each seperate type file.  Save in `$profile`

```powershell
$profileDir = $PSScriptRoot;

foreach ( $includeFile in ("azure", "defaults", "openssl", "development") ) {
    Unblock-File $profileDir\$includeFile.ps1
. "$profileDir\$includeFile.ps1"
}
```

## Add functions

Found this while searching around, this will save me a ton of time and keystrokes, I'll drop it in the development.ps1, as well as my New-BlogPost function I made a couple posts ago.

```powershell
function Invoke-GitAddCommit {
    <#
    .SYNOPSIS
        Shortcut for adding and committing files using git.
    .EXAMPLE
        Invoke-GitAddCommit "initial commit"
        gac "my commit" .\myFile.ps1
    #>
    [Alias("gac")]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]
        $Message,
        [Parameter(Position = 1)]
        [string]
        $File
    )
    if ($File) {
        git add $File
    }
    else {
        git add .
    }
    git commit -m $Message
}
```

## Copy to profile directory

Once profile.ps1 and all my other supporting .ps1 files are in place I can copy them to my profile directory using this command: `copy-item -Path C:\github\powershell-profile\* -D C:\Users\nickh\OneDrive\Documents\Powershell\ -Recurse`

## Conclusion

Now I just need to reload the profile and test the new function on this blogpost `gac "day 11"`.  If you are reading this, then it looked like it worked.  For Day 11 of 100 days of code, I created the structure of my PowerShell Profile and added a couple functions to it.  I put it in OneDrive so it should now sync to all my machines that are setup that way, but I can also pull a copy from GitHub if I need to.