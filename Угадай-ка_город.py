import os
import sys

import requests
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

from function import show_obj

SCREEN_SIZE = [600, 450]
CITIES = [
    # Крупные города
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону",
]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.current_slide = 0
        self.getImage()
        self.initUI()

    def get_coords(self, toponym_to_find):
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
        spn = list(map(str, map(lambda i: float(i) / 100, spn)))
        apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join(coords),
            "spn": ",".join(spn),
            "apikey": apikey,
        }
        return map_params

    def getImage(self):
        map_request = CITIES[self.current_slide]
        map_api_server = "https://static-maps.yandex.ru/v1"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=self.get_coords(map_request))
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Слайд-шоу')
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event: QKeyEvent):
        if os.path.exists(self.map_file):
            os.remove(self.map_file)

        self.current_slide = (self.current_slide + 1) % len(CITIES)
        self.getImage()

        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)
        self.update()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())