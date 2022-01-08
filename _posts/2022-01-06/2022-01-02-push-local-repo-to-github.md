---
title: Push local repository to GitHub using Git
tags:
- 100DaysOfCode
- Git
- GitHub
- "2022"
categories:
- Blog
comments: true
---
Welcome to day 6/100 days of code, today I'm going to push my local repo up to GitHub using Git on the Command Line.

I tried using the git that came with Github desktop, but it wasn't really installed correctly so I went and grabbed git for Windows  https://git-scm.com/download/win And set it up to be usable with Windows Terminal, after install I can open git in its own tab in Windows Terminal.

## Clone repo

We initially cloned our repo with this command `git clone https://github.com/mmistakes/minimal-mistakes.git C:/github/hawzy.github.io` and then made our configuration changes and added a couple posts.

The primary branch is called master, this can be changed to main using this command `git branch -m master main` the -m moves master and renames to main.

run `git init` this initializes the project folder and makes git track it. Then check the status of the project using `git status` I see a bunch of deleted/modified items compared to the original minimal mistakes repository

![git status](/assets/posts/git_status.png)

Next we will add our directory to git using `git add .` the . denotes the present working directory which is `C:\github\hawzy.github.io` 

Once we are sure that all these changes are good we need to commit them using the command

`git commit -m "initial commit"` -m is a message, put a short note to describe what you are changing, if you run a `git status` again at this point you will notice the deleted items change from red to green.

Since we cloned our repository we can check where its remote repository is using the command `git remote -v` which is still pointing at the minimal mistakes repository, which we can fix by running `git remote remove origin`

![git remote](/assets/posts/git_remote.png)

Next we will add our remote repository (on GitHub) this links the local repository to the remote destination  `git remote add origin https://github.com/Hawzy/hawzy.github.io.git`

and finally once everything is in place we push it up to GitHub using the command `git push`

Now anytime I update the folder `C:/github/hawzy.github.io` I can run the following commands to push to my GitHub repo.

1. `git add .` 
2. `git commit -m "message"`
3. `git push`

## Conclusion

For day 6 of 100 days of code, I used git from the command line to push my local blog repository to GitHub, and now have repeatable steps to do so again in the future.  And here is what it looks like:

![git push](/assets/posts/git_push.png)
