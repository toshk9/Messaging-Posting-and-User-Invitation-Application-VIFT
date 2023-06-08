import vk
import os, sys
import configparser
import time 
from selenium import webdriver


def get_access_token_user_id(email, password):
    try:
        browser = webdriver.Chrome()
        browser.get('https://oauth.vk.com/authorize?client_id=6121396&scope=501202911&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1')
        browser.implicitly_wait(8)

        username_input = browser.find_element_by_css_selector("input[name='email']")
        password_input = browser.find_element_by_css_selector("input[name='pass']")


        username_input.send_keys(email)
        time.sleep(1)
        password_input.send_keys(password)
        time.sleep(2)

        login_button = browser.find_element_by_xpath("//button[@type='submit']")
        login_button.click()

        browser.implicitly_wait(180)

        permit_button = browser.find_element_by_xpath("//button[contains(@class,'button_indent')]")
        permit_button.click()

        browser.implicitly_wait(5)

        browser_url = browser.current_url
        time.sleep(2)
        browser.close()

        got_datas = browser_url.split('&')

        eaccess_token = got_datas[0].split('#')[1]
        access_token = eaccess_token.split('=')[1]
        user_id = got_datas[2].split('=')[1]

        return access_token, user_id
    except:
        print("\nПроизошла ошибка при получении access token и user id.\nПопробуйте снова.")
        sys.exit()

def login(acc_title, scope):
    cpass = configparser.RawConfigParser()
    cpass.read(f'accounts/vk_accs/{acc_title}/config.data')
    username = cpass['cred']['username']
    access_token = cpass['cred']['access_token']
    try:
        session = vk.AuthSession(access_token=access_token, scope=scope)
        vk_api = vk.API(session, v='5.131')
        print(f"\nВход был выполнен в аккаунт с логином {username}.\n")
        return vk_api
    except KeyError:
        print("\n\n[!] Добавьте аккаунт!!\n")
        sys.exit()

def add_account():
    dir_list = os.listdir(path="accounts/vk_accs")
    cpass = configparser.RawConfigParser()
    cpass.add_section('cred')
    username = input("Введите логин/номер телефона: ")
    cpass.set('cred', 'username', username)
    password = input("Введите пароль: ")
    cpass.set('cred', 'password', password)
    print("\nПолучение access token и user id...")
    access_token, user_id = get_access_token_user_id(username, password)
    cpass.set('cred', 'access_token', access_token)
    cpass.set('cred', 'id', user_id)
    try:
        new_dir = "accounts/vk_accs/account_{}".format(int(dir_list[-1].split("_")[1]) + 1)
    except:
        new_dir = "accounts/vk_accs/account_1"
    os.mkdir(new_dir)
    with open(f'{new_dir}/config.data', 'w') as setup:
	    cpass.write(setup)
    print("\nАккаунт добавлен!")

def get_accounts():
    dir_list = os.listdir(path="accounts/vk_accs")
    cpass = configparser.RawConfigParser()
    for direct in enumerate(dir_list):
        acc_dir = direct[1]
        cpass.read(f'accounts/vk_accs/{acc_dir}/config.data')
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