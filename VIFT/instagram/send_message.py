from instabot import Bot
from .account import get_accounts
import configparser
import sys
import sqlite3, json


def send_message():
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
        sent_count = stats_decoded_json['instagram']['sended'][username]
    except KeyError:
        sent_count = 0

    users = []
    with open("instagram/last_user_inst.json", "r") as json_file:
        decoded_json = json.load(json_file)

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
        table_title = int(input('\nВведите номер таблицы, пользователи которой получат сообщение: '))
        try:
            last_id_sms = int(decoded_json["sms"][tables_list[table_title][0]])
        except KeyError:
            last_id_sms = None
        sent_users_num = 0
        cursor.execute(""" SELECT * FROM {} """.format(tables_list[table_title][0]))
        users_data = cursor.fetchall()
        if last_id_sms is not None:
            for user_data in users_data:
                if int(user_data[2]) == last_id_sms:
                    sent_users_num = len(users_data[:users_data.index(user_data)+1])
                    del users_data[:users_data.index(user_data)+1]
        for user_data in users_data:
            user_id = str(user_data[2])
            users.append(user_id)

    print("[1] - отправить пользователям указанной таблицы;\n[2] - отправить определенным пользователям.")
    mode = int(input("\nВведите номер: "))

    if mode == 1:
        users_to_send_num = input(f"\nВведите число пользователей, которому Вы хотите отправить сообщение.\nВсего пользователей, которым уже было отправлено сообщение: {sent_users_num}.\nВведите \"all\", если Вы хотите отправить сообщение всем пользователям из таблицы: ")
        if users_to_send_num != "all":
            del users[int(users_to_send_num):]
        message = input("\nВведите сообщение, которое необходимо отправить: ")
        try:
            bot.send_message(text=message, user_ids=users)
            sent_count += len(users)
            with open("instagram/last_user_inst.json", "w") as json_file:
                decoded_json["sms"][tables_list[table_title][0]] = int(users[-1])
                json.dump(decoded_json, json_file)
            print(f"\nСообщение успешно отправлено {len(users)} пользователям.")
        except:
            print("\nНе удалось отправить сообщение.\n")
    elif mode == 2:
        print("\nВведите имя пользователя, которому нужно отправить сообщение.\nВведите \"stop\", чтобы остановить ввод.")
        usernames_to_send = []
        user_inp = ""
        while True:
            if user_inp != "stop":
                user_inp = input()
                usernames_to_send.append(user_inp)
            else:
                break
        del usernames_to_send[-1]
        userids_to_send = []
        for username_to_send in usernames_to_send:
            try:
                userid = bot.get_user_id_from_username(username_to_send)
                userids_to_send.append(userid)
            except:
                print(f"Неверное имя пользователя: {username_to_send}")
                continue
        message = input("\nВведите сообщение, которое необходимо отправить: ")
        try:
            bot.send_message(text=message, user_ids=userids_to_send)
            print(f"\nСообщение успешно отправлено {len(userids_to_send)} пользователям.")
            sent_count += len(userids_to_send)
        except:
            print("\nНе удалось отправить сообщение.\n")
    else:
        print("\nНеправильная настройка отправки сообщений!\n")
        bot.logout()
        sys.exit()

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['instagram']['sended'][username] = sent_count
        json.dump(stats_decoded_json, stats_json_file)

    bot.logout()


