from .account import get_accounts, login
import sys
import random
import time
import vk
import configparser
from .get_users import get_friends
import json


def invite():
    acc_title = get_accounts()
    vk_api = login(acc_title, 'friends, groups, stats, wall, messages')
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    my_user_id = cpass['cred']['id']
    username = cpass['cred']['username']

    with open('stats.json') as stats_json_file:
        stats_decoded_json = json.load(stats_json_file)
    try:
        invite_count = stats_decoded_json['vk']['invited'][username]
    except KeyError:
        invite_count = 0

    group_id = int(input("\nВведите id группы, куда Вы хотите пригласить пользователей: "))

    print("\n[1] - пригласить в группу друзей.\n[2] - пригласить в группу неприглашенных друзей.")
    mode = int(input("\nВведите номер: "))

    users = get_friends(vk_api, my_user_id, "all")

    if mode == 2:
        for user in users:
            if user in vk_api.groups.getInvites()['items']:
                users.remove(user)
                
    friends_num = len(users)
    users_to_send_num = input(f"\nВведите число пользователей, которых Вы хотите пригласить в группу.\nВсего пользователей {friends_num}.\nВведите \"all\", если Вы хотите пригласить в группу всех друзей: ")
    if users_to_send_num != "all":
        del users[int(users_to_send_num):]

    succ_invited_users = []
    fail_invited_users = []
    for user in users:
        try:
            print(f"\nОтправка приглашения пользователю: {user}") 
            vk_api.groups.invite(group_id=group_id, user_id=user)
            print("{}/{} пользователей получило приглашение в группу.".format(len(succ_invited_users), len(users)))
            invite_count += 1
            print("Подождите 1-30 секунд")
            time.sleep(random.randint(1,30))
        except vk.exceptions.VkAPIError as err:
            print(f"Не удалось пригласить пользователя в группу.\nОшибка: {err}.\nПропускаем...")
            print("Подождите 1-10 секунд")
            time.sleep(random.randint(1,10))
            continue

    with open('stats.json', 'w') as stats_json_file:
        stats_decoded_json['vk']['invited'][username] = invite_count
        json.dump(stats_decoded_json, stats_json_file)

    print("\nГотово. Приглашение было отправлено {}/{} пользователям.".format(len(succ_invited_users), len(users)))
    print("Не удалось отправить приглашение {}/{} пользователям".format(len(fail_invited_users), len(users)))