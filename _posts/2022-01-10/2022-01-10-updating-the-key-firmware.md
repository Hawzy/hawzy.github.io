---
title: Updating "The Key" firmware with custom configuration
tags:
- 100DaysOfCode
- Macropad
- StackOverflow
- "The Key"
- firmware
categories:
- Blog
comments: true
header:
  teaser: "/assets/images/teasers/the-key.png"
---

I picked up the [Stack Overflow "The Key](https://stackoverflow.blog/2021/03/31/the-key-copy-paste/) and it ships with pretty lame default settings (gimmick settings) ctrl key, c key and v key.  Since its a macropad we can do a lot with just 3 keys, but this config will be a pretty quick basic upgrade.

The QMK firmware is kind of weird, but here are a couple links to help explain it:

* [https://blog.splitkb.com/how-to-work-with-small-keyboards](https://blog.splitkb.com/how-to-work-with-small-keyboards).  
* [https://drop.com/talk/93641/how-to-configure-stack-overflow-the-key-macropad](https://drop.com/talk/93641/how-to-configure-stack-overflow-the-key-macropad).

First upload the template to [https://kbfirmware.com/](https://kbfirmware.com/), then map out your keys.  

There are 3 keys, for our purposes labeled 0,1,2 and we are starting on the base layer 0 and going up from there.

## Key legend

```yaml
Layer 0 - key 0: MO(Layer 1) [change to layer 1 while being pressed]
Layer 0 - key 1: Ctrl + C [copy]
Layer 0 - key 2: Ctrl + V [paste]

Layer 1 - key 0: Transparent [Not used, because you are holding down this key to get to this layer]
Layer 1 - key 2: Win + Shift + S [Screen Snip]
Layer 1 - key 2: Win + V [clipboard history]
```

## Flash Firmware

Once we are done mapping the keys in kbfirmware we download the hex file and use the QMK firmware utility to flash the macropad.  Then test and confirm it works.  

You can download the hex file from this post here and use it on your own macropad: [https://github.com/Hawzy/hawzy.github.io/blob/main/_posts/2022-01-10/hawzysdefaults.hex)(https://github.com/Hawzy/hawzy.github.io/blob/main/_posts/2022-01-10/hawzysdefaults.hex)]

## Conclusion

In this blog post I walk through a high level overview of how to customise the firmware on a very tiny keyboard.  That wraps up day 10 of 100, excited to have decimated this challenge, only 90% to go.