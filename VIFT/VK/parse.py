from .account import get_accounts, login
import sys
import vk
import configparser, sqlite3
import time
from .get_users import get_members, get_friends

def parse():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')

    print("\n[1] - собрать подписчиков своей группы;\n[2] - собрать подписчиков другой группы;\n[3] - собрать друзей своей страницы;\n[4] - собрать друзей другой страницы")
    mode = int(input("Введите номер: "))
    if mode == 1:
        user_id = cpass['cred']['id']
        groups = vk_api.groups.get(user_id=user_id, filter='admin', extended=1)['items']
        if len(groups) > 1:
            print("\nВыберите группу для сбора подписчиков: ")
            for group in enumerate(groups):
                group_name = group[1]['name']
                group_num = group[0]
                print(f"[{group_num}] - {group_name}")
            group_num_inp = input("\nВведите номер группы.\nВведите \"all\", если хотите собрать подписчиков со всех доступных групп: ")
            if group_num_inp != "all":
                group = groups[int(group_num_inp)]
                group_id = group['id']
                group_name = group['name']
                members_amount = vk_api.groups.getMembers(group_id=group_id)['count']
                print(f"Сбор подписчиков с группы {group_name}...")
                users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего подписчиков: {members_amount}.\nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
                members = get_members(vk_api=vk_api, group_id=group_id, total_count=users_to_parse_num)
                with sqlite3.connect('VK/vk.db') as db:
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
                    cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, user_id INTEGER, link TEXT, friends_amount INTEGER, medias_amount INTEGER, group_title TEXT, group_id INTEGER) """.format(table_title))
                    for member in members:
                        list_id = int(members.index(member)) + 1
                        member_id = member
                        group_title = group_name
                        group_id = group_id
                        link = f"vk.com/id{member_id}"
                        try:
                            friends_amount = int(vk_api.friends.get(user_id=member_id)['count'])
                            medias_amount = int(vk_api.wall.get(owner_id=member_id)['count'])
                        except:
                            friends_amount = 0
                            medias_amount = 0

                        cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, member_id))
                        if cursor.fetchone()[0] == 0:
                            user_data = (list_id, member_id, link, friends_amount, medias_amount, group_title, group_id)
                            cursor.execute(""" INSERT INTO {} (list_id, user_id, link, friends_amount, medias_amount, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                            parserd_users.append(member_id)
                            print("{}/{} пользователей собрано".format(len(parserd_users), len(members)))
                        else:
                            print("Пользователь уже есть в таблице.")
                            fail_parsed_users.append(member_id)
                            continue
                        db.commit()
                    print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(members), table_title))
                    print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(members), table_title))
            else:
                for group in groups:
                    group_name = group['name']
                    group_id = group['id']
                    print(f"Сбор подписчиков с группы {group_name}...")
                    members_amount = vk_api.groups.getMembers(group_id=group_id)['count']
                    users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего подписчиков: {members_amount}.\nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
                    members = get_members(vk_api=vk_api, group_id=group_id, total_count=users_to_parse_num)
                    with sqlite3.connect('VK/vk.db') as db:
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
                        cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, user_id INTEGER, link TEXT, friends_amount INTEGER, medias_amount INTEGER, group_title TEXT, group_id INTEGER) """.format(table_title))
                        for member in members:
                            list_id = int(members.index(member)) + 1
                            member_id = member
                            group_title = group_name
                            group_id = group_id
                            link = f"vk.com/id{member_id}"
                            try:
                                friends_amount = int(vk_api.friends.get(user_id=member_id)['count'])
                                medias_amount = int(vk_api.wall.get(owner_id=member_id)['count'])
                            except:
                                friends_amount = 0
                                medias_amount = 0

                            cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, member_id))
                            if cursor.fetchone()[0] == 0:
                                user_data = (list_id, member_id, link, friends_amount, medias_amount, group_title, group_id)
                                cursor.execute(""" INSERT INTO {} (list_id, user_id, link, friends_amount, medias_amount, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                                parserd_users.append(member_id)
                                print("{}/{} пользователей собрано".format(len(parserd_users), len(members)))
                            else:
                                print("Пользователь уже есть в таблице.")
                                fail_parsed_users.append(member_id)
                                continue
                            db.commit()
                        print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(members), table_title))
                        print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(members), table_title))
        else:
            try:
                group = groups[0]
            except IndexError:
                print("\nДанный аккаунт не имеет группы!\n")
                sys.exit()
            group_name = group['name']
            group_id = group['id']
            print(f"Сбор подписчиков с группы {group_name}...")
            members_amount = vk_api.groups.getMembers(group_id=group_id)['count']
            users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего подписчиков: {members_amount}.\nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
            members = get_members(vk_api=vk_api, group_id=group_id, total_count=users_to_parse_num)
            with sqlite3.connect('VK/vk.db') as db:
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
                cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, user_id INTEGER, link TEXT, friends_amount INTEGER, medias_amount INTEGER, group_title TEXT, group_id INTEGER) """.format(table_title))
                for member in members:
                    list_id = int(members.index(member)) + 1
                    member_id = member
                    group_title = group_name
                    group_id = group_id
                    link = f"vk.com/id{member_id}"
                    try:
                        friends_amount = int(vk_api.friends.get(user_id=member_id)['count'])
                        medias_amount = int(vk_api.wall.get(owner_id=member_id)['count'])
                    except:
                        friends_amount = 0
                        medias_amount = 0

                    cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, member_id))
                    if cursor.fetchone()[0] == 0:
                        user_data = (list_id, member_id, link, friends_amount, medias_amount, group_title, group_id)
                        cursor.execute(""" INSERT INTO {} (list_id, user_id, link, friends_amount, medias_amount, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                        parserd_users.append(member_id)
                        print("{}/{} пользователей собрано".format(len(parserd_users), len(members)))
                    else:
                        print("Пользователь уже есть в таблице.")
                        fail_parsed_users.append(member_id)
                        continue
                    db.commit()
                print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(members), table_title))
                print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(members), table_title))
    elif mode == 2:
        group_id = input("\nВведите id или короткое имя группы, откуда Вы хотите собрать подписчиков: ")
        try:
            group_id = int(group_id)
        except:
            group_id = str(group_id)
        print(f"Сбор подписчиков с группы {group_id}...")
        members_amount = vk_api.groups.getMembers(group_id=group_id)['count']
        users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего подписчиков: {members_amount}.\nВведите \"all\", если Вы хотите спарсить всех пользователей группы: ")
        members = get_members(vk_api=vk_api, group_id=group_id, total_count=users_to_parse_num)
        
        with sqlite3.connect('VK/vk.db') as db:
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
            cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, user_id INTEGER, link TEXT, friends_amount INTEGER, medias_amount INTEGER, group_title TEXT, group_id INTEGER) """.format(table_title))
            for member in members:
                list_id = int(members.index(member)) + 1
                member_id = member
                group_title = None
                group_id = group_id
                link = f"vk.com/id{member_id}"
                try:
                    friends_amount = int(vk_api.friends.get(user_id=member_id)['count'])
                except:
                    friends_amount = 0
                try:
                    medias_amount = int(vk_api.wall.get(owner_id=member_id)['count'])
                except:
                    medias_amount = 0
                cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, member_id))
                if cursor.fetchone()[0] == 0:
                    user_data = (list_id, member_id, link, friends_amount, medias_amount, group_title, group_id)
                    cursor.execute(""" INSERT INTO {} (list_id, user_id, link, friends_amount, medias_amount, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                    parserd_users.append(member_id)
                    print("{}/{} пользователей собрано".format(len(parserd_users), len(members)))
                else:
                    print("Пользователь уже есть в таблице.")
                    fail_parsed_users.append(member_id)
                    continue
                db.commit()
            print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(members), table_title))
            print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(members), table_title))

    elif mode == 3:
        user_id = cpass['cred']['id']
        us_friends_amount = vk_api.friends.get(user_id=user_id)['count']
        users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего друзей: {us_friends_amount}.\nВведите \"all\", если Вы хотите спарсить всех друзей страницы: ")
        friends_list = get_friends(vk_api=vk_api, user_id=user_id, total_count=users_to_parse_num)
        with sqlite3.connect('VK/vk.db') as db:
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
            cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, user_id INTEGER, link TEXT, friends_amount INTEGER, medias_amount INTEGER, parsed_from_id INTEGER) """.format(table_title))
            for member in friends_list:
                list_id = int(friends_list.index(member)) + 1
                member_id = member
                parsed_from_id = user_id
                link = f"vk.com/id{member_id}"
                try:
                    friends_amount = int(vk_api.friends.get(user_id=member_id)['count'])
                except:
                    friends_amount = 0
                try:
                    medias_amount = int(vk_api.wall.get(owner_id=member_id)['count'])
                except:
                    medias_amount = 0
                cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, member_id))
                if cursor.fetchone()[0] == 0:
                    user_data = (list_id, member_id, link, friends_amount, medias_amount, parsed_from_id)
                    cursor.execute(""" INSERT INTO {} (list_id, user_id, link, friends_amount, medias_amount, parsed_from_id) VALUES(?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                    parserd_users.append(member_id)
                    print("{}/{} пользователей собрано".format(len(parserd_users), len(friends_list)))
                else:
                    print("Пользователь уже есть в таблице.")
                    fail_parsed_users.append(member_id)
                    continue
                db.commit()
            print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(friends_list), table_title))
            print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(friends_list), table_title))
    elif mode == 4:
        user_id = int(input("\nВведите id пользователя, у которого Вы хотите собрать друзей: "))
        try:
            us_friends_amount = vk_api.friends.get(user_id=user_id)['count']
        except vk.exceptions.VkAPIError as err:
            if err.code == 30:
                print("\nНастройки приватности пользователя не позволяют собрать его друзей.")
                sys.exit()
            else:
                print(f"\nНе удалось собрать друзей пользователя.\nОшибка: {err}")
        users_to_parse_num = input(f"\nУкажите число пользователей, которое Вы хотите спарсить.\nВсего друзей: {us_friends_amount}.\nВведите \"all\", если Вы хотите спарсить всех друзей страницы: ")
        friends_list = get_friends(vk_api=vk_api, user_id=user_id, total_count=users_to_parse_num)
        with sqlite3.connect('VK/vk.db') as db:
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
            cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, user_id INTEGER, link TEXT, friends_amount INTEGER, medias_amount INTEGER, parsed_from_id INTEGER) """.format(table_title))
            for member in friends_list:
                list_id = int(friends_list.index(member)) + 1
                member_id = member
                parsed_from_id = user_id
                link = f"vk.com/id{member_id}"
                try:
                    friends_amount = int(vk_api.friends.get(user_id=member_id)['count'])
                except:
                    friends_amount = 0
                try:
                    medias_amount = int(vk_api.wall.get(owner_id=member_id)['count'])
                except:
                    medias_amount = 0

                cursor.execute(""" SELECT COUNT( * ) FROM {} WHERE user_id='{}' """.format(table_title, member_id))
                if cursor.fetchone()[0] == 0:
                    user_data = (list_id, member_id, link, friends_amount, medias_amount, parsed_from_id)
                    cursor.execute(""" INSERT INTO {} (list_id, user_id, link, friends_amount, medias_amount, parsed_from_id) VALUES(?, ?, ?, ?, ?, ?) """.format(table_title), user_data)
                    parserd_users.append(member_id)
                    print("{}/{} пользователей собрано".format(len(parserd_users), len(friends_list)))
                else:
                    print("Пользователь уже есть в таблице.")
                    fail_parsed_users.append(member_id)
                    continue
                db.commit()
            print('\n\n{}/{} пользователей успешно собрано в таблицу {}'.format(len(parserd_users), len(friends_list), table_title))
            print('{}/{} пользователей уже есть в таблице {}'.format(len(fail_parsed_users), len(friends_list), table_title))
