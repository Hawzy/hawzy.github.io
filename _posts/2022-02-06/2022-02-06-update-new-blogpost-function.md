---
title: Upgrade function to include alias and second parameter
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

For day 14 of 100 Days of Code I'm going to update my new-blogpost function again, by adding an alias and a second parameter.

## New-Blogpost

```powershell
function New-Blogpost {
    <#
    .SYNOPSIS
        Shortcut for creating new folder and file in the jekyll date format
    .EXAMPLE
        New-BlogPost "how-to-create-a-blog" -AddDays 1
        nbp "new-blog-post"
    #>
    [Alias("nbp")]
    param(
        [Parameter(Mandatory=$false,Position = 0)] 
        [string]
        $Title = "new-blogpost",
        [int]$AddDays = 0)
        
    $date = (get-date).AddDays($AddDays).ToString('yyyy-MM-dd')
    
    New-Item -ItemType directory -Path ".\$date"

    Copy-Item -Path  "$profileDir\blog_template.md" -Destination ".\$date\$date-$title.md"
              
    code ".\$date\$date-$title.md"
    }
```
So a couple new updates are happening here: 

1. I've added the `[Alias("nbp")]` block to the start of the script, that lets me call it by typing nbp instead of new-blogpost.
2. I've added the `-Title` parameter, which is not Mandatory so if no title is chosen it defaults to `$date-new-blogpost.md`
3. The `-Title` parameter is also positional, which means when running the script it will accept any string of text as the `$title` value, without having to explicitly call `-Title`
4. Script now creates a copy of a markdown folder that lives in my `$profileDir` to use as a template base for all new blogposts.  In my template I've included a useful link for markdown stuff because I'm forgetful.

## Conclusion

For day 14 of 100 days of code, I've upgraded my custom function for the 2nd time, and added it to my powershell-profile startup script so that it is availble to run in my sessions.  I can now kick off a new blog post by navigating to my _posts directory and typing `nbp "update-new-blogpost-function"` and it will create a folder and starting .md file to my specifications.