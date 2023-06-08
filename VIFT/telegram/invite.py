#!/usr/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, ChatWriteForbiddenError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser
import os, sys
import sqlite3, json
import traceback
import time
import random
import socks 
from .check_spam import dates_list


def invite():
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

    cpass.read('accounts/telegram_accs/{}/config.data'.format(dir_list[acc_title]))
    try:
        api_id = cpass['cred']['id']
        api_hash = cpass['cred']['hash']
        phone = cpass['cred']['phone']
        ip = cpass['cred']['ip']
        port = cpass['cred']['port']
        client = TelegramClient(phone, api_id, api_hash, proxy=(socks.SOCKS4, ip, port))
        print("\nВход был выполнен в аккаунт с номером {}".format(phone))
    except KeyError:
        print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py\n")
        sys.exit(1)

    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Введите код, который придет на Ваш номер телефона: \n'))
    
    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        invite_count = stats_decoded_json['telegram']['invited'][phone]
    except KeyError:
        invite_count = 0

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
        table_title = int(input('\nВведите номер таблицы, пользователей которой Вы хотите пригласить: '))
        try:
            last_id_invite = int(decoded_json["invite"][tables_list[table_title][0]])
        except KeyError:
            last_id_invite = None
        invited_users_num = 0
        cursor.execute(""" SELECT * FROM {} """.format(tables_list[table_title][0]))
        users_data = cursor.fetchall()
        if last_id_invite is not None:
            for user_data in users_data:
                if int(user_data[2]) == last_id_invite:
                    invited_users_num = len(users_data[:users_data.index(user_data)+1])
                    del users_data[:users_data.index(user_data)+1]
        for user_data in users_data:
            user = {}
            user['username'] = user_data[1]
            user['id'] = int(user_data[2])
            user['access_hash'] = int(user_data[3])
            user['name'] = user_data[4]
            users.append(user)
    
    chats = []
    last_date = None
    chunk_size = 200
    groups=[]
    
    result = client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=chunk_size,
                hash = 0
            ))
    chats.extend(result.chats)
    
    for chat in chats:
        try:
            if chat.megagroup== True:
                groups.append(chat)
        except:
            continue
    
    i=0
    for group in groups:
        print(f'[{str(i)}] - ' + group.title)
        i+=1

    print('\nВыберите группу, куда Вы хотите пригласить пользователей: ')
    g_index = input("Введите номер : ")
    target_group = groups[int(g_index)]
    
    target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)
    
    print("\n[1] пригласить пользователя по id (рекомендовано)\n[2] пригласить пользователя по username")
    mode = int(input("Введите номер : ")) 
    users_to_invite_num = input(f"\nВведите число пользователей, которое Вы хотите пригласить.\nВсего приглашено: {invited_users_num}.\nВведите \"all\", если Вы хотите пригласить всех пользователей из таблицы: ")
    if users_to_invite_num != "all":
        del users[int(users_to_invite_num):]
        
    invited_users = []
    fail_invited_users = []
    for user in users:
        time.sleep(1)
        try:
            print ("\nДобавление пользователя {}".format(user['id']))
            if mode == 2:
                if user['username'] == "":
                    print("[!] У пользователя скрыто его имя.\nПриглашение по этой настройке невозможно. Пропускаем...")
                    with open("telegram/last_user.json", "w") as json_file:
                        decoded_json["invite"][tables_list[table_title][0]] = user['id']
                        json.dump(decoded_json, json_file)
                    continue
                user_to_add = client.get_input_entity(user['username'])
            elif mode == 1:
                user_to_add = InputPeerUser(user['id'], user['access_hash'])
            else:
                sys.exit("\n[!] Выбрана неправильная настройка! \nПопробуйте снова.")
            client(InviteToChannelRequest(target_group_entity,[user_to_add]))
            invited_users.append(user)
            print("{}/{} пользователей приглашено.".format(len(invited_users), len(users)))
            invite_count += 1
            print("Ожидайте 10-30 секунд...")
            with open("telegram/last_user.json", "w") as json_file:
                decoded_json["invite"][tables_list[table_title][0]] = user['id']
                json.dump(decoded_json, json_file)
            time.sleep(random.randrange(10, 30))
        except PeerFloodError:
            print("[!] Приглашение было временно заблокировано Телеграмом. \n[!] Скрипт останавливается. \n[!] Попробуйте снова через некоторое время.")
            fail_invited_users.append(user)
            with open("telegram/last_user.json", "w") as json_file:
                decoded_json["invite"][tables_list[table_title][0]] = user['id']
                json.dump(decoded_json, json_file)
            break
        except UserPrivacyRestrictedError:
            print("[!] Настройки приватности пользователя не позволяют отправить ему приглашение. Пропускаем...")
            with open("telegram/last_user.json", "w") as json_file:
                decoded_json["invite"][tables_list[table_title][0]] = user['id']
                json.dump(decoded_json, json_file)
            fail_invited_users.append(user)
        except sqlite3.OperationalError:
            print("[!] Не удалось подключится к базе данных. Пропускаем...")
            fail_invited_users.append(user)
        except ChatWriteForbiddenError:
            print("[!] Вы не можете приглашать в этот канал. ")
            fail_invited_users.append(user)
        except:
            traceback.print_exc()
            fail_invited_users.append(user)
            print("[!] Неожиданная ошибка. Продолжаем...")

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['telegram']['invited'][phone] = invite_count
        json.dump(stats_decoded_json, stats_json_file)

    print("\nПользователи приглашены! \nВсего пользователей приглашено:{}/{}".format(len(invited_users), len(users)))
    print("Не удалось пригласить: {}/{}".format(len(fail_invited_users), len(users)))
