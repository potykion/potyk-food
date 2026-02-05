# Пиво

<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 20px;">
{% for style in styles %}
{% for beer in style_beers[style.id] %}
    <a href="#{{ beer.id }}" style="display: inline-flex; align-items: flex-end; justify-content: center; width: 40px;"><img src="../{{ beer.img }}" alt="{{ beer.title }}" ></a>
{% endfor %}
{% endfor %}
</div>

{% for style in styles %}
## :{{ style.country_code }}: {{ style.title }}

<table>
<thead>
    <tr>
        <th>Банка/Бутылка</th>
        <th>Описание</th>
    </tr>
</thead>

<tbody>

{% for beer in style_beers[style.id] %}
    <tr id="{{ beer.id }}">
        <td style="text-align: center">
            <img src="../{{ beer.img }}" alt="{{ beer.title }}" width="40" >
        </td>
        <td>
            <a href="{{ beer.untappd_url }}"><b>{{ beer.brewery }} • {{ beer.title }}</b></a> <br> {{ beer.review }}
        </td>
    </tr>
{% endfor %}
</tbody>
</table>

{% endfor %}
