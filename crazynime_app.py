from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '041209@'  # Boleh tukar kepada kunci rahsia lain
UPLOAD_FOLDER = os.path.join('static', 'uploads')
VIDEO_JSON = 'video.json'
USERS_JSON = 'users.json'

# Menyediakan folder upload jika tiada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect ke login jika tidak log masuk
    
    search_query = request.args.get('search', '').lower()

    if os.path.exists(VIDEO_JSON):
        with open(VIDEO_JSON, 'r') as f:
            videos = json.load(f)
    else:
        videos = []

    if search_query:
        videos = [v for v in videos if search_query in v['title'].lower()]

    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect ke login jika tidak log masuk

    if request.method == 'POST':
        title = request.form['title']
        video = request.files['video']

        filename = secure_filename(video.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        video.save(filepath)

        video_data = {'title': title, 'filename': filename}

        if os.path.exists(VIDEO_JSON):
            with open(VIDEO_JSON, 'r') as f:
                videos = json.load(f)
        else:
            videos = []

        videos.append(video_data)

        with open(VIDEO_JSON, 'w') as f:
            json.dump(videos, f, indent=4)

        flash('Video berjaya dimuat naik!', 'success')
        return redirect(url_for('index'))

    return render_template('tambah.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Semak dalam fail users.json
        if os.path.exists(USERS_JSON):
            with open(USERS_JSON, 'r') as f:
                users = json.load(f)
            
            if username in users and users[username] == password:
                session['user'] = username  # Simpan username dalam sesi
                flash('Berjaya login!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Username atau password salah.', 'danger')
        else:
            flash('Sistem tidak dapat membaca pengguna. Fail users.json hilang.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Hapuskan sesi apabila logout
    flash('Anda berjaya log keluar', 'success')
    return redirect(url_for('login'))

import os

if __name__ == '__main__':
    # Dapatkan PORT dari environment variable (Render memberi PORT yang berbeza)
    port = int(os.environ.get("PORT", 5000))  # Jika tiada PORT, guna 5000
    app.run(debug=True, host='0.0.0.0', port=port)
