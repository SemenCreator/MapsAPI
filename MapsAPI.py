import sys

import requests

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt

from interface_MapsAPI import Ui_MainWindow


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.search.clicked.connect(self.search_address)
        self.reset.clicked.connect(self.reset_request)
        self.plus_postal_code.clicked.connect(self.change_plus_postal_code)
        self.type_maps = [self.type_1, self.type_2, self.type_3]
        self.type_1.clicked.connect(self.define_type_map)
        self.type_2.clicked.connect(self.define_type_map)
        self.type_3.clicked.connect(self.define_type_map)
        self.output_full_address.setReadOnly(True)
        self.apikey = '40d1649f-0493-4b70-98ba-98533de7710b'
        self.server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        self.counter_map = 0
        self.type_map = 'Схема'
        self.reset_request()

    def define_type_map(self):
        sender = self.sender()
        for button in self.type_maps:
            if button == sender:
                self.type_map = button.text()
        self.check_place()

    def change_plus_postal_code(self):
        self.output_full_address.setText(self.find_coordinates())

    def change_type_maps(self):
        self.check_place()

    def find_coordinates(self):
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.place,
            "format": "json"}
        response = requests.get(
            self.server_address, params=geocoder_params)

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        self.toponym_longitude = float(toponym_coodrinates.split(" ")[0])
        self.toponym_lattitude = float(toponym_coodrinates.split(" ")[1])
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        if self.plus_postal_code.isChecked():
            try:
                postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                toponym_address += f', Почтовый индекс - {postal_code}'
            except KeyError:
                toponym_address += ', введите более точный адрес или индекс вовсе отсутствует'

        return toponym_address

    def change_coordinates(self, longi, latti):
        self.toponym_longitude -= longi
        self.toponym_lattitude -= latti

    def check_place(self):
        if self.type_map == 'Схема':
            map = 'map'
        elif self.type_map == 'Спутник':
            map = 'sat'
        else:
            map = 'skl'
        map_params = {
            "pt": self.marks[-1],
            'll': ",".join([str(self.toponym_longitude), str(self.toponym_lattitude)]),
            "spn": ",".join([str(self.scale), str(self.scale)]),
            "l": f"{map}"
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        self.response = requests.get(map_api_server, params=map_params)
        self.map_file = "map.png"
        if self.response:
            if self.counter_map > 0:
                with open(self.map_file, "wb") as f:
                    f.write(self.response.content)
                self.pixmap = QPixmap(self.map_file)
                self.image.setPixmap(self.pixmap)
            else:
                self.new_image()

    def new_image(self):
        with open(self.map_file, "wb") as f:
            f.write(self.response.content)

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(50, 50)
        self.image.resize(570, 250)
        self.image.setPixmap(self.pixmap)
        self.counter_map += 1

    def search_address(self):
        right_address = False
        try:
            self.scale = float(self.map_scale.text())
            if 0 < self.scale < 1:
                right_address = True
        except ValueError:
            pass
        if not self.place_address.text() == '':
            right_address = True
            self.place = self.place_address.text()
        if right_address:
            self.output_full_address.setText(self.find_coordinates())
            self.marks.append(
                ",".join([str(self.toponym_longitude), str(self.toponym_lattitude), 'pm2rdm']))
            self.check_place()

    def reset_request(self):
        self.place_address.setText('')
        self.map_scale.setText('')
        self.plus_postal_code.setChecked(False)
        self.group.setExclusive(False)
        self.type_1.setChecked(False)
        self.type_2.setChecked(False)
        self.type_3.setChecked(False)
        self.group.setExclusive(True)
        self.toponym_longitude = 37.617779
        self.toponym_lattitude = 55.755246
        self.scale = 0.05
        self.place = 'Москва'
        self.marks = ['37.622513,55.75322,pm2rdm']
        self.type_map = 'Схема'
        self.output_full_address.setText(self.find_coordinates())
        self.check_place()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.scale += 0.002
            self.check_place()
        if event.key() == Qt.Key_PageDown:
            self.scale -= 0.002
            self.check_place()
        if event.key() == Qt.Key_Down:
            self.change_coordinates(0, self.scale)
            self.check_place()
        if event.key() == Qt.Key_Up:
            self.change_coordinates(0, -self.scale)
            self.check_place()
        if event.key() == Qt.Key_Right:
            self.change_coordinates(-self.scale, 0)
            self.check_place()
        if event.key() == Qt.Key_Left:
            self.change_coordinates(self.scale, 0)
            self.check_place()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
