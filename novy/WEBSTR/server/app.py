import os
import qrcode
import sqlite3
from flask import Flask, send_file, render_template, request, redirect, url_for, session

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret_key'

# Cesta pro ukládání QR kódů
QR_CODES_DIR = 'static/qrcodes'
os.makedirs(QR_CODES_DIR, exist_ok=True)

# Cesta k databázi
DB_PATH = 'db.sqlite3'


def init_db():
    """Inicializace databáze a tabulek"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coffees (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        conn.commit()


@app.route('/')
def index():
    """Hlavní stránka aplikace"""
    if 'user_id' in session:
        return redirect(url_for('coffee_overview'))  # Pokud je uživatel přihlášený, přejdeme na přehled
    return render_template('index.html')


@app.route('/api/qr_code/<string:token>')
def generate_qr_code(token):
    """Generování QR kódu pro registraci"""
    qr_data = f"http://127.0.0.1:5000/register/{token}"  # URL pro registraci
    img = qrcode.make(qr_data)
    img_path = os.path.join(QR_CODES_DIR, f'{token}.png')
    img.save(img_path)
    return send_file(img_path, mimetype='image/png')


@app.route('/register/<string:token>', methods=['GET', 'POST'])
def register(token):
    """Registrace uživatele"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # Uložení uživatele do databáze
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (name, email)
            VALUES (?, ?)
            ''', (name, email))
            conn.commit()

        # Přihlášení uživatele
        user_id = cursor.lastrowid  # ID právě přidaného uživatele
        session['user_id'] = user_id  # Uložení do session

        return redirect(url_for('coffee_overview'))  # Po registraci přesměrovat na přehled

    return render_template('register.html', token=token)


@app.route('/coffee_overview', methods=['GET', 'POST'])
def coffee_overview():
    """Přehled objednávek kávy"""
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Pokud není uživatel přihlášený, přesměrujeme na hlavní stránku

    user_id = session['user_id']
    
    # Pokud uživatel odesílá objednávku kávy (POST)
    if request.method == 'POST':
        amount = int(request.form.get('amount'))
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO coffees (user_id, amount)
            VALUES (?, ?)
            ''', (user_id, amount))
            conn.commit()

    # Získání přehledu o objednávkách pro všechny uživatele
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT u.name, SUM(c.amount) as total_coffees
        FROM coffees c
        JOIN users u ON c.user_id = u.id
        GROUP BY u.id
        ''')
        coffee_data = cursor.fetchall()  # Získání všech dat o objednávkách

    return render_template('coffee_overview.html', coffee_data=coffee_data)


@app.route('/add_coffee', methods=['POST'])
def add_coffee():
    """Přidání nové objednávky kávy"""
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Pokud není uživatel přihlášený, přesměrujeme na hlavní stránku

    amount = int(request.form.get('amount'))
    user_id = session['user_id']

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO coffees (user_id, amount)
        VALUES (?, ?)
        ''', (user_id, amount))
        conn.commit()

    return redirect(url_for('coffee_overview'))


@app.route('/logout')
def logout():
    """Odhlášení uživatele"""
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()  # Inicializace databáze při spuštění
    app.run(debug=True)
