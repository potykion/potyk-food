# Вино

{% for style in styles %}
## :{{ style.country_code }}: [{{ style.title }}]({{ style.vivino_url }})

<table>
<thead>
    <tr>
        <th>Бутылка</th>
        <th>Описание</th>
    </tr>
</thead>

<tbody>

{% for wine in style_wines[style.id] %}
    <tr>
        <td style="text-align: center">
            <img src="../{{ wine.img }}" alt="{{ wine.title }}" width="40" >
        </td>
        <td>
            <a href="{{ wine.vivino_url }}"><b>{{ wine.producer }} • {{ wine.title }}</b></a> <br> {{ wine.review }}
        </td>
    </tr>
{% endfor %}
</tbody>
</table>

{% endfor %}
