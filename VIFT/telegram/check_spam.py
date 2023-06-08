
from telethon.sync import TelegramClient
import configparser
import sys, os 
import socks  

def dates_list():
    dir_list = os.listdir(path="accounts/telegram_accs")
    dates_list = []
    for direct in dir_list:
        try:
            cpass = configparser.RawConfigParser()
            cpass.read('accounts/telegram_accs/{}/config.data'.format(direct))
            api_id = cpass['cred']['id']
            api_hash = cpass['cred']['hash']
            phone = cpass['cred']['phone']
            ip = cpass['cred']['ip']
            port = cpass['cred']['port']
        except KeyError:
            print("\n\n[!] Добавьте аккаунт!!\nВведите \"add\" после запуска main.py\n")
            sys.exit(1)

        client = TelegramClient(phone, api_id, api_hash, proxy=(socks.SOCKS4, ip, port))
        client.connect()

        if not client.is_user_authorized():
            try:
                client.send_code_request(phone)
                client.sign_in(phone, input(f'Введите код, который придет на номер {phone}: '))
            except:
                dates_list.append("Аккаунт удален.")
                continue

        receiver = client.get_input_entity("SpamBot")
        client.send_message(receiver, "/start")

        dialog_title = ""
        for dialog in client.iter_dialogs():
            dialog_title = dialog.title
            break

        response_message = ""
        for message in client.iter_messages(dialog_title):
            response_message = message.text
            break

        unlimited_date = "[+]"
        if response_message != "Good news, no limits are currently applied to your account. You’re free as a bird!" and response_message != "Ваш аккаунт свободен от каких-либо ограничений.":
            re_text = response_message.split(" ")
            if "until" in re_text:
                sym_ind = re_text.index("until")
                unlimited_date = re_text[sym_ind + 1] + " " + re_text[sym_ind + 2] + " " + re_text[sym_ind + 3] + " " + re_text[sym_ind + 4]
            else:
                try:
                    sym_ind = re_text.index("до")
                    unlimited_date = re_text[sym_ind + 1] + " " + re_text[sym_ind + 2] + " " + re_text[sym_ind + 3] + " " + re_text[sym_ind + 4]
                except:
                    unlimited_date = "Неизвестно"
        dates_list.append(unlimited_date)
        client.disconnect()
    return dates_list
    