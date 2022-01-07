---
title: Docker Compose and Jekyll
tags:
- 100DaysOfCode
- Powershell
- Github
- Jekyll
- Docker
- "2022"
categories:
- Blog
comments: true
---

Now that I've got some material, I want to setup a Jekyll container to display my content locally and tweak the theme and settings before I fire it off into github.  I'm going to use docker-compose.

## Prerequisites

For this project I'm running Windows 10 with these programs installed:

* Docker
* WSL2
* Github desktop

## Clone Jekyll Theme - Minimal mistakes

We are going to clone the [Minimal Mistakes Theme](https://github.com/mmistakes/minimal-mistakes) repo to use as our theme, I have github desktop installed but they buried git.exe so its not reachable by default and we need to add it to path.  First I'm going to install the [Pscx - PowerShell Community Extensions](https://github.com/Pscx/Pscx) which has a cmdlet called `Add-PathVariable` and a bunch of other cool stuff.  Once that is added to path I can run git.

```powershell
Install-Module Pscx -Scope CurrentUser -AllowClobber -Force

Add-PathVariable "${env:LOCALAPPDATA}\GitHubDesktop\app-2.9.6\resources\app\git\cmd\"

git clone https://github.com/mmistakes/minimal-mistakes.git C:/github/hawzy.github.io
```

## Docker-compose

Next we will create a docker compose configuration file, that defines the image to download, commands to run and linked folders between the host and the container called volumes.

Navigate to the Jekyll directory (C:/github/hawzy.github.io in my case) and create the configuration file.
`code docker-compose.yml`

```yaml
version: '3'

services:
  jekyll:
    image: jekyll/jekyll:latest
    command: jekyll serve --watch --force_polling --verbose
    ports:
      - 4000:4000
    volumes:
      - .:/srv/jekyll
```

Next we will spin up the Jekyll docker container as a background service, not sure what -d stands for, daemon or detached?

```docker
docker-compose up -d
```

Find the docker image name and list which containers are running with `docker-compose ps` we can enter the bash terminal on our container and execute commands with this command:

```docker
docker exec -it tmp_jekyll_1 bash
```

## Jekyll Theme clean-up

Per the documentation [Minimal Mistakes Quick-Start Guide](https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/#gem-based-method) we need to remove /docs and /test and I'm going to delete some other stuff that I dont think I'll need, and add a posts folder to put my posts into.

```powershell
$Delete = @('.editorconfig','.gitattributes','CHANGELOG.md', 'README.md', 'screenshot-layouts.png', 'screenshot.png', 'test', 'docs')

$Delete | Foreach {remove-item $_}

New-Item -ItemType directory -Path ".\_posts"
```

## Conclusion

Once I move my posts over to the .\_posts folder I can navigate to [http://localhost:4000](http://localhost:4000) and see my blog post content formatted with the Jekyll theme I've chosen.  That wraps up day 4 of 100 days of code.  Next up I'll be tweaking the default settings to customize the Jekyll theme.
