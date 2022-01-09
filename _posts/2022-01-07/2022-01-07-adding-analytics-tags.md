---
title: Adding Analytics Tags to a Jekyll Blog
tags:
- 100DaysOfCode
- Jekyll
- "Google Analytics"
- "2022"
- "Bing Webmaster Tools"
categories:
- Blog
comments: true
---
Hi, welcome to day 7/100 days of code.  Today I'm going to walk through adding Google Analytics and Bing Webmaster Tools Analytics to this blog.  As always you can view the raw contents of this blog here: https://github.com/hawzy/hawzy.github.io 

## Sign Up
First go to the respective websites and create an account and find the tag section
  * https://analytics.google.com/
    * ![google analytics tag](/assets/posts/analytics_google.png)
  * https://www.bing.com/webmasters/
    * ![bing analytics tag](/assets/posts/analytics_clarity.png)

each site will give you a script tag to embed into the `<Head>` section of the website.

## Modify Theme
I'm using the minimal mistakes theme, but other Jekyll themes should be similar.  Minimal Mistakes does support some analytics tags in the config.yml file, but Bing isn't one of them so I'm going to setup both tags in the custom.html file manually.  Start by modifying `C:\github\hawzy.github.io\_includes\analytics-providers\custom.html` and add the tag scripts.

```html
<!-- start custom analytics snippet -->
<!-- Clarity tracking code for https://hawzy.github.io -->
<script>
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "a2fwrdncga");
</script>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-S4CZ8DD6EQ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-S4CZ8DD6EQ');
</script>
<!-- end custom analytics snippet -->
```

Then we include the analytics-providres\custom.html in the headers tag by including it in the following file: `C:\github\hawzy.github.io\_layouts\default.html`

![Update Head Tags](/assets/posts/head_update.png)

And thats it, git add, git commit and git push.

## Conclusion
We've added the tracking tags and pushed the code to our website.  Once this is live on the website, analytics data should start rolling in.  You can confirm its working by going to any page and right-click > `view source` and inspect the `<Head>` tags manually.