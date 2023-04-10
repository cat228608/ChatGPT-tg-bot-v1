import sqlite3
import requests
import openai

def connect():
    conn = sqlite3.connect("db.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor
conn, cursor = connect()

def get_key(key):
    if key == '0':
        cursor.execute(f"SELECT token FROM Token")
        row = cursor.fetchone()
        if row == None:
            return "no key"
        conn.commit()
        return row[0]
    else:
        cursor.execute(f"DELETE FROM Token WHERE token = ?", [key])
        conn.commit()
        cursor.execute(f"SELECT token FROM Token")
        row = cursor.fetchone()
        if row == None:
            return "no key"
        conn.commit()
        return row[0]
    
def add_token(token):
    cursor.execute(f"INSERT INTO Token(token) VALUES ('{token}')")
    conn.commit()
    
def ban(comand, chatid):
    if comand == 'check':
        print(f"[LOG] - Проверка на бан {chatid}")
        cursor.execute(f"SELECT ban FROM ban WHERE ban = {chatid}")
        row = cursor.fetchone()
        conn.commit()
        if row is not None:
            return False
        else:
            return True
    if comand == 'check_chat':
        cursor.execute(f"SELECT ban FROM ban WHERE ban = {chatid}")
        row = cursor.fetchone()
        conn.commit()
        if row is not None:
            return False
        else:
            return True
    elif comand == 'ban':
        cursor.execute(f"SELECT ban FROM ban WHERE ban = {chatid}")
        row = cursor.fetchone()
        conn.commit()
        if row == None:
            cursor.execute(f"INSERT INTO ban(ban) VALUES ('{chatid}')")
            return '0'
        else:
            return '1'
    elif comand == 'unban':
        cursor.execute(f"SELECT ban FROM ban WHERE ban = {chatid}")
        row = cursor.fetchone()
        conn.commit()
        if row == None:
            return '1'
        else:
            cursor.execute(f"DELETE FROM ban WHERE ban = {chatid}")
            return '0'
    elif comand == 'addadmin':
        cursor.execute(f"SELECT chatid FROM admin WHERE chatid = {chatid}")
        row = cursor.fetchone()
        conn.commit()
        if row == None:
            cursor.execute(f"INSERT INTO admin(chatid) VALUES ('{chatid}')")
            return '0'
        else:
            return '1'
          
def get_adm(chatid):
    cursor.execute(f"SELECT chatid FROM admin WHERE chatid = {chatid}")
    row = cursor.fetchone()
    conn.commit()
    return row