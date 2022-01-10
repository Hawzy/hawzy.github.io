---
title: Add show_date to Minimal Mistakes Theme
tags:
- 100DaysOfCode
- Jekyll
- "2022"
categories:
- Blog
comments: true
---

Out of the box Minimal Mistakes theme does not show the date on posts, just the read time.  I want to add that functionality to my blog and luckily I found someone else that already did the hard work.

[https://github.com/iBug/iBug-source/commit/de736bda](https://github.com/iBug/iBug-source/commit/de736bda)

whats happening here is we are editing the `page__hero.html`, to look for the inclusion of `show_date: true` in the front matter.  If it finds that it displays the date.  And then we also edit the `config.yml` to include `show_date: true` on all posts.

Here is an example of what it looks like when its all done:

![show date](/assets/posts/show_date.png)