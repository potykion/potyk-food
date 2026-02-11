/**
 * Запускаем скрипт на https://script.google.com/
 *
 * В выводе получаем что-то такое:
 * 13:32:20	Информация	{"url":"https://youtu.be/sso0qRN-7Fs","title":"ПроСто кухня | Выпуск 223","description":"ПроСто кухня | Выпуск 223 (13.08.2022)\n\nБлюдо № 1 - Пожарские котлеты\nБлюдо № 2 - Турецкий пирог \"Су Бурек\"\nБлюдо № 3 - Зефир из черной смородины\nБлюдо № 4 - Мангал-салат","dishes":["Пожарские котлеты","Турецкий пирог \"Су Бурек\"","Зефир из черной смородины","Мангал-салат"]}
 * 13:32:20	Информация	{"url":"https://youtu.be/lqPjx-Uadsc","title":"ПроСто кухня | Выпуск 222","description":"ПроСто кухня | Выпуск 222 (06.08.2022)\n\nБлюдо № 1 - Поке-боул с битыми огурцами\nБлюдо № 2 - Буррито со скрэмблом\nБлюдо № 3 - Бисквитный рулет \"Рафаэлло\"\nБлюдо № 4 - Макароны с мясом на сковородке\nБлюдо № 5 - Раки по-лузиански","dishes":["Поке-боул с битыми огурцами","Буррито со скрэмблом","Бисквитный рулет \"Рафаэлло\"","Макароны с мясом на сковородке","Раки по-лузиански"]}
 *
 * Все копируем в json-файл, удаляем "13:32:20	Информация" + добавляем "," в конце каждой строки и "[]" в начале и конце файла
 *
 * Таким образом получаем json с выпусками - data/prosto-kuhnya.json
 *
 */

function main() {
  const videos = getPlaylistVideos("PLRQwloIf-xS-PWGAytv_U1HUJ6U8BvSiP");
  videos.forEach(v => console.log(JSON.stringify(v)));
}

/**
 * Из description вида "Блюдо № 1 - Пожарские котлеты\nБлюдо № 2 - ..." достаёт названия блюд.
 * @returns {string[]}
 */
function parseDishes(description) {
  if (!description) return [];
  const re = /Блюдо № \d+ - ([^\n]+)/g;
  const dishes = [];
  let m;
  while ((m = re.exec(description)) !== null) {
    dishes.push(m[1].trim());
  }
  return dishes;
}

function getPlaylistVideos(playlistId) {
  // [{url, title, description, dishes}]
  let videos = [];

  let pageToken = '';
  while(true){
    const resp = YouTube.PlaylistItems.list(
      'snippet',
      {
        playlistId,
        maxResults: 50,
        pageToken,
      },
    );
    videos = [
      ...videos,
      ...resp.items.map(i => ({
        url: `https://youtu.be/${i.snippet.resourceId.videoId}`,
        title: i.snippet.title,
        description: i.snippet.description,
        dishes: parseDishes(i.snippet.description),
      })),
    ];
    pageToken = resp.nextPageToken;
    if (!pageToken) {
      break;
    }
  }

  return videos;
}


