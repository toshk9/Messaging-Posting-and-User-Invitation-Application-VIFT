from .account import get_accounts, login
import sys, os
import random
import vk
import time
import configparser
import requests
from datetime import datetime
import json, sqlite3


def post():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall, messages')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    my_user_id = cpass['cred']['id']
    username = cpass['cred']['username']

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        post_count = stats_decoded_json['vk']['posted'][username]
    except KeyError:
        post_count = 0

    print('\n[!] Перед использованием убедитесь: файлы, которые необходимо загрузить, находятся в директории VIFT/resources [!]\n')
    print("[1] - Загрузить фото на страницу аккаунта;\n[2] - загрузить видео на страницу аккаунта;\n[3] - Загрузить текстовый пост на страницу аккаунта.")
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

    print("\n[1] - Опубликовать пост сейчас;\n[2] - Отложить публикацию поста.")
    mode_1 = int(input("\nВведите номер: "))

    if mode_1 == 2:
        upload_date = input("Введите дату размещения записи в формате 31.12.1999: ").split(".")
        upload_hm = input("Введите время размещения записи в формате 23:59: ").split(":")

        upload_time = f"{upload_date[0]}/{upload_date[1]}/{upload_date[2]}/{upload_hm[0]}/{upload_hm[1]}"
        try:
            timestamp = time.mktime(datetime.strptime(upload_time, "%d/%m/%Y/%H/%M").timetuple())
            s_date = f"{upload_date[0]}.{upload_date[1]}.{upload_date[2]}"
            s_time = f"{upload_hm[0]}:{upload_hm[1]}"
        except ValueError:
            print("Неправильно введено время публикации!")
            sys.exit()
    elif mode_1 == 1:
        timestamp = None
        s_date = None
        s_time = None
    else:
        print("\nНеправильная настройка времени публикации поста!")
        sys.exit()

    def save_post(date, time, content, post_id, owner_id):
        if mode_1 == 2:
            with sqlite3.connect('VK/planned_posts_vk.db') as db:
                cursor = db.cursor()
                cursor.execute(""" CREATE TABLE IF NOT EXISTS planned_posts (date TEXT, time TEXT, content TEXT, post_id INTEGER, owner_id INTEGER) """)
                post_data = (date, time, content, int(post_id), int(owner_id))
                cursor.execute(f""" INSERT INTO planned_posts (date, time, content, post_id, owner_id) VALUES(?, ?, ?, ?, ?) """, post_data)
                db.commit()

    if mode == 1:
        filename = f'resources/{get_file()}'
        message = input("\nВведите текст, который будет прикреплен к записи. Нажмите Enter, чтобы пропустить: ")
        upload_url = vk_api.photos.getWallUploadServer()['upload_url']
        try:
            resp = requests.post(upload_url, files = {'file': open(filename, 'rb')}).json()
            s = vk_api.photos.saveWallPhoto(server = resp['server'], photo=resp['photo'], hash = resp['hash'])
            post_id = vk_api.wall.post(owner_id = my_user_id, message=message, attachments=f"photo{s[0]['owner_id']}_{s[0]['id']}", publish_date=timestamp)['post_id']
            save_post(s_date, s_time, message + " + " + filename, post_id, my_user_id)
            post_count += 1
            print("Запись успешно опубликована!")
        except vk.exceptions.VkAPIError as err:
            if err.code == 29:
                print("Превышен лимит запросов в сутки.")   
            elif err.code == 5:
                print("Пользователь заблокирован. Публикация невозможна.")       
            else:
                print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
        
    elif mode == 2:
        filename = f'resources/{get_file()}'
        message = input("\nВведите текст, который будет прикреплен к записи. Нажмите Enter, чтобы пропустить: ")
        try:
            upload_url = vk_api.video.save()['upload_url']
            resp = requests.post(upload_url, files = {'video_file': open(filename, 'rb')}).json()
            post_id = vk_api.wall.post(owner_id = my_user_id, message=message, attachments=f"video{resp['owner_id']}_{resp['video_id']}", publish_date=timestamp)['post_id']
            save_post(s_date, s_time, message + " + " + filename, post_id, my_user_id)
            post_count += 1
            print("Запись успешно опубликована!")
        except vk.exceptions.VkAPIError as err:
            if err.code == 29:
                print("Превышен лимит запросов в сутки.")   
            elif err.code == 5:
                print("Пользователь заблокирован. Публикация невозможна.")       
            else:
                print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
    elif mode == 3:
        message = input("\nВведите текст поста: ") 
        try:
            post_id = vk_api.wall.post(owner_id = my_user_id, message=message, publish_date=timestamp)['post_id']
            save_post(s_date, s_time, message, post_id, my_user_id)
            post_count += 1
            print("Запись успешно опубликована!")
        except vk.exceptions.VkAPIError as err:
            if err.code == 29:
                print("Превышен лимит запросов в сутки.")   
            elif err.code == 5:
                print("Пользователь заблокирован. Публикация невозможна.")       
            else:
                print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
    else:
        print("\nНеправильная настройка типа поста!")
    
    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['vk']['posted'][username] = post_count
        json.dump(stats_decoded_json, stats_json_file)
