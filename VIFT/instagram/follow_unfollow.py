from instabot import Bot
import sys
import configparser
import time 
from .account import get_accounts
import sqlite3, json

def follow():
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
        follow_count = stats_decoded_json['instagram']['followed'][username]
    except KeyError:
        follow_count = 0

    print("\n[1] - подписаться на пользователей из указанной таблицы.\n[2] - подписаться на определенных пользователей.")
    mode = int(input("\nВведите номер: "))
    
    if mode == 1:
        users = []
        with sqlite3.connect("instagram/instagram.db") as db:
            cursor = db.cursor()
            cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
            tables_list = cursor.fetchall()
            if len(tables_list) != 0:
                print("\nCуществующие таблицы: ")
                for table in enumerate(tables_list):
                    print(f"таблица: [{table[0]}] - {table[1][0]}")
            else:
                print("\nВ instagram.db нет таблиц.\n")
                sys.exit()
            table_title = int(input('\nВведите номер таблицы, на пользователей которой Вы хотите подписаться: '))
            cursor.execute(""" SELECT * FROM {} """.format(tables_list[table_title][0]))
            users_data = cursor.fetchall()

            for user_data in users_data:
                user_id = int(user_data[2])
                users.append(user_id)

        users_to_follow_num = input(f"\nВведите число пользователей, на которых Вы хотите подписаться.\nВведите \"all\", если Вы хотите подписаться на всех пользователей из таблицы: ")
        if users_to_follow_num != "all":
            del users[int(users_to_follow_num):]
        
        print("\nПроисходит подписка аккаунта на указанных пользователей...\n")
        try:
            bot.follow_users(users)
            follow_count += len(users)
            print("\nПодписка успешно завершена!")
        except:
            print("\nНе удалось подписаться на всех указанных пользователей. Попробуйте снова через некоторый промежуток времени..")
        
    elif mode == 2:
        print("\nВведите имя пользователя, на которого должен подписаться аккаунт.\nВведите \"stop\", чтобы остановить ввод.")
        usernames_to_follow = []
        user_inp = ""
        while True:
            if user_inp != "stop":
                user_inp = input()
                usernames_to_follow.append(user_inp)
            else:
                break
        del usernames_to_follow[-1]
        my_user_id = bot.get_user_id_from_username(username)
        following_list = bot.get_user_following(my_user_id)
        userids_to_follow = []
        for username_to_follow in usernames_to_follow:
            try:
                userid = bot.get_user_id_from_username(username_to_follow)
                if userid not in following_list:
                    userids_to_follow.append(userid)
            except:
                print(f"Неверное имя пользователя: {username_to_follow}")
                continue
        try:    
            print("\nПроисходит подписка аккаунта на указанных пользователей...\n")
            bot.follow_users(userids_to_follow)
            print("\nПодписка успешно завершена!")
            follow_count += len(userids_to_follow)
        except:
            print("\nНе удалось подписаться на всех указанных пользователей. Попробуйте снова через некоторый промежуток времени..")
        
    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['instagram']['followed'][username] = follow_count
        json.dump(stats_decoded_json, stats_json_file)


def unfollow():
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

    print("\n[1] - отписаться от пользователей из указанной таблицы.\n[2] - отписаться от определенных пользователей.")
    mode = int(input("\nВведите номер: "))
    
    if mode == 1:
        users = []
        with sqlite3.connect("instagram/instagram.db") as db:
            cursor = db.cursor()
            cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
            tables_list = cursor.fetchall()
            if len(tables_list) != 0:
                print("\nCуществующие таблицы: ")
                for table in enumerate(tables_list):
                    print(f"таблица: [{table[0]}] - {table[1][0]}")
            else:
                print("\nВ instagram.db нет таблиц.\n")
                sys.exit()
            table_title = int(input('\nВведите номер таблицы, от пользователей которой Вы хотите отписаться: '))
            cursor.execute(""" SELECT * FROM {} """.format(tables_list[table_title][0]))
            users_data = cursor.fetchall()

            for user_data in users_data:
                user_id = int(user_data[2])
                users.append(user_id)

        users_to_follow_num = input(f"\nВведите число пользователей, от которых Вы хотите отписаться.\nВведите \"all\", если Вы хотите отписаться от всех пользователей из таблицы: ")
        if users_to_follow_num != "all":
            del users[int(users_to_follow_num):]
        
        print("\nПроисходит отписка аккаунта от указанных пользователей...\n")
        try:
            bot.unfollow_users(users)
            print("\nОтписка успешно завершена!")
        except:
            print("\nНе удалось отписаться от всех указанных пользователей. Попробуйте снова через некоторый промежуток времени..")

    elif mode == 2:
        print("\nВведите имя пользователя, от которого должен отписаться аккаунт.\nВведите \"stop\", чтобы остановить ввод.")
        usernames_to_unfollow = []
        user_inp = ""
        while True:
            if user_inp != "stop":
                user_inp = input()
                usernames_to_unfollow.append(user_inp)
            else:
                break
        del usernames_to_unfollow[-1]
        my_user_id = bot.get_user_id_from_username(username)
        following_list = bot.get_user_following(my_user_id)
        userids_to_unfollow = []
        for username_to_unfollow in usernames_to_unfollow:
            try:
                userid = bot.get_user_id_from_username(username_to_unfollow)
                if userid in following_list:
                    userids_to_unfollow.append(userid)
            except:
                print(f"Неверное имя пользователя: {username_to_unfollow}")
                continue
            
        print("\nПроисходит отписка аккаунта от указанных пользователей...\n")
        bot.unfollow_users(userids_to_unfollow)
        print("\nОтписка успешно завершена!")    
