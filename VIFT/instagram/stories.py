from instabot import Bot
import sys, os
import configparser
import json
from .account import get_accounts


def stories():
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
        stories_count = stats_decoded_json['instagram']['stories'][username]
    except KeyError:
        stories_count = 0

    print('\n[!] Перед использованием убедитесь: файлы, которые необходимо загрузить, находятся в директории VIFT/resources [!]\n')

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

    filename = f'resources/{get_file()}'
    bot.upload_story_photo(photo=filename)
    stories_count += 1
    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['instagram']['stories'][username] = stories_count
        json.dump(stats_decoded_json, stats_json_file)

