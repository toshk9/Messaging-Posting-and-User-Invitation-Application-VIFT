import configparser
import os, sys 


def add_account():
    dir_list = os.listdir(path="accounts/instagram_accs")
    cpass = configparser.RawConfigParser()
    cpass.add_section('cred')
    username = input("Введите логин : ")
    cpass.set('cred', 'username', username)
    password = input("Введите пароль : ")
    cpass.set('cred', 'password', password)
    try:
        new_dir = "accounts/instagram_accs/account_{}".format(int(dir_list[-1].split("_")[1]) + 1)
    except:
        new_dir = "accounts/instagram_accs/account_1"
    os.mkdir(new_dir)
    with open(f'{new_dir}/config.data', 'w') as setup:
	    cpass.write(setup)
    print("Аккаунт добавлен!")

def get_accounts():
    dir_list = os.listdir(path="accounts/instagram_accs")
    cpass = configparser.RawConfigParser()
    for direct in enumerate(dir_list):
        acc_dir = direct[1]
        cpass.read(f'accounts/instagram_accs/{acc_dir}/config.data')
        username = cpass['cred']['username']
        print(f"[{direct[0]}] - {direct[1]} ({username}) ")
    if len(dir_list) != 0:
        print("\nВыберите аккаунт для входа.")
        acc_num = int(input("Введите номер аккаунта: "))
        acc_title = dir_list[acc_num]
        return acc_title
    else:
        print("\nДобавьте аккаунт.")
        sys.exit()


