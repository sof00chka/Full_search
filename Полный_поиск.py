import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image

from function import show_obj

# Пусть наше приложение предполагает запуск:
#  python Полный_поиск.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
coords, spn = show_obj(toponym)

delta = "0.005"
apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    "ll": ",".join(coords),
    "spn": ",".join(spn),
    "apikey": apikey,
    "pt": f"{coords[0]},{coords[1]},pm2rdm"

}

map_api_server = "https://static-maps.yandex.ru/v1"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
im = BytesIO(response.content)
opened_image = Image.open(im)
opened_image.show()  # Создадим картинку и тут же ее покажем встроенным просмотрщиком операционной системы