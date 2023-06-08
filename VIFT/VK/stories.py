from .account import get_accounts, login
import sys, os
import random
import vk
import time
import configparser
import requests
from datetime import datetime
import json


def stories():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall, messages, stories')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    my_user_id = cpass['cred']['id']
    username = cpass['cred']['username']

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        stories_count = stats_decoded_json['vk']['stories'][username]
    except KeyError:
        stories_count = 0

    print('\n[!] Перед использованием убедитесь: файлы, которые необходимо загрузить, находятся в директории VIFT/resources [!]\n')
    print("[1] - Загрузить фото в сторис аккаунта;\n[2] - загрузить видео в сторис аккаунта.")
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

    timestamp = None

    if mode == 1:
        filename = f'resources/{get_file()}'
        link_url = input("\nВведите адрес ссылки для перехода из истории. Допустимы только внутренние ссылки https://vk.com. Нажмите Enter, чтобы пропустить: ")
        if link_url == "":
            link_url = None
        upload_url = vk_api.stories.getPhotoUploadServer(add_to_news=1,link_url=link_url)
        try:
            resp = requests.post(upload_url['upload_url'], files = {'file': open(filename, 'rb')}).json()['response']['upload_result']
            vk_api.stories.save(upload_results=resp)
            stories_count += 1
            print("Запись успешно опубликована!")
        except vk.exceptions.VkAPIError as err:
            print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
            print(err)
        
    elif mode == 2:
        filename = f'resources/{get_file()}'
        link_url = input("\nВведите адрес ссылки для перехода из истории. Допустимы только внутренние ссылки https://vk.com. Нажмите Enter, чтобы пропустить: ")
        upload_url = vk_api.stories.getVideoUploadServer(add_to_news=1,link_url=link_url)
        try:
            resp = requests.post(upload_url['upload_url'], files = {'file': open(filename, 'rb')}).json()['response']['upload_result']
            vk_api.stories.save(upload_results=resp)
            stories_count += 1
            print("Запись успешно опубликована!")
        except vk.exceptions.VkAPIError:
            print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
    else:
        print("\nНеправильная настройка типа поста!")

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['vk']['stories'][username] = stories_count
        json.dump(stats_decoded_json, stats_json_file)