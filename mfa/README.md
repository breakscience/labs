These are steps to create a Dockerized container to simulate Multi-Factor Authentication (MFA). You’ll need to create a basic application that includes MFA functionality. For this example, I’ll use a simple Python Flask application with MFA using Time-based One-Time Password (TOTP).

Step 1: Setup Your Environment

First, make sure you have Docker installed on your machine. You will also need to have docker-compose installed.

Step 2: Create the Flask Application

Create a new directory for your project and navigate into it:

    mkdir flask-mfa
    cd flask-mfa

Create a new file named app.py:

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

Create the login.html template:

    <!doctype html>
    <html>
    <head>
        <title>Login</title>
    </head>
    <body>
        <h1>Login</h1>
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <ul>
                {% for message in messages %}
                    <li>{{ message }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}
    </body>
    </html>
    
    Create the mfa.html template:
    
    <!doctype html>
    <html>
    <head>
        <title>MFA</title>
    </head>
    <body>
        <h1>Multi-Factor Authentication</h1>
        <img src="data:image/png;base64,{{ qr_code }}"><br>
        <form method="post">
            Token: <input type="text" name="token"><br>
            <input type="submit" value="Verify">
        </form>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <ul>
                {% for message in messages %}
                    <li>{{ message }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}
    </body>
    </html>

Step 3: Create a Dockerfile

Create a Dockerfile in the same directory:

    # Use the official Python image from the Docker Hub
    FROM python:3.9-slim
    
    # Set the working directory in the container
    WORKDIR /app
    
    # Copy the current directory contents into the container at /app
    COPY . /app
    
    # Install the necessary packages
    RUN pip install flask pyotp qrcode[pil]
    
    # Make port 5000 available to the world outside this container
    EXPOSE 5000
    
    # Define environment variable
    ENV NAME World
    
    # Run app.py when the container launches
    CMD ["python", "app.py"]

Step 4: Create a Docker Compose File

Create a docker-compose.yml file:

    version: '3'
    services:
      web:
        build: .
        ports:
          - "5000:5000"
        volumes:
          - .:/app


Step 5: Build and Run the Docker Container

Build and run your container using Docker Compose:

    docker-compose up --build

Now, navigate to http://localhost:5000 in your web browser. You should be able to log in and go through the MFA process.
