import requests
import sqlite3
from datetime import datetime, timedelta, timezone

try:
    # Замените эти значения на свои
    CLIENT_ID = 'sjc2n354ipa9w21gnwf3aywzcz5oce'
    CLIENT_SECRET = 'n32ew1nsqjfgyxl4ks3yav28gwdk2f'


    # Функция для получения токена доступа
    def get_access_token():
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }

        response = requests.post(url, params=params)
        response.raise_for_status()
        access_token = response.json()['access_token']
        return access_token


    # Функция для получения релизов игр через IGDB API
    def fetch_game_releases(platform_id, access_token, days):
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

        query = f'''
            fields name, first_release_date, platforms;
            where platforms = {platform_id} & first_release_date >= {int(datetime.now().timestamp())} 
            & first_release_date <= {int((datetime.now() + timedelta(days=days)).timestamp())};
            sort first_release_date asc;
            limit 10;
        '''

        url = 'https://api.igdb.com/v4/games'
        response = requests.post(url, headers=headers, data=query)
        response.raise_for_status()

        games = response.json()
        return games


    # Функция для создания базы данных и таблицы
    def create_db():
        conn = sqlite3.connect('game_releases.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                platform TEXT,
                release_date TEXT
            )
        ''')
        conn.commit()
        conn.close()


    # Функция для добавления игр в базу данных
    def add_games_to_db(games):
        conn = sqlite3.connect('game_releases.db')
        cursor = conn.cursor()

        for game in games:
            release_date = datetime.fromtimestamp(game['first_release_date'], timezone.utc).strftime('%Y-%m-%d')
            platform = "PC"  # Здесь можно добавить логику для правильного определения платформы

            cursor.execute('''
                INSERT INTO games (title, platform, release_date)
                VALUES (?, ?, ?)
            ''', (game['name'], platform, release_date))

        conn.commit()
        conn.close()


    # Функция для отображения ближайших релизов из базы данных
    def show_upcoming_releases(days):
        conn = sqlite3.connect('game_releases.db')
        cursor = conn.cursor()

        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT title, platform, release_date
            FROM games
            WHERE release_date <= ?
            ORDER BY release_date ASC
        ''', (end_date,))

        rows = cursor.fetchall()
        conn.close()

        print(f"Upcoming Releases for the next {days} days:")
        for row in rows:
            print(f"Title: {row[0]}, Platform: {row[1]}, Release Date: {row[2]}")


    # Пример использования
    if __name__ == "__main__":
        # Создаем базу данных и таблицу
        create_db()

        # Получаем токен доступа
        access_token = get_access_token()

        # ID платформ (например, для PC это 6)
        platform_id = 6

        # Получаем релизы для ближайших 30 дней
        upcoming_games = fetch_game_releases(platform_id, access_token, 30)

        # Добавляем релизы в базу данных
        add_games_to_db(upcoming_games)

        # Выводим ближайшие релизы из базы данных
        show_upcoming_releases(30)
    print("Program completed successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    input("Press Enter to exit...")


