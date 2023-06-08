from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os, sys
import configparser
import sqlite3
import time
import socks
from .check_spam import dates_list


def parse():
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
    print(f"[{int(len(dir_list))}] - все аккаунты")

    print("\nВыберите аккаунт для входа.")
    acc_title = int(input("Введите номер: "))

    if acc_title != int(len(dir_list)):
        cpass.read('accounts/telegram_accs/{}/config.data'.format(dir_list[acc_title]))

        try:
            api_id = cpass['cred']['id']
            api_hash = cpass['cred']['hash']
            phone = cpass['cred']['phone']
            ip = cpass['cred']['ip']
            port = cpass['cred']['port']
            client = TelegramClient(phone, api_id, api_hash, proxy=(socks.SOCKS4, ip, port))
            print("Вход был выполнен в аккаунт с номером {}".format(phone))
        except KeyError:
            print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py")
            sys.exit(1)

        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            client.sign_in(phone, input('Введите код, который придет на Ваш номер телефона: '))
        

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
        
        print('\nВыберите группу, пользователей с которой Вы хотите спарсить: ')
        i=0
        for g in groups:
            print(f'[{str(i)}] - ' + g.title)
            i+=1
        
        print('')
        g_index = input("Введите номер : ")
        target_group=groups[int(g_index)]
        
        print('\nСбор участников...\n')
        time.sleep(1)
        all_participants = []
        all_participants = client.get_participants(target_group, aggressive=True)
        users_to_parse_num = input(f"Укажите число пользователей, которое Вы хотите спарсить.\nВсего пользователей {len(all_participants)}.\nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
        if users_to_parse_num != "all":
            del all_participants[int(users_to_parse_num):]

        with sqlite3.connect('telegram/telegram.db') as db:
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
            cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, username TEXT, user_id INTEGER, access_hash TEXT, name TEXT, group_title TEXT, group_id INTEGER) """.format(table_title))
            for user in all_participants:
                list_id = int(all_participants.index(user)) + 1
                user_id = user.id
                access_hash = user.access_hash
                group_title = target_group.title
                group_id = target_group.id

                if user.username:
                    username = user.username
                else:
                    username = ""
                if user.first_name:
                    first_name = user.first_name
                else:
                    first_name = ""
                if user.last_name:
                    last_name = user.last_name
                else:
                    last_name = ""
                name = (first_name + ' ' + last_name).strip()
                
                cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}'""".format(table_title, user_id))
                if cursor.fetchone()[0] == 0:
                    user_data = (list_id, username, user_id, access_hash, name, group_title, group_id)
                    cursor.execute(""" INSERT INTO {} (list_id, username, user_id, access_hash, name, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                    parserd_users.append(user)
                    print("{}/{} пользователей собрано".format(len(parserd_users), len(all_participants)))
                else:
                    print("Пользователь уже есть в таблице.")
                    fail_parsed_users.append(user)
                    continue
                db.commit()
        print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(all_participants), table_title))
        print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(all_participants), table_title))
    else:
        for direct in dir_list:
            lim_status = dates_list[int(dir_list.index(direct))]
            if lim_status == "Аккаунт удален.":
                continue
            cpass.read('accounts/telegram_accs/{}/config.data'.format(direct))

            try:
                api_id = cpass['cred']['id']
                api_hash = cpass['cred']['hash']
                phone = cpass['cred']['phone']
                ip = cpass['cred']['ip']
                port = cpass['cred']['port']
                client = TelegramClient(phone, api_id, api_hash, proxy=(socks.SOCKS4, ip, port))
                print("\nВход был выполнен в аккаунт с номером {}".format(phone))
            except KeyError:
                print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py")
                sys.exit(1)

            client.connect()
            if not client.is_user_authorized():
                client.send_code_request(phone)
                client.sign_in(phone, input('Введите код, который придет на Ваш номер телефона: '))

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
            
            print('\n\nВыберите группу, пользователей с которой Вы хотите спарсить: ')
            i=0
            for g in groups:
                print(f'[{str(i)}] - ' + g.title)
                i+=1
            
            print('')
            g_index = input("Введите номер : ")
            target_group=groups[int(g_index)]
            
            print('\nСбор участников...\n')
            time.sleep(1)
            all_participants = []
            all_participants = client.get_participants(target_group, aggressive=True)
            users_to_parse_num = input("Укажите число пользователей, которое Вы хотите спарсить.\nВсего пользователей {len(all_participants)}. \nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
            if users_to_parse_num != "all":
                del all_participants[int(users_to_parse_num):]
                
            with sqlite3.connect('telegram/telegram.db') as db:
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
                    cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, username TEXT, user_id INTEGER, access_hash TEXT, name TEXT, group_title TEXT, group_id INTEGER) """.format(table_title))
                    for user in all_participants:
                        list_id = int(all_participants.index(user)) + 1
                        user_id = user.id
                        access_hash = user.access_hash
                        group_title = target_group.title
                        group_id = target_group.id

                        if user.username:
                            username = user.username
                        else:
                            username = ""
                        if user.first_name:
                            first_name = user.first_name
                        else:
                            first_name = ""
                        if user.last_name:
                            last_name = user.last_name
                        else:
                            last_name = ""
                        name = (first_name + ' ' + last_name).strip()
                        
                        cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}'""".format(table_title, user_id))
                        if cursor.fetchone()[0] == 0:
                            user_data = (list_id, username, user_id, access_hash, name, group_title, group_id)
                            cursor.execute(""" INSERT INTO {} (list_id, username, user_id, access_hash, name, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                            parserd_users.append(user)
                            print("{}/{} пользователей собрано.".format(len(parserd_users), len(all_participants)))
                        else:
                            print("Пользователь уже есть в таблице.")
                            fail_parsed_users.append(user)
                            continue
                        db.commit()
                    print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(all_participants), table_title))
                    print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(all_participants), table_title))

