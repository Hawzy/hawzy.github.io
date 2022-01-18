---
title: Install Oh My Posh Theme Engine
tags:
 - 100DaysOfCode
 - PowerShell
 - "Windows Terminal"
 - "PowerShell Profile"
categories:
- Blog
comments: true
header:
  teaser: "/assets/images/teasers/powershell-prompt.png"
---

Today for Day 12 of 100 Days of Code I'm going to install the Oh My Posh Prompt theme engine, Nerd Fonts and Terminal Icons into my powershell profile.

Scott Hanselman has a great post covering this in depth:
* [https://www.hanselman.com/blog/my-ultimate-powershell-prompt-with-oh-my-posh-and-the-windows-terminal](https://www.hanselman.com/blog/my-ultimate-powershell-prompt-with-oh-my-posh-and-the-windows-terminal)

## Install Nerd Font

Head over to [https://www.nerdfonts.com/font-downloads](https://www.nerdfonts.com/font-downloads) and choose your font, Nerd Fonts contain cool icons for different folders and file types, I'm using Caskaydia Cove Nerd Font.  Download and extract the contents of the .zip file, then highlight the font files, right-click *Install*.  Once installed, open Windows Terminal Settings `Ctrl + ,`, goto Powershell > Appearance and change the font face to your chosen Nerd Font.

## Download Oh My Posh Themes
Find a theme you like from the Oh My Posh website, you can customize your own theme if you want.

* [https://ohmyposh.dev/docs/themes](https://ohmyposh.dev/docs/themes)

Each theme links to a .json file on github, download that file to your local theme repository, my directory `C:\Users\nickh\.oh-my-posh\themes`

Run the command `code $profile` and enter this line which points to your chosen config: `oh-my-posh --init --shell pwsh --config C:\Users\nickh\.oh-my-posh\themes\night-owl.omp.json | Invoke-Expression`
## Install Terminal Icons and Oh My Posh

First time you will need to install the modules
```powershell
Install-Module -Name Terminal-Icons -force
Install-Module -Name oh-my-posh -scope CurrentUser -force
```

then I add these lines to my `profile.ps1`, but you can put them in $profile also.
```powershell
Import-Module -Name Terminal-Icons
Import-Module -Name oh-my-posh
```

## Conclusion

For Day 12 of 100 Days of code, I've massively upgraded the look of my terminal.  Here is a preview of what it looks like now:
![Powershell Profile](/assets/posts/powershell-prompt.png)