import time, datetime
import os, sys, shutil
import configparser
import json, sqlite3
import requests
import vk
from VK import account as accounts_vk
from VK import post as post_vk
from VK import stories as stories_vk
from VK import send_message as sms_vk
from VK import parse as parse_vk
from VK import invite as invite_vk
from VK import friends as friends_vk
from instagram import account as accounts_inst
from instagram import post as post_inst
from instagram import stories as stories_inst
from instagram import send_message as sms_inst
from instagram import parse as parse_inst
from instagram import follow_unfollow as follow_inst
from telegram import delete_acc, utilits as accounts_tg
from telegram import smsbot as sms_tg
from telegram import parse as parse_tg
from telegram import invite as invite_tg
from telegram import check_spam
from telegram import change_ip
from telegram import delete_acc


def get_cur_acc(my_user_id):
    listdirff = os.listdir("accounts/vk_accs")
    for dirr in listdirff:
        cpass = configparser.RawConfigParser()
        cpass.read(f'accounts/vk_accs/{dirr}/config.data')
        owner_id = cpass['cred']['id']
        if owner_id == my_user_id:
            return dirr
        else:
            continue

def get_planned_posts():
    while True:
        with sqlite3.connect('VK/planned_posts_vk.db') as db:
            cursor = db.cursor()
            try:
                cursor.execute(""" SELECT * FROM planned_posts """)
            except:
                print("\nВ базе данных нет запланированных постов.")
                time.sleep(2)
                break
            posts_data = cursor.fetchall()
            db.commit()
            if len(posts_data) != 0:
                print("\nЗапланированные посты ВК: ")
                for post_data in enumerate(posts_data):
                    date = post_data[1][0]
                    ptime = post_data[1][1]
                    content = post_data[1][2]
                    owner_id = post_data[1][4]
                    if len(str(content)) > 50:
                        print(f"[{post_data[0]}] - {date}, {ptime} [{owner_id}] : \"{content[:50]}...\" ")
                    else:
                        print(f"[{post_data[0]}] - {date}, {ptime} [{owner_id}] : \"{content}\" ")
            else:
                print("\nЗапланированные посты ВК отсутствуют.")
                break 
            print("\n[0] - развернуть пост;\n[1] - редактировать отложенный пост;\n[2] - назад.")
            user_solution_post = int(input("\nВведите номер: "))
            if user_solution_post == 0:
                for post_data in enumerate(posts_data):
                    date = post_data[1][0]
                    ptime = post_data[1][1]
                    content = post_data[1][2]
                    owner_id = post_data[1][4]
                    if len(str(content)) > 50:
                        print(f"[{post_data[0]}] - {date}, {ptime} [{owner_id}] : \"{content[:50]}...\" ")
                    else:
                        print(f"[{post_data[0]}] - {date}, {ptime} [{owner_id}] : \"{content}\" ")
                
                us_post_num = int(input("\nВведите номер поста, чтобы его развернуть: "))
                cur_date = posts_data[us_post_num][0]
                cur_time = posts_data[us_post_num][1]
                cur_content = posts_data[us_post_num][2]
                cur_post_id = posts_data[us_post_num][3]
                cur_owner_id  = posts_data[us_post_num][4]
                print(f"{cur_date}, {cur_time} [{cur_owner_id}] : \"{cur_content}\" \nid поста: {cur_post_id}")
                input("\nНажмите Enter, чтобы вернуться назад.")
            elif user_solution_post == 1:
                for post_data in enumerate(posts_data):
                    date = post_data[1][0]
                    ptime = post_data[1][1]
                    content = post_data[1][2]
                    owner_id = post_data[1][4]
                    if len(str(content)) > 50:
                        print(f"[{post_data[0]}] - {date}, {ptime} [{owner_id}] : \"{content[:50]}...\" ")
                    else:
                        print(f"[{post_data[0]}] - {date}, {ptime} [{owner_id}] : \"{content}\" ")
                
                us_post_num = int(input("\nВведите номер поста, чтобы его редактировать: "))

                cur_post_id = posts_data[us_post_num][3]
                cur_owner_id  = posts_data[us_post_num][4]
                cur_acc_title = get_cur_acc(cur_owner_id)

                vk_api = accounts_vk.login(cur_acc_title, 'friends, groups, stats, wall, messages')

                cur_cpass = configparser.RawConfigParser()
                cur_cpass.read(f'accounts/vk_accs/{cur_acc_title}/config.data')
                username = cur_cpass['cred']['username']

                with open('stats.json') as stats_json_file:
                    stats_decoded_json = json.load(stats_json_file)
                try:
                    post_count = stats_decoded_json['vk']['posted'][username]
                except KeyError:
                    post_count = 0

                print("Прикрепить видео или фото к публикации?\n")
                mode_2 = input("y/n: ")
                if mode_2 == "y":
                    print("[0] - Фото;\n[1] - Видео.")
                    v_or_photo = int(input("\nВведите номер: "))
                    if v_or_photo == 0:
                        upload_date = input("Введите дату размещения записи в формате 31.12.1999: ").split(".")
                        upload_hm = input("Введите время размещения записи в формате 23:59: ").split(":")

                        upload_time = f"{upload_date[0]}/{upload_date[1]}/{upload_date[2]}/{upload_hm[0]}/{upload_hm[1]}"
                        try:
                            timestamp = time.mktime(datetime.strptime(upload_time, "%d/%m/%Y/%H/%M").timetuple())
                            s_date = f"{upload_date[0]}.{upload_date[1]}.{upload_date[2]}"
                            s_time = f"{upload_hm[0]}:{upload_hm[1]}"
                        except ValueError:
                            print("Неправильно введено время публикации!")
                            sys.exit()

                        filename = f'resources/{post_vk.get_file()}'
                        message = input("\nВведите текст, который будет прикреплен к записи. Нажмите Enter, чтобы пропустить: ")
                        
                        try:
                            upload_url = vk_api.photos.getWallUploadServer()['upload_url']
                            resp = requests.post(upload_url, files = {'file': open(filename, 'rb')}).json()
                            s = vk_api.photos.saveWallPhoto(server = resp['server'], photo=resp['photo'], hash = resp['hash'])
                            post_id = vk_api.wall.edit(post_id=cur_post_id, owner_id = cur_owner_id, message=message, attachments=f"photo{s[0]['owner_id']}_{s[0]['id']}", publish_date=timestamp)['post_id']
                            post_vk.save_post(s_date, s_time, message + " + " + filename, post_id, cur_owner_id)
                            post_count += 1
                            print("Запись успешно опубликована!")
                        except vk.exceptions.VkAPIError as err:
                            if err.code == 29:
                                print("Превышен лимит запросов в сутки.")   
                            elif err.code == 5:
                                print("Пользователь заблокирован. Публикация невозможна.")       
                            else:
                                print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
                        
                    elif v_or_photo == 1:
                        upload_date = input("Введите дату размещения записи в формате 31.12.1999: ").split(".")
                        upload_hm = input("Введите время размещения записи в формате 23:59: ").split(":")

                        upload_time = f"{upload_date[0]}/{upload_date[1]}/{upload_date[2]}/{upload_hm[0]}/{upload_hm[1]}"
                        try:
                            timestamp = time.mktime(datetime.strptime(upload_time, "%d/%m/%Y/%H/%M").timetuple())
                            s_date = f"{upload_date[0]}.{upload_date[1]}.{upload_date[2]}"
                            s_time = f"{upload_hm[0]}:{upload_hm[1]}"
                        except ValueError:
                            print("Неправильно введено время публикации!")
                            sys.exit()

                        filename = f'resources/{post_vk.get_file()}'
                        message = input("\nВведите текст, который будет прикреплен к записи. Нажмите Enter, чтобы пропустить: ")
                        
                        try:
                            upload_url = vk_api.video.save()['upload_url']
                            resp = requests.post(upload_url, files = {'video_file': open(filename, 'rb')}).json()
                            post_id = vk_api.wall.edit(post_id=cur_post_id, owner_id = cur_owner_id, message=message, attachments=f"video{resp['owner_id']}_{resp['video_id']}", publish_date=timestamp)['post_id']
                            post_vk.save_post(s_date, s_time, message + " + " + filename, post_id, cur_owner_id)
                            post_count += 1
                            print("Запись успешно опубликована!")
                        except vk.exceptions.VkAPIError as err:
                            if err.code == 29:
                                print("Превышен лимит запросов в сутки.")   
                            elif err.code == 5:
                                print("Пользователь заблокирован. Публикация невозможна.")       
                            else:
                                print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")
                elif mode_2 == "n":
                    upload_date = input("Введите дату размещения записи в формате 31.12.1999: ").split(".")
                    upload_hm = input("Введите время размещения записи в формате 23:59: ").split(":")

                    upload_time = f"{upload_date[0]}/{upload_date[1]}/{upload_date[2]}/{upload_hm[0]}/{upload_hm[1]}"
                    try:
                        timestamp = time.mktime(datetime.strptime(upload_time, "%d/%m/%Y/%H/%M").timetuple())
                        s_date = f"{upload_date[0]}.{upload_date[1]}.{upload_date[2]}"
                        s_time = f"{upload_hm[0]}:{upload_hm[1]}"
                    except ValueError:
                        print("Неправильно введено время публикации!")
                        sys.exit()
                    message = input("\nВведите текст поста: ") 
                    try:
                        post_id = vk_api.wall.edit(post_id=cur_post_id, owner_id = cur_owner_id, message=message, publish_date=timestamp)['post_id']
                        post_vk.save_post(s_date, s_time, message, post_id, cur_owner_id)
                        post_count += 1
                        print("Запись успешно опубликована!")
                    except vk.exceptions.VkAPIError as err:
                        if err.code == 29:
                            print("Превышен лимит запросов в сутки.")   
                        elif err.code == 5:
                            print("Пользователь заблокирован. Публикация невозможна.")       
                        else:
                            print("\nНе удалось опубликовать пост. Попробуйте снова через некоторый промежуток времени.")


                with open('stats.json', 'w') as stats_json_file:
                    stats_decoded_json['vk']['posted'][username] = post_count
                    json.dump(stats_decoded_json, stats_json_file)

            elif user_solution_post == 2:
                break

while True:
    print("""\nВведите: \n\n\"add\", чтобы добавить новый аккаунт;\n\"post\", чтобы опубликовать пост на странице аккаунта;\n\"story\", чтобы опубликовать сторис;\n\"parse\", чтобы собрать пользователей;\n\"invite\", чтобы пригласить пользователей в группу, добавить в друзья, подписаться и др;\n\"sms\", чтобы отправить сообщение пользователям;\n\"stats\", чтобы посмотреть статистику;\n\"del stats\", чтобы обнулить статистику;\n\"ip\", чтобы изменить ip аккаунта telegram;\n\"check accounts\", чтобы проверить доступ к аккаунтам telegram;\n\"delete\", чтобы удалить аккаунт;\n\"exit\", чтобы выйти.\n""")
    user_solution = str(input())
    if user_solution == "add":
        socmeds = ["VK", "Instagram", "Facebook", "Telegram"]
        print("\nК какой социальной сети Вы хотите добавить аккаунт?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            accounts_vk.add_account()
            time.sleep(2)
        elif socmed == "Instagram":
            accounts_inst.add_account()
            time.sleep(2)
        elif socmed == "Telegram":
            accounts_tg.add_account()
            time.sleep(2)
        elif socmed == "Facebook":
            print("{<[]>} В РАЗРАБОТКЕ {<[]>}")
            time.sleep(2)

    elif user_solution == "post":
        socmeds = ["VK", "Instagram", "Facebook"]
        print("\nВ какой социальной сети Вы хотите опубликовать пост?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            print("\n[0] - опубликовать пост;\n[1] - посмотреть отложенные посты.")
            us_sol_pos = int(input("\nВведите номер: "))
            if us_sol_pos == 0:
                post_vk.post()
                time.sleep(2)
            elif us_sol_pos:
                get_planned_posts()
                time.sleep(1)
        elif socmed == "Instagram":
            post_inst.post()
            time.sleep(2)
        elif socmed == "Facebook":
            print("{<[]>} В РАЗРАБОТКЕ {<[]>}")
            time.sleep(2)
            
    elif user_solution == "story":
        socmeds = ["VK", "Instagram"]
        print("\nВ какой социальной сети Вы хотите опубликовать сторис?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            stories_vk.stories()
            time.sleep(2)
        elif socmed == "Instagram":
            stories_inst.stories()
            time.sleep(2)

    elif user_solution == "parse":
        socmeds = ["VK", "Instagram", "Telegram"]
        print("\nВ какой социальной сети Вы хотите собрать пользователей?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            parse_vk.parse()
            time.sleep(2)
        elif socmed == "Instagram":
            parse_inst.parse()
            time.sleep(2)
        elif socmed == "Telegram":
            parse_tg.parse()
            time.sleep(2)

    elif user_solution == "invite":
        socmeds = ["VK", "Instagram", "Telegram"]
        print("\nВ какой социальной сети Вы хотите пригласить, добавить в друзья пользователей или подписаться на них?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            print("Что Вы хотите сделать?\n[0] - пригласить пользователей в группу;\n[1] - добавить пользователей в друзья;\n[2] - удалить пользователей из списка друзей.")
            vk_invite_mode = int(input("Введите номер: "))
            if vk_invite_mode == 0:
                invite_vk.invite()
                time.sleep(2)
            elif vk_invite_mode == 1:
                friends_vk.add_friends()
                time.sleep(2)
            elif vk_invite_mode == 2:
                friends_vk.delete_friends()
                time.sleep(2)
            else:
                print("Неправильная настройка!")
                time.sleep(2)
        elif socmed == "Instagram":
            print("Что Вы хотите сделать?\n[0] - подписаться на пользователей;\n[1] - отписаться от пользователей.")
            inst_follow_mode = int(input("Введите номер: "))
            if inst_follow_mode == 0:
                follow_inst.follow()
                time.sleep(2)
            elif inst_follow_mode == 1:
                follow_inst.unfollow()
                time.sleep(2)
            else:
                print("Неправильная настройка!")
                time.sleep(2)
        elif socmed == "Telegram":
            invite_tg.invite()
            time.sleep(2)

    elif user_solution == "sms":
        socmeds = ["VK", "Instagram", "Telegram"]
        print("\nВ какой социальной сети Вы хотите отправить сообщение?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            sms_vk.send_message()
            time.sleep(2)
        elif socmed == "Instagram":
            sms_inst.send_message()
            time.sleep(2)
        elif socmed == "Telegram":
            sms_tg.sms()
            time.sleep(2)
    
    elif user_solution == "stats":
        with open('stats.json') as stats_json_file:
            stats_decoded_json = json.load(stats_json_file)

        vk_posts = stats_decoded_json['vk']['posted']
        vk_stories = stats_decoded_json['vk']['stories']
        vk_invited = stats_decoded_json['vk']['invited']
        vk_sended = stats_decoded_json['vk']['sended']
        vk_friends = stats_decoded_json['vk']['friends']

        inst_posts = stats_decoded_json['instagram']['posted']
        inst_stories = stats_decoded_json['instagram']['stories']
        inst_follow = stats_decoded_json['instagram']['followed']
        inst_sended = stats_decoded_json['instagram']['sended']

        tg_invited = stats_decoded_json['telegram']['invited']
        tg_sended = stats_decoded_json['telegram']['sended']

        fb_posted = stats_decoded_json['facebook']['posted']
        fb_stories = stats_decoded_json['facebook']['stories']

        ### VK ###
        print("")
        print("     [VK]")
        print("")
        print("Отправлено сообщений:\n")
        if len(vk_sended.items()) == 0:
            print("0")
        else:
            for i in vk_sended.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nОтправлено приглашений в группу:\n")
        if len(vk_invited.items()) == 0:
            print("0")
        else:
            for i in vk_invited.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nОтправлено заявок в друзья:\n")
        if len(vk_friends.items()) == 0:
            print("0")
        else:
            for i in vk_friends.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nСделано постов:\n")
        if len(vk_posts.items()) == 0:
            print("0")
        else:
            for i in vk_posts.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nСделано сторис:\n")
        if len(vk_stories.items()) == 0:
            print("0")
        else:
            for i in vk_stories.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")

        ### INSTAGRAM ###
        print("")
        print("     [INSTAGRAM]")
        print("")
        print("Отправлено сообщений:\n")
        if len(inst_sended.items()) == 0:
            print("0")
        else:
            for i in inst_sended.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nСделано подписок:\n")
        if len(inst_follow.items()) == 0:
            print("0")
        else:
            for i in inst_follow.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nСделано постов:\n")
        if len(inst_posts.items()) == 0:
            print("0")
        else:
            for i in inst_posts.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nСделано сторис:\n")
        if len(inst_stories.items()) == 0:
            print("0")
        else:
            for i in inst_stories.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")

        ### TELEGRAM ###
        print("")
        print("     [TELEGRAM]")
        print("")
        print("Отправлено сообщений:\n")
        if len(tg_sended.items()) == 0:
            print("0")
        else:
            for i in tg_sended.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nОтправлено приглашений в группу:\n")
        if len(tg_invited.items()) == 0:
            print("0")
        else:
            for i in tg_invited.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")

        ### FACEBOOK ###
        print("")
        print("     [FACEBOOK]")
        print("")
        print("Сделано постов:\n")
        if len(fb_posted.items()) == 0:
            print("0")
        else:
            for i in fb_posted.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        print("\nСделано сторис:\n")
        if len(fb_stories.items()) == 0:
            print("0")
        else:
            for i in fb_stories.items():
                print(f"аккаунт ({i[0]}) - {i[1]}")
        
        enter = input("\nНажмите Enter, чтобы продолжить.")
        time.sleep(1)

    elif user_solution == "del stats":
        print("\nВы уверены, что хотите сбросить все данные статистики?")
        us_dels = input("y/n: ")
        if us_dels == "y":
            new_stats_json = {'facebook': {'posted': {}, 'stories': {}}, 'vk': {'posted': {}, 'stories': {}, 'invited': {}, 'sended': {}, 'friends': {}}, 'instagram': {'posted': {}, 'stories': {}, 'followed': {}, 'sended': {}}, 'telegram': {'invited': {}, 'sended': {}}}

            with open('stats.json', 'w') as cr_json_file:
                json.dump(new_stats_json, cr_json_file)
            print("\nСтатистика успешно сброшена.")  
            time.sleep(3)
    elif user_solution == "change ip":
        change_ip.change_ip()
        time.sleep(2)
    elif user_solution == "check accounts":
        dir_list = os.listdir(path="accounts/telegram_accs")
        dates_list = check_spam.dates_list()
        cpass = configparser.RawConfigParser()
        print("\nСписок аккаунтов: \n")
        for direct in enumerate(dir_list):
            acc_dir = direct[1]
            cpass.read('accounts/telegram_accs/{}/config.data'.format(acc_dir))
            phone = cpass['cred']['phone']
            lim_status = dates_list[int(dir_list.index(direct[1]))]
            if lim_status != "[+]":
                print(f"аккаунт: [{direct[0]}] - {direct[1]} ({phone}) " + "[-]" + f" Дата разблокировки: {lim_status}")
            else:
                print(f"аккаунт: [{direct[0]}] - {direct[1]} ({phone}) {lim_status}")
        
        enter = input("\nНажмите Enter, чтобы продолжить.")
        time.sleep(1)
    elif user_solution == "delete":
        socmeds = ["VK", "Instagram", "Facebook", "Telegram"]
        print("\nАккаунт какой социальной сети Вы хотите удалить?")
        for socmed in enumerate(socmeds):
            print(f"[{socmed[0]}] - {socmed[1]}")
        socmed_num = int(input("\nВведите номер: "))
        socmed = socmeds[socmed_num]
        if socmed == "VK":
            dir_list = os.listdir(path="accounts/vk_accs")
            cpass = configparser.RawConfigParser()
            for direct in enumerate(dir_list):
                acc_dir = direct[1]
                cpass.read(f'accounts/vk_accs/{acc_dir}/config.data'.format(acc_dir))
                username = cpass['cred']['username']
                print(f"аккаунт: [{direct[0]}] - {direct[1]} ({username})")

            print("\nВыберите аккаунты для удаления.")
            acc_nums = input("Введите номера аккаунтов через пробел: ").split(" ")
            for acc_num in acc_nums:    
                shutil.rmtree(f'accounts/vk_accs/{dir_list[int(acc_num)]}')
            print("\nАккаунт успешно удален!")
            time.sleep(2)
        elif socmed == "Instagram":
            dir_list = os.listdir(path="accounts/instagram_accs")
            cpass = configparser.RawConfigParser()
            for direct in enumerate(dir_list):
                acc_dir = direct[1]
                cpass.read(f'accounts/instagram_accs/{acc_dir}/config.data'.format(acc_dir))
                username = cpass['cred']['username']
                print(f"аккаунт: [{direct[0]}] - {direct[1]} ({username})")

            print("\nВыберите аккаунты для удаления.")
            acc_nums = input("Введите номера аккаунтов через пробел: ").split(" ")
            for acc_num in acc_nums:    
                shutil.rmtree(f'accounts/instagram_accs/{dir_list[int(acc_num)]}')
            print("\nАккаунт успешно удален!")
            time.sleep(2)
        elif socmed == "Facebook":
            print("{<[]>} В РАЗРАБОТКЕ {<[]>}")
            time.sleep(2)
        elif socmed == "Telegram":
            delete_acc.delete_account()
            time.sleep(2)
    
    elif user_solution == "exit":
        break
    else:
        print("\nНеправильный ввод пользователя!\n")
        time.sleep(2)