---
title: Site Setup and Jekyll theme configuration
tags:
- 100DaysOfCode
- Jekyll
- GitHub
- Docker Compose
categories:
- Blog
comments: true
---
Welcome to day 5 of my 100 days of code journey.  Last time, I cloned a jekyll theme, spun up a docker container to serve the files and did some light cleanup of leftover files. Today I'm going to tweak the config to get setup finalized.  Some helpful links from the docs to get started:

* [Official quick-start guide](https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/#setup-your-site)
* [Structure Page](https://mmistakes.github.io/minimal-mistakes/docs/structure/) - a list of theme files and what they do
* [Configuration documentation page](https://mmistakes.github.io/minimal-mistakes/docs/configuration/)

## Docker Compose and Jekyll

Pull down the branch we want to use `git clone https://github.com/mmistakes/minimal-mistakes C:/github/hawzy.github.io`

Launch our webserver using `docker-compose up -d` and browse to `http://localhost:4000/`

## _config.yml

Most of the fun stuff happens here, I edited these lines in the_config.yml, dark theme is mandatory of course.

New content like posts will automatically refresh and display in your web browser, but anytime we update the config file we also need to restart the jekyll service so we run a `docker-compose restart` for those changes to take effect.

* **minimal_mistakes_skin**    : "dark" # "air", "aqua", "contrast", "dark", "dirt", "neon", "mint", "plum", "sunrise"
* title and subtitle
* name
* description
* url
* repository
* logo
* Site Author section
* Twitter username
* Github username
* Author Section
* Footer Secction

also adding some defaults to every page so I dont have to call these out manually in the frontmatter of those pages.  This does things like enable table of contents, enable comments, permalink: sets the formatting for URLs, that means this post URL will be something like hawzy.github.io/2022/site-setup-and-jekyll-theme-config.


```yaml
# Defaults
defaults:
  # _posts
  - scope:
      path: ""
      type: posts
    values:
      layout: single
      author_profile: true
      read_time: true
      comments: true
      share: true
      related: true
      toc: true
      toc_sticky: true
  # _pages
  - scope:
      path: "_pages"
      type: pages
    values:
      layout: single
      author_profile: true
permalink: /:categories/:year/:title:output_ext
```

Here is the link to my full config file if you want to take a look: https://raw.githubusercontent.com/Hawzy/hawzy.github.io/main/_config.yml

## Conclusion

On Day 5 of 100 Days of Code,I cloned a jekyll theme repo, I tweaked the settings and added dark mode (very important), and added my About Me page info.  On Day 6 I will push my local files up to GitHub and make https://hawzy.github.io viewable on the internet.
