from instabot import Bot
import sys, os
import configparser
from .account import get_accounts
import json


def post():
    acc_title = get_accounts()
    cpass = configparser.RawConfigParser()
    cpass.read(f"accounts/instagram_accs/{acc_title}/config.data")

    try:
        username = cpass['cred']['username']
        password = cpass['cred']['password']
        bot = Bot()
        bot.login(username=username, password=password, use_cookie=False)
        print(f"\nВход был выполнен в аккаунт с именем {username}")
    except KeyError:
        print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py")
        sys.exit(1)

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        post_count = stats_decoded_json['instagram']['posted'][username]
    except KeyError:
        post_count = 0

    print('\n[!] Перед использованием убедитесь: файлы, которые необходимо загрузить, находятся в директории VIFT/resources [!]\n')
    print("[1] - Загрузить фото на страницу аккаунта;\n[2] - загрузить видео на страницу аккаунта.")
    mode = int(input("\nВведите номер: "))

    def get_file():
        print()
        files = os.listdir('resources')
        if len(files) != 0:
            for file in enumerate(files):
                print(f"[{file[0]}] - {file[1]}")
            print("\nВыберите файл для загрузки.")
            file_num = int(input("Введите номер: "))
            filename = files[file_num]
            return filename
        else:
            print("В директории VIFT/resources нет файлов.")
            sys.exit()


    if mode == 1:
        filename = f'resources/{get_file()}'
        message = input("\nВведите текст, который будет прикреплен к записи. Нажмите Enter, чтобы пропустить: ")
        if message == "":
            message = None
        try:
            bot.upload_photo(photo=filename, caption=message)
            post_count += 1
            print("Запись успешно опубликована!")
        except:
            print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
        
    elif mode == 2:
        filename = f'resources/{get_file()}'
        message = input("\nВведите текст, который будет прикреплен к записи. Нажмите Enter, чтобы пропустить: ")
        if message == "":
            message = None
        try:
            bot.upload_video(video=filename, caption=message)
            post_count += 1
            print("Запись успешно опубликована!")
        except:
            print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
    else:
        print("\nНеправильная настройка типа поста!")

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['instagram']['posted'][username] = post_count
        json.dump(stats_decoded_json, stats_json_file)