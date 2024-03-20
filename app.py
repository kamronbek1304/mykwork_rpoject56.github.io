from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def create_users_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, score INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

create_users_table()

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            return 'Invalid username or password'
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        session['username'] = username
        return redirect('/dashboard')
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'POST':
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("UPDATE users SET score = score + 1 WHERE username=?", (session['username'],))
            conn.commit()
            conn.close()
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT score FROM users WHERE username=?", (session['username'],))
        score = c.fetchone()[0]
        c.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
        top_users = c.fetchall()
        conn.close()
        return render_template('index.html', score=score, top_users=top_users)
    else:
        return redirect('/')

@app.route('/top_users')
def top_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
    top_users = c.fetchall()
    conn.close()
    return render_template('top_users.html', top_users=top_users)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
