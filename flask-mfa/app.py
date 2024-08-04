from flask import Flask, request, session, redirect, url_for, render_template, flash
import pyotp
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# User data for demonstration purposes
users = {
    'user1': {
        'password': 'password123',
        'secret': pyotp.random_base32()
    }
}

@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('mfa'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/mfa', methods=['GET', 'POST'])
def mfa():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    
    if request.method == 'POST':
        token = request.form['token']
        totp = pyotp.TOTP(user['secret'])
        if totp.verify(token):
            return redirect(url_for('index'))
        flash('Invalid token')
    
    totp = pyotp.TOTP(user['secret'])
    qr_uri = totp.provisioning_uri(username, issuer_name="MyApp")
    img = qrcode.make(qr_uri)
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render_template('mfa.html', qr_code=img_str)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
