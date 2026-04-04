import sys
from io import BytesIO

import requests
from PIL import Image

from function import show_obj, calculate_distance, get_pharmacy_color

# Пусть наше приложение предполагает запуск:
# python 10_аптек.py Москва, ул. Ак. Королева, 12
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

search_params = {
    "apikey": apikey2,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": f"{coords[0]},{coords[1]}",
    "type": "biz",
    "results": 10
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print("Ошибка поиска")
    sys.exit(1)

json_response = response.json()

if not json_response["features"]:
    print("Аптеки не найдены")
    sys.exit(1)

pharmacies = json_response["features"]
print(f"\nНайдено аптек: {len(pharmacies)}")

pt_points = [f"{coords[0]},{coords[1]},pm2rdm"]

pharmacies_info = []
for i, pharmacy in enumerate(pharmacies, 1):
    org_name = pharmacy["properties"]["CompanyMetaData"]["name"]
    org_address = pharmacy["properties"]["CompanyMetaData"]["address"]
    point = pharmacy["geometry"]["coordinates"]
    try:
        work_time = pharmacy["properties"]["CompanyMetaData"]["Hours"]["text"]
    except (KeyError, TypeError):
        work_time = None
    color = get_pharmacy_color(work_time)
    color_name = {
        "gn": "зелёный (круглосуточно)",
        "bl": "синий (некруглосуточно)",
        "gr": "серый (нет данных)"
    }[color]
    pt_points.append(f"{point[0]},{point[1]},pm2{color}m")
    lon_obj = float(coords[0])
    lat_obj = float(coords[1])
    distance_km = calculate_distance(lon_obj, lat_obj, point[0], point[1])
    distance_m = distance_km * 1000
    if distance_km < 1:
        distance_str = f"{distance_m:.0f} м"
    else:
        distance_str = f"{distance_km:.2f} км"
    pharmacies_info.append({
        "name": org_name,
        "address": org_address,
        "work_time": work_time if work_time else "Нет данных",
        "distance": distance_str,
        "color": color_name
    })

    print(f"\n{i}. 📍 {org_name}")
    print(f"   📮 Адрес: {org_address}")
    print(f"   🕒 Часы работы: {work_time if work_time else 'Нет данных'}")
    print(f"   📏 Расстояние: {distance_str}")
    print(f"   🎨 Цвет точки: {color_name}")

map_params = {
    "apikey": apikey1,
    "pt": "~".join(pt_points),
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

print("\n" + "=" * 70)
print("                     АПТЕКИ РЯДОМ")
print("=" * 70)
print(f"📍 Исходный адрес: {toponym_to_find}")
print(f"📊 Всего найдено аптек: {len(pharmacies_info)}")
print(f"   🟢 Круглосуточные: {sum(1 for p in pharmacies_info if 'круглосуточно' in p['color'])}")
print(f"   🔵 Некруглосуточные: {sum(1 for p in pharmacies_info if 'некруглосуточно' in p['color'])}")
print(f"   ⚪ С отсутствием данных: {sum(1 for p in pharmacies_info if 'нет данных' in p['color'])}")
print("=" * 70)