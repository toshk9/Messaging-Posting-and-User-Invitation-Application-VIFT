from .account import get_accounts, login
import sqlite3, json
import configparser
import sys
import random 
import time
import vk

def add_friends():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall, messages')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    my_user_id = cpass['cred']['id']
    username = cpass['cred']['username']

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        friend_count = stats_decoded_json['vk']['friends'][username]
    except KeyError:
        friend_count = 0

    print("\n[1] - добавить в друзья пользователей из указанной таблицы.\n[2] - добавить в друзья определенных пользователей.")
    mode = int(input("\nВведите номер: "))

    succ_added_users = []
    fail_added_users = []
    if mode == 1:
        users = []
        with sqlite3.connect("VK/vk.db") as db:
            cursor = db.cursor()
            cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
            tables_list = cursor.fetchall()
            if len(tables_list) != 0:
                print("\nCуществующие таблицы: ")
                for table in enumerate(tables_list):
                    print(f"таблица: [{table[0]}] - {table[1][0]}")
            else:
                print("\nВ vk.db нет таблиц.\n")
                sys.exit()
            table_title = int(input('\nВведите номер таблицы, пользователей которой Вы хотите добавить в друзья: '))
            cursor.execute(""" SELECT * FROM {} """.format(tables_list[table_title][0]))
            users_data = cursor.fetchall()

            for user_data in users_data:
                user_id = int(user_data[1])
                users.append(user_id)

        users_to_send_num = input(f"\nВведите число пользователей, которых Вы хотите добавить в друзья.\nВведите \"all\", если Вы хотите добавить в друзья всех пользователей из таблицы: ")
        if users_to_send_num != "all":
            del users[int(users_to_send_num):]
        message = input("\nВведите текст сопроводительного сообщения для заявки на добавление в друзья.\nНажмите Enter, чтобы пропустить ввод: ")
        if message == "":
            message = None
        for user in users:
            friend_status = vk_api.friends.areFriends(user_ids=[my_user_id])[0]['friend_status']
            if friend_status == 1:
                print("Пользователь уже есть в списке друзей у данного аккаунта.")
                succ_added_users.append(user)
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
                continue
            try:
                print(f"\nОтправка заявки пользователю: {user}")    
                friend_status = vk_api.friends.add(user_id=user,text=message)
                succ_added_users.append(user)
                print("{}/{} пользователей получило заявку в друзья.".format(len(succ_added_users), len(users)))
                friend_count += 1
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
            except vk.exceptions.VkAPIError as err:
                if err.code == 14:
                    print("Не удалось добавить пользователя в друзья. ВКонтакте временно заблокировал отправку заявки в друзья данного аккаунта.\nПопробуйте снова через некоторый промежуток времени.")
                    sys.exit()
                else:
                    print(f"Не удалось добавить пользователя в друзья.\nОшибка: {err}.\nПропускаем...")
                    fail_added_users.append(user)
                    print("Подождите 1-30 секунд...")
                    time.sleep(random.randint(1,30))
    elif mode == 2:
        print("\nВведите id пользователя, которому нужно отправить заявку в друзья.\nВведите \"stop\", чтобы остановить ввод.")
        users = []
        user_inp = ""
        while True:
            if user_inp != "stop":
                user_inp = input()
                users.append(user_inp)
            else:
                break
        del users[-1]

        message = input("\nВведите текст сопроводительного сообщения для заявки на добавление в друзья.\nНажмите Enter, чтобы пропустить ввод: ")
        for user in users:
            friend_status = vk_api.friends.areFriends(user_ids=[my_user_id])[0]['friend_status']
            if friend_status == 1:
                print("Пользователь уже есть в списке друзей у данного аккаунта.")
                succ_added_users.append(user)
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
                continue
            try:
                print(f"\nОтправка заявки пользователю: {user}")    
                friend_status = vk_api.friends.add(user_id=user,text=message)
                succ_added_users.append(user)
                print("{}/{} пользователей получило заявку в друзья.".format(len(succ_added_users), len(users)))
                friend_count += 1
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
            except vk.exceptions.VkAPIError as err:
                if err.code == 14:
                    print("Не удалось добавить пользователя в друзья. ВКонтакте временно заблокировал отправку заявки в друзья данного аккаунта.\nПопробуйте снова через некоторый промежуток времени.")
                    sys.exit()
                else:
                    print(f"Не удалось добавить пользователя в друзья.\nОшибка: {err}.\nПропускаем...")
                    fail_added_users.append(user)
                    print("Подождите 1-30 секунд...")
                    time.sleep(random.randint(1,30))
    else: 
        print("\nНеправильная настройка добавления пользователей в друзья!\n")
        sys.exit()

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['vk']['friends'][username] = friend_count
        json.dump(stats_decoded_json, stats_json_file)

    print("\nГотово. Заявка была отправлена {}/{} пользователям.".format(len(succ_added_users), len(users)))
    print("Не удалось отправить заявку {}/{} пользователям".format(len(fail_added_users), len(users)))

def delete_friends():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall, messages')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    my_user_id = cpass['cred']['id']

    print("\n[1] - удалить из списка друзей пользователей из указанной таблицы.\n[2] - удалить из списка друзей определенных пользователей.")
    mode = int(input("\nВведите номер: "))

    succ_deleted_users = []
    fail_deleted_users = []
    if mode == 1:
        users = []
        with sqlite3.connect("VK/vk.db") as db:
            cursor = db.cursor()
            cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
            tables_list = cursor.fetchall()
            if len(tables_list) != 0:
                print("\nCуществующие таблицы: ")
                for table in enumerate(tables_list):
                    print(f"таблица: [{table[0]}] - {table[1][0]}")
            else:
                print("\nВ vk.db нет таблиц.\n")
                sys.exit()
            table_title = int(input('\nВведите номер таблицы, пользователей которой Вы хотите удалить из списка друзей: '))
            cursor.execute(""" SELECT * FROM {} """.format(tables_list[table_title][0]))
            users_data = cursor.fetchall()

            for user_data in users_data:
                user_id = int(user_data[1])
                users.append(user_id)

        users_to_send_num = input(f"\nВведите число пользователей, которых Вы хотите удалить из списка друзей.\nВведите \"all\", если Вы хотите удалить из списка друзей всех пользователей из таблицы: ")
        if users_to_send_num != "all":
            del users[int(users_to_send_num):]
        for user in users:
            friend_status = vk_api.friends.areFriends(user_ids=[my_user_id])[0]['friend_status']
            if friend_status == 0:
                print("Пользователя нет в списке друзей у данного аккаунта.")
                succ_deleted_users.append(user)
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
                continue
            try:
                print(f"\nУдаление из списка друзей пользователя: {user}")    
                vk_api.friends.delete(user_id=user)
                succ_deleted_users.append(user)
                print("{}/{} пользователей удалено из списка друзей.".format(len(succ_deleted_users), len(users)))
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
            except vk.exceptions.VkAPIError as err:
                print(f"Не удалось добавить пользователя в друзья.\nОшибка: {err}.\nПропускаем...")
                fail_deleted_users.append(user)
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
    elif mode == 2:
        print("\nВведите id пользователя, которого нужно удалить из списка друзей аккаунта.\nВведите \"stop\", чтобы остановить ввод.")
        users = []
        user_inp = ""
        while True:
            if user_inp != "stop":
                user_inp = input()
                users.append(user_inp)
            else:
                break
        del users[-1]

        for user in users:
            friend_status = vk_api.friends.areFriends(user_ids=[my_user_id])[0]['friend_status']
            if friend_status == 0:
                print("Пользователя нет в списке друзей у данного аккаунта.")
                succ_deleted_users.append(user)
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
                continue
            try:
                print(f"\nУдаление из списка друзей пользователя: {user}")    
                vk_api.friends.delete(user_id=user)
                succ_deleted_users.append(user)
                print("{}/{} пользователей удалено из списка друзей.".format(len(succ_deleted_users), len(users)))
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
            except vk.exceptions.VkAPIError as err:
                print(f"Не удалось удалить пользователя из списка друзей.\nОшибка: {err}.\nПропускаем...")
                fail_deleted_users.append(user)
                print("Подождите 1-30 секунд...")
                time.sleep(random.randint(1,30))
    else: 
        print("\nНеправильная настройка удаления из списка друзей!\n")
        sys.exit()

    print("\nГотово. {}/{} пользователей было удалено из списка друзей.".format(len(succ_deleted_users), len(users)))
    print("{}/{}  пользователей не удалось удалить из списка друзей.".format(len(fail_deleted_users), len(users)))


