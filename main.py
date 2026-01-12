import requests
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

# Получаем токены из переменных окружения
KP_TOKEN = os.getenv('KINOPOISK_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

INPUT_MOVIE = 0


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Привет! Этот бот ищет фильмы\nДоступные команды: \n /random - случайный фильм\n /film - поиск по названию\n")


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
    if 'shortDescription' in data:
        msg += f'Описание: {data["shortDescription"]}' + '\n'

    img_url = None
    if 'poster' in data:
        img_url = data["poster"]["url"]

    return msg, img_url


async def random_handler(update: Update, context: CallbackContext):
    msg, img = random_film()

    if img:
        await update.message.reply_photo(photo=img, caption=msg)
    else:
        await update.message.reply_text(msg)


def random_film():
    url = 'https://api.kinopoisk.dev/v1.4/movie/random'
    img = None
    try:
        response = requests.get(url, headers={'X-API-KEY': KP_TOKEN}, params={
            'notNullFields': ['name', 'status', 'year', 'countries.name', 'genres.name', 'rating.kp', 'rating.imdb',
                              'shortDescription', 'poster.url']})

        if response.status_code == 200:
            data = response.json()
            msg, img = get_film_info(data)
        else:
            msg = f"Не удалось получить данные" + '\n'
            print(f"Failed to retrieve data: {response}")

    except requests.exceptions.RequestException as e:
        msg = f"Не удалось получить данные" + '\n'
        print(f"An error occurred: {e}")

    return msg, img


async def film_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я помогу найти фильм по названию, введите название фильма: ")
    return INPUT_MOVIE


async def search_movie(update: Update, context: CallbackContext):
    movie_name = update.message.text
    res = search_film(movie_name)

    if isinstance(res, str):
        await update.message.reply_text(res)
    else:
        for msg, img in res:
            if img:
                await update.message.reply_photo(photo=img, caption=msg)
            else:
                await update.message.reply_text(msg)

    return ConversationHandler.END


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
                    msg, img = get_film_info(film)
                    if img:
                        count += 1
                        res.append((msg, img))
                    if count == 10:
                        break
                return res
        else:
            msg += f"Не удалось получить данные" + '\n'

    except requests.exceptions.RequestException as e:
        msg += f"Не удалось получить данные" + '\n'
        print(f"An error occurred: {e}")

    return msg


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Поиск отменен")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_handler))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("film", film_handler)],
        states={
            INPUT_MOVIE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        # Важно: allow_reentry позволяет команде /film снова запустить диалог
        allow_reentry=True
    )
    
    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == '__main__':
    main()