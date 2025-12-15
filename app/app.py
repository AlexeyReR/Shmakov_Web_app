from flask import Flask, request, make_response, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = '/tmp/users.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "User already exists!"
    return '''
    <form method="post">
        Username: <input name="username" required><br>
        Password: <input name="password" type="password" required><br>
       <input type="submit" value="Register">
    </form>
    '''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        user = c.fetchone()
        conn.close()
        if user:
            resp = make_response(redirect(url_for('welcome')))
            resp.set_cookie('username', user[1])
            return resp
        return "Invalid credentials!"
    return '''
    <form method="post">
        Username: <input name="username" required><br>
        Password: <input name="password" type="password" required><br>
        <input type="submit" value="login">
    </form>
    '''

@app.route('/welcome')
def welcome():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    return f"<h1>Privet, {username}</h1>"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
