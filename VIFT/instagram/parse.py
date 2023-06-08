from instabot import Bot
from .account import get_accounts
import configparser
import sys
import time
import sqlite3


def parse():
    acc_title = get_accounts()
    cpass = configparser.RawConfigParser()
    cpass.read(f"accounts/instagram_accs/{acc_title}/config.data")

    try:
        username = cpass['cred']['username']
        password = cpass['cred']['password']
        bot = Bot()
        bot.login(username=username, password=password, use_cookie=False)
        print(f"\nВход был выполнен в аккаунт с именем {username}\n")
    except KeyError:
        print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py")
        sys.exit(1)

    print("\n[1] - собрать подписчиков данного аккаунта;\n[2] - собрать подписчиков определенного аккаунта;\n[3] - собрать подписки данного аккаунта.")
    mode = int(input("Введите номер: "))

    if any([mode == 1, mode == 2]):
        if mode == 1:
            username_f = username
        elif mode == 2:
            username_f = input("\nВведите имя пользователя, подписчиков которого нужно собрать: ")
        userid_f = bot.get_user_id_from_username(username_f)
        print('\nСбор участников...\n')
        followers_id_list = bot.get_user_followers(userid_f)
        users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего подписчиков: {len(followers_id_list)}.\nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
        if users_to_parse_num != "all":
            del followers_id_list[int(users_to_parse_num):]

        with sqlite3.connect('instagram/instagram.db') as db:
            parserd_users =  []
            fail_parsed_users = []
            cursor = db.cursor()
            cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
            tables_list = cursor.fetchall()
            if len(tables_list) != 0:
                print("\nУже существующие таблицы: ")
                for table in enumerate(tables_list):
                    print(f"таблица: [{table[0]}] - {table[1][0]}")
            table_title = input('\nВведите название таблицы, куда будут сохранены пользователи: ')
            time.sleep(1)
            print('Сохранение...')
            cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, username TEXT, user_id INTEGER, parsed_from_username TEXT, parsed_from_id INTEGER) """.format(table_title))
            for user in followers_id_list:
                list_id = int(followers_id_list.index(user)) + 1
                follower_id = user
                follower_username = bot.get_username_from_user_id(follower_id)
                following_username = username_f
                following_id = userid_f

                cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, follower_id))
                if cursor.fetchone()[0] == 0:
                    user_data = (list_id, follower_username, follower_id, following_username, following_id)
                    cursor.execute(""" INSERT INTO {} (list_id, username, user_id, parsed_from_username, parsed_from_id) VALUES(?, ?, ?, ?, ?) """.format(table_title), user_data)
                    parserd_users.append(user)
                    print("{}/{} пользователей собрано".format(len(parserd_users), len(followers_id_list)))
                else:
                    print("Пользователь уже есть в таблице.")
                    fail_parsed_users.append(user)
                    continue
                db.commit()
        print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(followers_id_list), table_title))
        print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(followers_id_list), table_title))
    elif mode == 3:
        username_f = username
        userid_f = bot.get_user_id_from_username(username_f)
        print('\nСбор участников...\n')
        followers_id_list = bot.get_user_following(userid_f)
        users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего подписок: {len(followers_id_list)}.\nВведите \"all\", если Вы хотите спарсить все подписки данного аккаунта: ")
        if users_to_parse_num != "all":
            del followers_id_list[int(users_to_parse_num):]

        with sqlite3.connect('instagram/instagram.db') as db:
            parserd_users =  []
            fail_parsed_users = []
            cursor = db.cursor()
            cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
            tables_list = cursor.fetchall()
            if len(tables_list) != 0:
                print("\nУже существующие таблицы: ")
                for table in enumerate(tables_list):
                    print(f"таблица: [{table[0]}] - {table[1][0]}")
            table_title = input('\nВведите название таблицы, куда будут сохранены пользователи: ')
            time.sleep(1)
            print('Сохранение...')
            cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, username TEXT, user_id INTEGER, parsed_from_username TEXT, parsed_from_id INTEGER) """.format(table_title))
            for user in followers_id_list:
                list_id = int(followers_id_list.index(user)) + 1
                follower_id = user
                follower_username = bot.get_username_from_user_id(follower_id)
                following_username = username_f
                following_id = userid_f

                cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, follower_id))
                if cursor.fetchone()[0] == 0:
                    user_data = (list_id, follower_username, follower_id, following_username, following_id)
                    cursor.execute(""" INSERT INTO {} (list_id, username, user_id, parsed_from_username, parsed_from_id) VALUES(?, ?, ?, ?, ?) """.format(table_title), user_data)
                    parserd_users.append(user)
                    print("{}/{} пользователей собрано".format(len(parserd_users), len(followers_id_list)))
                else:
                    print("Пользователь уже есть в таблице.")
                    fail_parsed_users.append(user)
                    continue
                db.commit()
        print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(followers_id_list), table_title))
        print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(followers_id_list), table_title))
    else:
        print("\nНеправильная настройка cбора пользователей!\n")