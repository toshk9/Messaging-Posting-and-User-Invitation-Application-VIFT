import os, sys


def add_account():
	import configparser
	import stun
	dir_list = os.listdir(path="accounts/telegram_accs")
	cpass = configparser.RawConfigParser()
	cpass.add_section('cred')
	xid = input("Введите API ID : ")
	cpass.set('cred', 'id', xid)
	xhash = input("Введите API HASH : ")
	cpass.set('cred', 'hash', xhash)
	xphone = input("Введите номер телефона : ")
	cpass.set('cred', 'phone', xphone)
	proxy_data = stun.get_ip_info()
	ip = proxy_data[1]
	cpass.set('cred', 'ip', ip)
	port = proxy_data[2]
	cpass.set('cred', 'port', port)
	try:
		new_dir = "accounts/telegram_accs/account_{}".format(int(dir_list[-1].split("_")[1]) + 1)
	except:
		new_dir = "accounts/telegram_accs/account_1"
	os.mkdir(new_dir)
	with open(f'{new_dir}/config.data', 'w') as setup:
		cpass.write(setup)
	print("Аккаунт добавлен!")

def merge_sqlite():
	import sqlite3
	import sys
	with sqlite3.connect("telegram.db") as db:
		cursor = db.cursor()
		cursor.execute(f"""SELECT * FROM {sys.argv[2]}""")
		users_table_1 = cursor.fetchall()
		cursor.execute(f"""SELECT * FROM {sys.argv[3]}""")
		users_table_2 = cursor.fetchall()
		new_table_title = input("Введите название новой таблицы : ")
		print(' Объединение '+sys.argv[2]+' & '+sys.argv[3]+' ...')
		print('Большие файлы могу занять некоторое время ... ')
		cursor.execute(""" CREATE TABLE IF NOT EXISTS {} (list_id INTEGER, username TEXT, user_id INTEGER, access_hash TEXT, name TEXT, group_title TEXT, group_id INTEGER) """.format(new_table_title))
		for user_table_2 in users_table_2:
			cursor.execute(""" INSERT INTO {} (list_id, username, user_id, access_hash, name, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(new_table_title), user_table_2)
		for user_table_1 in users_table_1:
			if user_table_1 not in users_table_2:
				cursor.execute(""" INSERT INTO {} (list_id, username, user_id, access_hash, name, group_title, group_id) VALUES(?, ?, ?, ?, ?, ?, ?) """.format(new_table_title), user_table_1)
		db.commit()
	print(' Таблица "{}" сохранена в members.db'.format(new_table_title))
