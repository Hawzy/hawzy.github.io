---
title: New-Blogpost - Creating a basic PowerShell function
tags:
- 100DaysOfCode
- PowerShell
- GitHub
- Jekyll
comments: true
---

I wanted to make a quick powershell function to create a blogpost folder and file structure.  I'm planning to use jekyll to host this and the way jekyll works is that there is a `.\_posts\` folder that holds all your blog post files, and if there are any files in the posts directory they have to be pre-fixed with the date, so we need to name our blog files something like `2022-01-02-blogpost.md`.  

I'd rather have every blogpost be its own self-contained folder with the files or scripts and images related to that post also in that folder. To be able to actually use the pictures in a post I will need to make a copy of them in the `\Assets\` folder, but I dont mind doing that little extra work for the sake of organization

## New-Blogpost Function

So for now I want this function to create a folder in the current directory, formatted with a specific date, and then also create a starter blogpost file inside that folder and then open it in VS Code.

I think I'll use a later blogpost to expand the functionality, and pass a parameter to add future dates.

Let's create the PowerShell file using `code New-Blogpost.ps1`

```powershell
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
```

## Conclusion

After this function is stored in memory we can run `New-Blogpost` in powershell, it will then create a folder with the current date in the present working directory, and open a template of a blogpost in VS Code to start editing.

That wraps up day 2 for my 100 Days of Code.
