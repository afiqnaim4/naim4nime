from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '041209@'  # Pastikan ini ditetapkan untuk menyokong sesi
UPLOAD_FOLDER = os.path.join('static', 'uploads')
VIDEO_JSON = 'video.json'

# Menyediakan folder upload jika tiada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Membaca video dari fail JSON
def get_videos():
    if os.path.exists(VIDEO_JSON):
        with open(VIDEO_JSON, 'r') as f:
            return json.load(f)
    else:
        return []

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect ke login jika tidak log masuk

    search_query = request.args.get('search', '').lower()

    videos = get_videos()

    # Tapis ikut search
    if search_query:
        videos = [v for v in videos if search_query in v['title'].lower()]

    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect ke login jika tidak log masuk

    if request.method == 'POST':
        # Dapatkan maklumat video
        title = request.form['title']
        video = request.files['video']

        # Nama fail yang selamat untuk disimpan
        filename = secure_filename(video.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        video.save(filepath)

        # Menambah video ke dalam fail JSON
        video_data = {'title': title, 'filename': filename}

        videos = get_videos()
        videos.append(video_data)

        with open(VIDEO_JSON, 'w') as f:
            json.dump(videos, f, indent=4)

        flash('Video berjaya dimuat naik!', 'success')
        return redirect(url_for('index'))

    return render_template('tambah.html')

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Semak login, contohnya dengan fail users.json
        with open('users.json', 'r') as f:
            users = json.load(f)

        if username in users and users[username] == password:
            session['user'] = username
            flash('Berjaya login!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Berjaya log keluar!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
