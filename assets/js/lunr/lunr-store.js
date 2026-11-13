---
layout: none
---

{%- assign searchable_docs = "" | split: "" -%}
{%- for c in site.collections -%}
  {%- assign filtered = c.docs | where_exp:'doc','doc.search != false' | where_exp:'doc','doc.archived != true' | where_exp:'doc','doc.status != "draft"' -%}
  {%- assign searchable_docs = searchable_docs | concat: filtered -%}
{%- endfor -%}
var store = [
  {%- for doc in searchable_docs -%}
    {%- if doc.header.teaser -%}
      {%- capture teaser -%}{{ doc.header.teaser }}{%- endcapture -%}
    {%- else -%}
      {%- assign teaser = site.teaser -%}
    {%- endif -%}
    {
      "title": {{ doc.title | jsonify }},
      "excerpt":
        {%- if site.search_full_content == true -%}
          {{ doc.content | newline_to_br |
            replace:"<br />", " " |
            replace:"</p>", " " |
            replace:"</h1>", " " |
            replace:"</h2>", " " |
            replace:"</h3>", " " |
            replace:"</h4>", " " |
            replace:"</h5>", " " |
            replace:"</h6>", " "|
          strip_html | strip_newlines | jsonify }},
        {%- else -%}
          {{ doc.content | newline_to_br |
            replace:"<br />", " " |
            replace:"</p>", " " |
            replace:"</h1>", " " |
            replace:"</h2>", " " |
            replace:"</h3>", " " |
            replace:"</h4>", " " |
            replace:"</h5>", " " |
            replace:"</h6>", " "|
          strip_html | strip_newlines | truncatewords: 50 | jsonify }},
        {%- endif -%}
      "categories": {{ doc.categories | jsonify }},
      "tags": {{ doc.tags | jsonify }},
      "url": {{ doc.url | relative_url | jsonify }},
      "teaser": {{ teaser | relative_url | jsonify }}
    }{%- unless forloop.last -%},{%- endunless -%}
  {%- endfor -%}]
