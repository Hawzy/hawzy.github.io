---
layout: single
title: "Projects"
permalink: /projects/
author_profile: false
surface: blog
classes:
  - wide
  - surface-blog
---

<p class="hz-projects-intro">Code and AI agent projects built in Google Antigravity to get recurring chores off my plate.</p>

<div class="hz-project-grid">
  {% assign active_posts = site.posts | where_exp: "p", "p.archived != true" %}
  {% for proj in site.data.projects %}
    {% assign card_href = "#" | append: proj.slug %}
    {% if proj.surface_url %}
      {% assign card_href = proj.surface_url | relative_url %}
    {% else %}
      {% for post in active_posts %}
        {% if post.projects contains proj.slug or post.project == proj.slug %}
          {% assign card_href = post.url | relative_url %}
          {% break %}
        {% endif %}
      {% endfor %}
    {% endif %}

    {% assign has_proj_posts = false %}
    {% for post in active_posts %}
      {% if post.projects contains proj.slug or post.project == proj.slug %}
        {% assign has_proj_posts = true %}
        {% break %}
      {% endif %}
    {% endfor %}

    <article id="{{ proj.slug }}" class="hz-project-card">
      <div class="hz-eyebrow">{{ proj.eyebrow }}</div>
      <h2 class="hz-project-card__title"><a href="{{ card_href }}">{{ proj.title }}</a></h2>
      <p class="hz-project-card__desc">{{ proj.description }}</p>

      {% if has_proj_posts %}
        <ul class="hz-project-card__posts" aria-label="Posts for {{ proj.title }}">
          {% for post in active_posts %}
            {% if post.projects contains proj.slug or post.project == proj.slug %}
              <li class="hz-project-card__post-item">
                <time datetime="{{ post.date | date_to_xmlschema }}" class="hz-project-card__post-date">{{ post.date | date: "%Y-%m-%d" }}</time>
                <a href="{{ post.url | relative_url }}" class="hz-project-card__post-link">{{ post.title }}</a>
              </li>
            {% endif %}
          {% endfor %}
        </ul>
      {% endif %}

      {% if proj.surface_url %}
        <p class="hz-project-card__meta">
          <a href="{{ proj.surface_url | relative_url }}" class="hz-project-card__surface-link">{{ proj.surface_label | default: proj.surface_url }} &rarr;</a>
        </p>
      {% elsif has_proj_posts == false %}
        <p class="hz-project-card__meta">Full build writeup coming soon.</p>
      {% endif %}
    </article>
  {% endfor %}
</div>
