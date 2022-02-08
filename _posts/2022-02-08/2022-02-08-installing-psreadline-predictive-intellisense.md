---
title: Installing PSReadLine for Predictive Intellisense 
tags:
 - 100DaysOfCode
 - PowerShell
 - "PowerShell Profile"
 - PSReadLine
categories:
- Blog
comments: true
header:
  teaser: "/assets/images/teasers/powershell-prompt.png"
---
You can read all about PSReadLine here: [About PSReadLine](https://docs.microsoft.com/en-us/powershell/module/psreadline/about/about_psreadline), the feature I want most is the predictive intellisense, you set your PowerShell command history as the source so that you can prioritize commands you use frequently.

I'm using PowerShell 7.2 from the Windows Store.

## Install

```code PowerShell
Install-Module -Name PSReadLine -AllowPrerelease -Force
Set-PSReadLineOption -PredictionSource History
```
For the functionality i wanted, these 2 lines was all it took

![PSReadLine](/assets/posts/psreadline.png)

I will also need to add `Set-PSReadLineOption -PredictionSource History` to my profile.ps1, so that it runs every time i start PowerShell

## Conclusion

For Day 16 I enabled PSReadLine, honestly not sure why it took me so long.  Should be pretty useful.