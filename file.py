import requests

KP_TOKEN = 'ZK1559Z-4F54HDE-HVHK0RB-QJP47FE'


def get_film_info(data):
    msg = ''
    genres = []
    if 'genres' in data:
        for i in data['genres']:
            genres.append(i['name'])

    msg += f'Название: {data["name"]}\n'
    if 'status' in data:
        k = ''
        if data["status"] == 'announced':
            k = 'аннонсирован'
        elif data["status"] == 'completed':
            k = 'завершён'
        elif data["status"] == 'filming':
            k = 'снимается'
        elif data["status"] == 'post-production':
            k = 'пост-продакшн'
        elif data["status"] == 'pre-production':
            k = 'пре-продакшн'
        msg += f'Статус: {k} \n'
    if 'year' in data:
        msg += f'Год выпуска: {data["year"]}\n'
    if 'genres' in data:
        s = 'Жанр: '
        for i in genres:
            s += i + ', '
        msg += s[:-2] + '\n'
    if 'countries' in data:
        msg += f'Страна: {data["countries"][0]["name"]}' + '\n'
    if 'rating' in data:
        if 'kp' in data["rating"]:
            if data["rating"]["kp"] != 0:
                msg += f'Рейтинг на кп: {data["rating"]["kp"]}' + '\n'
        if 'imdb' in data["rating"]:
            if data["rating"]["imdb"] != 0:
                msg += f'Рейтинг imdb: {data["rating"]["imdb"]}' + '\n'
    if 'shortDescription' in data and data["shortDescription"]:
        msg += f'Описание: {data["shortDescription"]}' + '\n'

    return msg


def random_film():
    url = 'https://api.kinopoisk.dev/v1.4/movie/random'

    try:
        response = requests.get(url, headers={'X-API-KEY': KP_TOKEN}, params={
            'notNullFields': ['name', 'status', 'year', 'countries.name', 'genres.name', 'rating.kp', 'rating.imdb',
                              'shortDescription', 'poster.url']})

        if response.status_code == 200:
            data = response.json()
            msg = get_film_info(data)
        else:
            msg = f"Не удалось получить данные" + '\n'

    except requests.exceptions.RequestException as e:
        msg = f"Не удалось получить данные" + '\n'

    return msg


def search_film(name):
    url = 'https://api.kinopoisk.dev/v1.4/movie/search?'
    msg = ''
    res = []
    try:
        response = requests.get(url, headers={'X-API-KEY': KP_TOKEN}, params={'query': name})

        if response.status_code == 200:
            data = response.json()
            count = 0
            if 'docs' in data:
                films = data['docs']
                for film in films:
                    msg = get_film_info(film)
                    res.append(msg)
                    if count == 10:
                        break
                return res
        else:
            msg = f"Не удалось получить данные" + '\n'

    except requests.exceptions.RequestException as e:
        msg = f"Не удалось получить данные" + '\n'

    return msg


def get_params():
    params = {}

    genre = input('Введите жанр(Примеры: "драма", "комедия", "!мелодрама", "+ужасы") или -')
    if genre != '-':
        params['genres.name'] = genre

    film_year = input('Введите год(Примеры: 2000, 1999) или -')
    if film_year != '-':
        params['year'] = film_year

    film_country = input('Введите страну(Примеры: Россия, США, Франция) или -')
    if film_country != '-':
        params['countries.name'] = film_country

    return params


def search(params):
    url = 'https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10'
    try:
        response = requests.get(url, headers={'X-API-KEY': KP_TOKEN}, params=params)
        if response.status_code == 200:
            res = []
            data = response.json()
            for film in data['docs']:
                msg = get_film_info(film)
                res.append(msg)
            return res
        else:
            return "Не удалось найти фильмы с такими параметрами"
    except requests.exceptions.RequestException as e:
        return "Не удалось найти фильмы с такими параметрами"


print("Добро пожаловать в Kinopoisk API клиент!")
print("=" * 50)

while True:
    print("\nДоступные команды:")
    print("1. Получить случайный фильм")
    print("2. Поиск фильма по названию")
    print("3. Расширенный поиск по параметрам")
    print("4. Выход")
    print("=" * 50)

    choice = input("\nВыберите действие (1-4): ").strip()

    if choice == '1':
        print("\n" + "=" * 50)
        print("Случайный фильм:")
        print("=" * 50)
        result = random_film()
        print(result)

    elif choice == '2':
        print("\n" + "=" * 50)
        film_name = input("Введите название фильма для поиска: ").strip()
        if not film_name:
            print("Название не может быть пустым!")
            continue

        print(f"\nРезультаты поиска по запросу '{film_name}':")
        print("=" * 50)
        result = search_film(film_name)

        if isinstance(result, list):
            if not result:
                print("Фильмы не найдены.")
            else:
                for i, film in enumerate(result, 1):
                    print(f"\nРезультат {i}:")
                    print("-" * 30)
                    print(film)
        else:
            print(result)

    elif choice == '3':
        print("\n" + "=" * 50)
        print("Расширенный поиск")
        print("=" * 50)
        print("Заполните параметры (или введите '-' для пропуска):")

        params = get_params()

        if not params:
            print("Не выбрано ни одного параметра для поиска.")
            continue

        result = search(params)

        if isinstance(result, list):
            if not result:
                print("Фильмы не найдены по заданным параметрам.")
            else:
                print(f"Найдено фильмов: {len(result)}\n")
                for i, film in enumerate(result, 1):
                    print(f"Фильм {i}:")
                    print("-" * 30)
                    print(film)
                    print()
        else:
            print(result)

    elif choice == '4':
        print("\nСпасибо за использование! До свидания!")
        break

    else:
        print("\nНеверный выбор. Пожалуйста, выберите от 1 до 4.")
