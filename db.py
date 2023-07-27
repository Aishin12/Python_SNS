import os, psycopg2, string, random, hashlib
from datetime import datetime


def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection


def get_salt():
    charset = string.ascii_letters + string.digits

    salt = ''.join(random.choices(charset, k=30))
    return salt


def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 1246).hex()
    return hashed_password


def insert_user(user_name, birth, tel_number, email, password):
    sql = 'INSERT INTO sns_user VALUES(default, %s, %s, %s, %s, %s, %s)'

    salt = get_salt()
    hashed_password = get_hash(password, salt)

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            sql, (user_name, birth, tel_number, email, salt, hashed_password)
        )
        count = cursor.rowcount
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()

    return count


def login(email, password):
    sql = 'SELECT password, salt FROM sns_user WHERE email = %s'
    flg = False

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        if user != None:
            salt = user[1]
            hashed_password = get_hash(password, salt)

            if hashed_password == user[0]:
                flg = True

    except psycopg2.DatabaseError:
        flg = False

    finally:
        cursor.close()
        connection.close()

    return flg


# ログイン時のセッション取り出し
def user_data(email):
    sql = 'SELECT user_id, user_name, birth, tel_number FROM sns_user WHERE email = %s'

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    user_id = user[0]
    user_name = user[1]
    birth = user[2]
    tel_number = user[3]

    cursor.close()
    connection.close()

    return (user_id, user_name, birth, tel_number, email)


# アカウント編集
def edit_user(user_name, birth, tel_number, email):
    sql = 'UPDATE sns_user SET user_name = %s, birth = %s, tel_number = %s, email = %s WHERE email = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (user_name, birth, tel_number, email, email))
        count = cursor.rowcount
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()

    return count


# 投稿
def insert_post(post_text, user_id):
    sql = 'INSERT INTO sns_post VALUES(default, %s, %s)'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (post_text, user_id))
        count = cursor.rowcount
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()

    return count


def post_list():
    sql = 'SELECT sns_user.user_name, sns_post.post_text FROM sns_user INNER JOIN sns_post ON sns_user.user_id = sns_post.user_id'

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql)
        rows = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return rows


def my_post_list(user_id):
    sql = 'SELECT sns_user.user_name, sns_post.post_text, sns_post.post_id FROM sns_user INNER JOIN sns_post ON sns_user.user_id = sns_post.user_id WHERE sns_post.user_id = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return rows


def drop_my_post(user_id, post_id):
    sql = 'DELETE FROM sns_post WHERE user_id = %s AND post_id = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (user_id, post_id))
        count = cursor.rowcount
        connection.commit()
        
    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()

    return count

def search_user(data):
    
    sql ='SELECT user_name, user_id FROM sns_user WHERE user_name LIKE  %s '
    
    search_query = f'%{ data }%'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (search_query, ))
        rows = cursor.fetchall()
        
    finally:
        cursor.close()
        connection.close()

    return rows

def search_post(data):
    
    sql ='SELECT sns_user.user_name, sns_post.post_text, sns_post.post_id FROM sns_user INNER JOIN sns_post ON sns_user.user_id = sns_post.user_id WHERE sns_post.post_text LIKE  %s'
    
    search_query = f'%{ data }%'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (search_query, ))
        rows = cursor.fetchall()
        
    finally:
        cursor.close()
        connection.close()
    return rows


