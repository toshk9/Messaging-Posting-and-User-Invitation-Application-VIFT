import os, sys


def requirements():
    print("\nУстановка модулей...")
    modules_to_install = ['shutil', 'selenium','telethon','requests','configparser','sqlite3','PySocks','pystun3', 'instabot', 'json', 'vk', 'random', 'datetime', 'facebook', 'urllib3']
    for module in modules_to_install:
        try:
            os.system(f"pip3 install {module}\npython3 -m pip install {module}")
        except:
            continue

    if "accounts" not in os.listdir():
        os.mkdir("accounts")
        os.mkdir("accounts/facebook_accs")
        os.mkdir("accounts/vk_accs")
        os.mkdir("accounts/instagram_accs")
        os.mkdir("accounts/telegram_accs")
    
    if "resources" not in os.listdir():
        os.mkdir("resources")
    
    print("\nМодули установлены.")

if __name__ == "__main__":
    try:
        if any([sys.argv[1] == '--install', sys.argv[1] == '-i']):
            print("\nВыбранный модуль: " + sys.argv[1])
            requirements()
        elif any ([sys.argv[1] == '--help', sys.argv[1] == '-h']):
            print("( --install / -i ) установка необходимых модулей")
        else:
            print(f"\nНеизвестный аргумент: {sys.argv[1]}.\nДля помощи используйте:\n\'$ python3 setup.py -h\'")
    except IndexError:
        print(f"\nНе дан аргумент.\nДля помощи используйте:\n\'$ python3 setup.py -h\'")

