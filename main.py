import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QComboBox, QListWidget, QListWidgetItem, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta

# Замените ваши значения CLIENT_ID и CLIENT_SECRET
CLIENT_ID = 'sjc2n354ipa9w21gnwf3aywzcz5oce'
CLIENT_SECRET = 'n32ew1nsqjfgyxl4ks3yav28gwdk2f'

# Словарь платформ
PLATFORM_NAMES = {
    6: 'PC',
    48: 'PlayStation 4',
    167: 'PlayStation 5',
    49: 'Xbox One',
    169: 'Xbox Series X/S',
    130: 'Nintendo Switch'
}


# Получаем токен доступа
def get_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']


# Функция для получения релизов игр
def fetch_game_releases(platform_id, access_token, days):
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    query = f'''
        fields name, first_release_date, platforms, cover.url;
        where platforms = {platform_id} & first_release_date >= {int(datetime.now().timestamp())} 
        & first_release_date <= {int((datetime.now() + timedelta(days=days)).timestamp())};
        sort first_release_date asc;
        limit 10;
    '''

    url = 'https://api.igdb.com/v4/games'
    response = requests.post(url, headers=headers, data=query)
    response.raise_for_status()

    return response.json()


# Основное окно приложения
class GameReleaseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Release Calendar")
        self.setGeometry(100, 100, 600, 400)

        # Layout
        self.layout = QVBoxLayout()

        # Выпадающий список для платформ
        self.platforms_combo = QComboBox(self)
        self.platforms_combo.addItems(PLATFORM_NAMES.values())
        self.platforms_combo.currentIndexChanged.connect(self.update_game_list)
        self.layout.addWidget(self.platforms_combo)

        # Список релизов игр
        self.games_list = QListWidget(self)
        self.games_list.itemClicked.connect(self.show_game_details)
        self.layout.addWidget(self.games_list)

        # Изображение постера и дата выхода
        self.h_layout = QHBoxLayout()  # Горизонтальный Layout для постера и даты выхода
        self.poster_label = QLabel(self)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.h_layout.addWidget(self.poster_label)

        # Дата выхода игры
        self.release_date_label = QLabel(self)
        self.release_date_label.setAlignment(Qt.AlignCenter)
        self.h_layout.addWidget(self.release_date_label)

        # Добавляем горизонтальный Layout
        self.layout.addLayout(self.h_layout)

        self.setLayout(self.layout)

        # Получаем токен доступа
        self.access_token = get_access_token()

        # Обновляем список игр для платформы по умолчанию
        self.update_game_list()

    def update_game_list(self):
        platform_name = self.platforms_combo.currentText()
        platform_id = list(PLATFORM_NAMES.keys())[list(PLATFORM_NAMES.values()).index(platform_name)]

        games = fetch_game_releases(platform_id, self.access_token, 30)
        self.games_list.clear()

        for game in games:
            item = QListWidgetItem(game['name'])
            item.setData(Qt.UserRole, game)
            self.games_list.addItem(item)

    def show_game_details(self, item):
        game = item.data(Qt.UserRole)

        # Отображаем постер игры, если он доступен
        if 'cover' in game and 'url' in game['cover']:
            cover_url = game['cover']['url'].replace("t_thumb", "t_cover_big")
            response = requests.get(f"https:{cover_url}")
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.poster_label.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatio))
        else:
            self.poster_label.setText("No cover available")  # Если постера нет

        # Отображаем дату выхода игры, если она доступна
        if 'first_release_date' in game:
            release_date = datetime.utcfromtimestamp(game['first_release_date']).strftime('%Y-%m-%d')
            self.release_date_label.setText(f"Release Date: {release_date}")
        else:
            self.release_date_label.setText("Release date not available")  # Если даты нет


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameReleaseApp()
    window.show()
    sys.exit(app.exec_())
