from flask import Flask, render_template, request, redirect, url_for, session
import db, string, random
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))


@app.route('/')
def index():
    msg = request.args.get('msg')
    if msg == None:
        return render_template('index.html')
    else:
        return render_template('index.html', msg=msg)


# ログイン
@app.route('/', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if db.login(email, password):
        session['user'] = db.user_data(email)
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10000)
        return redirect(url_for('home'))
    else:
        error = 'ユーザー名またはパスワードが違います。'
        return render_template('index.html', error=error)


@app.route('/home', methods=['GET'])
def home():
    if 'user' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('index'))


# 登録
@app.route('/register')
def register_form():
    return render_template('register_form.html')


@app.route('/register_confirm', methods=['POST'])
def register_confirm():
    user_name = request.form.get("username")
    birth = request.form.get("calendar")
    tel_number = request.form.get("tel_number")
    email = request.form.get("email")
    password = request.form.get("password")
    error = None

    if user_name == '':
        error = '必須項目に未入力です。'
        return render_template('register_form.html', error=error)
    elif tel_number == '':
        error = '必須項目に未入力です。'
        return render_template('register_form.html', error=error)
    elif email == '':
        error = '必須項目に未入力です。'
        return render_template('register_form.html', error=error)
    elif password == '':
        error = 'パスワードが未入力です。'
        return render_template('register_form.html', error=error)
    elif error == None:
        session['user_list'] = (user_name, birth, tel_number, email, password)
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)

        return render_template('register_confirm.html')
    else:
        return render_template('index.html', error=error)


@app.route('/register_exe')
def register_exe():
    user = session['user_list']

    user_name = user[0]
    birth = user[1]
    tel_number = user[2]
    email = user[3]
    password = user[4]
    session.pop('user_list')

    count = db.insert_user(user_name, birth, tel_number, email, password)

    if count == 1:
        msg = '登録が完了しました。'
        return render_template('register_complete.html', msg=msg)
    else:
        error = '登録に失敗しました。'
        return render_template('register_form.html', error=error)


@app.route('/home/post_form', methods=['GET'])
def post_form():
    if 'user' in session:
        return render_template('post_form.html')
    else:
        return redirect(url_for('index'))


@app.route('/post_exe', methods=['POST'])
def post_exe():
    data = request.form.get("post_text")
    user = session['user']
    user_id = user[0]
    print(data)

    count = db.insert_post(data, user_id)
    
    if count == 1:
        return render_template('post_complete.html')
    else:
        error = '投稿に失敗しました。'
        return render_template('post_form.html', error=error)


@app.route('/home/post_list')
def post_list():
    if 'user' in session:
        row = db.post_list()
        if row != None:
            return render_template('post_list.html', rows=row)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


# アカウント編集


@app.route('/home/account_edit')
def account_edit_form():
    if 'user' in session:
        return render_template('account_edit_form.html')
    else:
        return redirect(url_for('index'))


@app.route('/home/account_edit_confirm', methods=['POST'])
def account_edit_confirm():
    if 'user' in session:
        user_name = request.form.get("user_name")
        birth = request.form.get("birth")
        tel_number = request.form.get("tel_number")
        email = request.form.get("email")
        error = None

        if user_name == '':
            error = '必須項目に未入力です。'
            return render_template('account_edit_form.html', error=error)
        elif tel_number == '':
            error = '必須項目に未入力です。'
            return render_template('account_edit_form.html', error=error)
        elif birth == '':
            error = '必須項目に未入力です。'
            return render_template('account_edit_form.html', error=error)
        elif error == None:
            session['user_list'] = (user_name, birth, tel_number, email)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return render_template('account_edit_confirm.html')
        else:
            return render_template('index.html')


@app.route('/home/account_edit_exe')
def account_edit_exe():
    user = session['user_list']

    user_name = user[0]
    birth = user[1]
    tel_number = user[2]
    email = user[3]

    session.pop('user_list')
    session.pop('user')

    count = db.edit_user(user_name, birth, tel_number, email)

    if count == 1:
        session['user'] = db.user_data(email)
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=1)
        msg = '登録が完了しました。'
        return render_template('account_edit_complete.html', msg=msg)
    else:
        error = '登録に失敗しました。'
        return render_template('account_edit_form.html', error=error)

#自分の情報
@app.route('/home/account_post_list')
def account_post_list():
    if 'user' in session:
        user = session['user']
        user_id = user[0]
        rows = db.my_post_list(user_id)
        
        if rows != None:
            return render_template('account_post_list.html', rows=rows)
        
    else:
        return redirect(url_for('home'))

#削除機能
@app.route('/account_drop_post', methods=['POST'])
def account_drop_post():
    if 'user' in session:
        user = session['user']
        user_id = user[0]
        post_id = request.form.get('post_id')
        
        print(post_id)
        print(user_id)

        count = db.drop_my_post(user_id, post_id)
        print(count)
        
        if count == 1:
            return render_template('account_drop_complete.html')
        else:
            error = '削除に失敗しました。再度お試しください。'
            return render_template('account_drop_error.html')
    else:
        return redirect(url_for('index'))
    

#検索機能
@app.route('/search', methods=['GET'])
def search():
    
    data = request.args.get('data')
    num = data.find('@')
    
    if num == 0:
        print(1)
        fdata =  data.strip("@")
        print(fdata)
        data_list = db.search_user(fdata)
        return render_template('search_user.html', rows=data_list)
    else:
        print(2)
        data_list = db.search_post(data)
        return render_template('search_post_list.html', rows=data_list)


    

# logout
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
