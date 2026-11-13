---
layout: single
title: "Kitchen & Weekly Menu"
permalink: /recipes/
author_profile: false
surface: kitchen
classes:
  - wide
  - kitchen-home
  - kitchen-recipes
---

<section class="weekly-menu-container" aria-labelledby="weekly-menu-heading">
  <div class="weekly-menu-header">
    <div>
      <span class="weekly-menu-eyebrow">Automated Kitchen &amp; Grocery Fulfillment</span>
      <h2 id="weekly-menu-heading" class="weekly-menu-title">Active Weekly Dinner Plan</h2>
    </div>
    <div class="weekly-menu-badges">
      <span class="weekly-menu-week-pill">Week of {{ site.data.weekly_menu.week_of }}</span>
      <a href="{{ '/api/weekly-menu.json' | relative_url }}" class="weekly-menu-api-pill" title="Machine-readable B2A Weekly Menu JSON">JSON API &nearr;</a>
    </div>
  </div>
  <p class="weekly-menu-lead">Our active family dinner rotation, structured for prep efficiency and one-command grocery cart consolidation.</p>

  <div class="weekly-meals-grid">
    {% for meal in site.data.weekly_menu.meals %}
      {% assign matched_recipe = site.recipes | where: "slug", meal.recipe_slug | first %}
      {% if matched_recipe and matched_recipe.status == 'draft' %}
        {% continue %}
      {% endif %}
      <article class="weekly-meal-card">
        <div>
          <div class="weekly-meal-card__day">{{ meal.day }}</div>
          <h3 class="weekly-meal-card__title">
            {% if matched_recipe %}
              <a href="{{ matched_recipe.url | relative_url }}">{{ matched_recipe.title }}</a>
            {% else %}
              {{ meal.recipe_slug }}
            {% endif %}
          </h3>
          <div class="weekly-meal-card__meta">
            <span class="weekly-meal-scale-badge">{{ meal.scale_factor }}x scale</span>
            {% if matched_recipe %}
              <span class="weekly-meal-time">{{ matched_recipe.prep_minutes | plus: matched_recipe.cook_minutes }} mins</span>
              <span class="recipe-status-dot recipe-status-dot--{{ matched_recipe.status | default: 'untested' }}" title="{% if matched_recipe.status == 'tested' %}Kitchen-tested{% else %}Untested draft{% endif %}">{% if matched_recipe.status == 'tested' %}&#10003; Tested{% else %}&#9679; Untested{% endif %}</span>
            {% endif %}
          </div>
        </div>
        {% if meal.notes %}
          <p class="weekly-meal-card__notes">&ldquo;{{ meal.notes }}&rdquo;</p>
        {% endif %}
      </article>
    {% endfor %}
  </div>
</section>

<section class="recipes-catalog-container" aria-labelledby="kitchen-catalog-heading">
  <div class="kitchen-section-bar">
    <h2 id="kitchen-catalog-heading" class="kitchen-section-title">From the Recipe Box</h2>
  </div>
  <p class="kitchen-catalog-intro">Tested weeknight staples and weekend projects with inline step measurements, interactive scaling, and <em>Cooking for Engineers</em> dependency grids.</p>
  {% include recipe-catalog-grid.html %}
</section>
