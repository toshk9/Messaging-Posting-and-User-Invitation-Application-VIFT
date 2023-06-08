import os, shutil
import configparser
from .check_spam import dates_list


def delete_account():
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

    print("\nВыберите аккаунты для удаления.")
    acc_nums = input("Введите номера аккаунтов через пробел: ").split(" ")
    for acc_num in acc_nums:    
        shutil.rmtree(f'accounts/telegram_accs/{dir_list[int(acc_num)]}')
    print("\nАккаунт успешно удален!")