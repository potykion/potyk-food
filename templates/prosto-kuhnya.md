# ПроСто кухня

| Выпуск | Блюдо 1 | Блюдо 2 | Блюдо 3 | Блюдо 4 | Блюдо 5 |
|--------|---------|---------|---------|---------|---------|
{% for episode in episodes %}
| [{{ episode.number }}]({{ episode.url }}) | {{ episode.dishes[0] if episode.dishes|length > 0 else '—' }} | {{ episode.dishes[1] if episode.dishes|length > 1 else '—' }} | {{ episode.dishes[2] if episode.dishes|length > 2 else '—' }} | {{ episode.dishes[3] if episode.dishes|length > 3 else '—' }} | {{ episode.dishes[4] if episode.dishes|length > 4 else '—' }} |
{% endfor %}
