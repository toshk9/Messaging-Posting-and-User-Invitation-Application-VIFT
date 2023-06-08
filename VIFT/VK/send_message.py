from .account import get_accounts, login
import sqlite3, json
import sys
import random
import vk
import time
import configparser


def send_message():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall, messages')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    my_user_id = cpass['cred']['id']
    username = cpass['cred']['username']

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        sent_count = stats_decoded_json['vk']['sended'][username]
    except KeyError:
        sent_count = 0

    print("[1] - отправить пользователям указанной таблицы;\n[2] - отправить определенным пользователям.")
    mode = int(input("\nВведите номер: "))
    
    fail_sent_users = []
    succ_sent_users = []
    if mode == 1:
        users = []
        with open("VK/last_user_vk.json", "r") as json_file:
            decoded_json = json.load(json_file)

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
                    if int(user_data[1]) == last_id_sms:
                        sent_users_num = len(users_data[:users_data.index(user_data)+1])
                        del users_data[:users_data.index(user_data)+1]
            for user_data in users_data:
                user_id = int(user_data[1])
                users.append(user_id)

        users_to_send_num = input(f"\nВведите число пользователей, которому Вы хотите отправить сообщение.\nВсего пользователей, которым уже было отправлено сообщение: {sent_users_num}.\nВведите \"all\", если Вы хотите отправить сообщение всем пользователям из таблицы: ")
        if users_to_send_num != "all":
            del users[int(users_to_send_num):]
        message = input("\nВведите сообщение, которое необходимо отправить: ")
        for user in users:
            try:
                print(f"\nОтправка сообщения пользователю: {user}")
                vk_api.messages.send(user_id=user, random_id=random.randint(1, 100000), message=message)
                with open("VK/last_user_vk.json", "w") as json_file:
                    decoded_json["sms"][tables_list[table_title][0]] = user
                    json.dump(decoded_json, json_file)
                succ_sent_users.append(user)
                sent_count += 1
                print("{}/{} пользователей получило сообщение.".format(len(succ_sent_users), len(users)))
                print("Подождите 1-5 секунд...")
                time.sleep(random.randint(1,5))
            except vk.exceptions.VkAPIError as err:
                if err.code == 902:
                    print(f"\nНе удалось отправить сообщение пользователю из-за его настроек приватности. Пропускаем...\n")
                    fail_sent_users.append(user)
                    with open("VK/last_user_vk.json", "w") as json_file:
                        decoded_json["sms"][tables_list[table_title][0]] = user
                        json.dump(decoded_json, json_file)
                    print("Подождите 1-5 секунд...")
                    time.sleep(random.randint(1,5))
                else:
                    print(f"Не удалось отправить сообщение. Ошибка: {err}. Пропускаем...")
                    fail_sent_users.append(user)
                    with open("VK/last_user_vk.json", "w") as json_file:
                        decoded_json["sms"][tables_list[table_title][0]] = user
                        json.dump(decoded_json, json_file)
                    print("Подождите 1-5 секунд...")
                    time.sleep(random.randint(1,5))
    elif mode == 2:
        print("\nВведите id пользователя, которому нужно отправить сообщение.\nВведите \"stop\", чтобы остановить ввод.")
        users = []
        user_inp = ""
        while True:
            if user_inp != "stop":
                user_inp = input()
                users.append(user_inp)
            else:
                break
        del users[-1]

        message = input("\nВведите сообщение, которое необходимо отправить: ")
        fail_sent_users = []
        succ_sent_users = []
        for user in users:
            try:
                print(f"\nОтправка сообщения пользователю: {user}")
                vk_api.messages.send(user_id=user, random_id=random.randint(1, 100000), message=message)
                succ_sent_users.append(user)
                print("{}/{} пользователей получило сообщение.".format(len(succ_sent_users), len(users)))
                print("Подождите 1-5 секунд...")
                sent_count += 1
                time.sleep(random.randint(1,5))
            except vk.exceptions.VkAPIError as err:
                if err.code == 902:
                    print(f"\nНе удалось отправить сообщение пользователю из-за его настроек приватности. Пропускаем...\n")
                    fail_sent_users.append(user)
                    print("Подождите 1-5 секунд...")
                    time.sleep(random.randint(1,5))
                else:
                    print(f"Не удалось отправить сообщение. Ошибка: {err}. Пропускаем...")
                    fail_sent_users.append(user)
                    print("Подождите 1-5 секунд...")
                    time.sleep(random.randint(1,5))
    else:
        print("\nНеправильная настройка отправки сообщений!\n")
        sys.exit()

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['vk']['sended'][username] = sent_count
        json.dump(stats_decoded_json, stats_json_file)
        
    print("\nГотово. Сообщение было отправлено {}/{} пользователям.".format(len(succ_sent_users), len(users)))
    print("Не удалось отправить сообщение {}/{} пользователям".format(len(fail_sent_users), len(users)))
        


