import os
from .check_spam import dates_list
import configparser


def change_ip():
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

    print("\nВыберите аккаунт для смены ip.")
    acc_title = int(input("Введите номер аккаунта: "))
    
    cpass.read(f'accounts/telegram_accs/{dir_list[acc_title]}/config.data')

    ip = (input("\nВведите новый ip: "))
    port = (input("\nВведите новый порт: "))
    
    cpass["cred"]["ip"] = ip
    cpass["cred"]["port"] = port

    with open(f'accounts/telegram_accs/{dir_list[acc_title]}/config.data', 'w') as setup:
        cpass.write(setup)

    print("\nip успешно изменен!")

