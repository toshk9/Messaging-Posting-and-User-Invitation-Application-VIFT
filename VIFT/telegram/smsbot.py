from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
import configparser
import os, sys
import sqlite3, json
import random
import time
import socks
from .check_spam import dates_list


def sms():
    SLEEP_TIME = 30

    dir_list = os.listdir(path="accounts/telegram_accs")
    date_list = dates_list()
    cpass = configparser.RawConfigParser()
    for direct in enumerate(dir_list):
        acc_dir = direct[1]
        cpass.read('accounts/telegram_accs/{}/config.data'.format(acc_dir))
        phone = cpass['cred']['phone']
        lim_status = date_list[int(dir_list.index(direct[1]))]
        if lim_status != "[+]":
            print(f"аккаунт: [{direct[0]}] - {direct[1]} ({phone}) " + "[-]" + f" Дата разблокировки: {lim_status}")
        else:
            print(f"аккаунт: [{direct[0]}] - {direct[1]} ({phone}) {lim_status}")

    print("\nВыберите аккаунт для входа.")
    acc_title = int(input("Введите номер аккаунта: "))

    try:
        cpass.read('accounts/telegram_accs/{}/config.data'.format(dir_list[acc_title]))
        api_id = cpass['cred']['id']
        api_hash = cpass['cred']['hash']
        phone = cpass['cred']['phone']
        ip = cpass['cred']['ip']
        port = cpass['cred']['port']
    except KeyError:
        print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py\n")
        sys.exit(1)

    client = TelegramClient(phone, api_id, api_hash, proxy=(socks.SOCKS4, ip, port))
    print("\nВход был выполнен в аккаунт с номером {}".format(phone))
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Введите код, который придет на Ваш номер телефона: '))

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        sent_count = stats_decoded_json['telegram']['sended'][phone]
    except KeyError:
        sent_count = 0

    users = []

    with open("telegram/last_user.json", "r") as json_file:
        decoded_json = json.load(json_file)

    with sqlite3.connect("telegram/telegram.db") as db:
        cursor = db.cursor()
        cursor.execute(""" SELECT name FROM sqlite_master WHERE type="table" """)
        tables_list = cursor.fetchall()
        if len(tables_list) != 0:
            print("\nCуществующие таблицы: ")
            for table in enumerate(tables_list):
                print(f"таблица: [{table[0]}] - {table[1][0]}")
        else:
            print("\nВ telegram.db нет таблиц.\nЗапустите main.py повторно и напишите parse, чтобы создать новые таблицы.\n")
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
            user = {}
            user['username'] = user_data[1]
            user['id'] = int(user_data[2])
            user['access_hash'] = int(user_data[3])
            user['name'] = user_data[4]
            users.append(user)

    print("\n[1] отправить сообщение пользователю по id (рекомендовано)\n[2] отправить сообщение пользователю по username")
    mode = int(input("Введите номер : "))
        
    message = input("\nВведите ваше сообщение: ")

    users_to_send_num = input(f"\nВведите число пользователей, которому Вы хотите отправить сообщение.\nВсего пользователей, которым уже было отправлено сообщение: {sent_users_num}.\nВведите \"all\", если Вы хотите пригласить всех пользователей из таблицы: ")
    if users_to_send_num != "all":
        del users[int(users_to_send_num):]

    sent_users = [] 
    fail_sent_users = [] 
    for user in users:
        if mode == 2:
            if user['username'] == "":
                print("[!] У пользователя скрыто его имя.\Отправка сообщений по этой настройке невозможно. Пропускаем...")
                with open("telegram/last_user.json", "w") as json_file:
                    decoded_json["sms"][tables_list[table_title][0]] = user['id']
                    json.dump(decoded_json, json_file)
                continue
            receiver = client.get_input_entity(user['username'])
        elif mode == 1:
            receiver = InputPeerUser(user['id'], user['access_hash'])
        else:
            print("\n[!] Выбрана неправильная настройка! \nПопробуйте снова.")
            client.disconnect()
            sys.exit()
        try:
            print("\nОтправка сообщения пользователю: ", user['name'])
            client.send_message(receiver, message.format(user['name']))
            sent_users.append(user)
            print("{}/{} пользователей получило сообщение.".format(len(sent_users), len(users)))
            with open("telegram/last_user.json", "w") as json_file:
                decoded_json["sms"][tables_list[table_title][0]] = user['id']
                json.dump(decoded_json, json_file)
            print("Ожидайте {} секунд".format(SLEEP_TIME))
            sent_count += 1
            time.sleep(1)
        except PeerFloodError:
            print("[!] Отправка сообщений была временно заблокирована Телеграмом. \n[!] Скрипт останавливается. \n[!] Попробуйте снова через некоторое время.")
            fail_sent_users.append(user)
            with open("telegram/last_user.json", "w") as json_file:
                decoded_json["sms"][tables_list[table_title][0]] = user['id']
                json.dump(decoded_json, json_file)
            break
        except Exception as e:
            print("[!] Ошибка:", e)
            print("[!] Пробуем продолжить...")
            fail_sent_users.append(user)
            with open("telegram/last_user.json", "w") as json_file:
                decoded_json["sms"][tables_list[table_title][0]] = user['id']
                json.dump(decoded_json, json_file)
            continue
    client.disconnect()

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['telegram']['sended'][phone] = sent_count
        json.dump(stats_decoded_json, stats_json_file)

    print("\nГотово. Сообщение было отправлено {}/{} пользователям.".format(len(sent_users), len(users)))
    print("Не удалось отправить сообщение {}/{} пользователям".format(len(fail_sent_users), len(users)))

