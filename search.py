import sys
from io import BytesIO

import requests
from PIL import Image

from function import show_obj, calculate_distance

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
apikey1 = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
search_api_server = "https://search-maps.yandex.ru/v1/"
apikey2 = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

geocoder_params = {
    "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
    "geocode": toponym_to_find,
    "format": "json"
}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    print("Ошибка геокодера")
    sys.exit(1)

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
coords, spn = show_obj(toponym)

# Поиск аптеки
search_params = {
    "apikey": apikey2,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": f"{coords[0]},{coords[1]}",
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print("Ошибка поиска")
    sys.exit(1)

json_response = response.json()

if not json_response["features"]:
    print("Аптеки не найдены")
    sys.exit(1)

organization = json_response["features"][0]
org_name = organization["properties"]["CompanyMetaData"]["name"]
org_address = organization["properties"]["CompanyMetaData"]["address"]
point = organization["geometry"]["coordinates"]  # [долгота, широта]
org_point = f"{point[0]},{point[1]}"

lon_obj = float(coords[0])
lat_obj = float(coords[1])

lon_org = float(point[0])
lat_org = float(point[1])

distance_km = calculate_distance(lon_obj, lat_obj, lon_org, lat_org)
distance_m = distance_km * 1000

if distance_km < 1:
    distance_str = f"{distance_m:.0f} м"
else:
    distance_str = f"{distance_km:.2f} км"

try:
    work_time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
except (KeyError, TypeError):
    work_time = "Информация о времени работы отсутствует"

print("\n" + "=" * 60)
print("                     БЛИЖАЙШАЯ АПТЕКА")
print("=" * 60)
print(f"  📍 Название: {org_name}")
print(f"  📮 Адрес: {org_address}")
print(f"  🕒 Часы работы: {work_time}")
print(f"  📏 Расстояние: {distance_str} от точки")
print(f"     \"{toponym_to_find}\"")
print("=" * 60 + "\n")

map_params = {
    "apikey": apikey1,
    "pt": f"{coords[0]},{coords[1]},pm2rdm~{org_point},pm2blm",
    "size": "600,400"
}

map_api_server = "https://static-maps.yandex.ru/v1"
response = requests.get(map_api_server, params=map_params)

if not response:
    print("Ошибка получения карты")
    sys.exit(1)

im = BytesIO(response.content)
opened_image = Image.open(im)
opened_image.show()