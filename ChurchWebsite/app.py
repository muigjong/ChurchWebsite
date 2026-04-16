# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hope_church_key_1234'

# 관리자 설정
ADMIN_ID = 'admin'
ADMIN_PW = '1234'

##파이션애니웨어
# 파이션애네웨어 업로드 위해 수정 전
# UPLOAD_FOLDER = 'static/uploads'
# 파이션애니웨어 업르드 위해 수정 후 (PythonAnywhere의 실제 폴더 구조 반영)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 데이터 저장 (서버 재시작 시 초기화됨)
CHURCH_INTRO = "Welcome to Hopeful Church."
SERMON_VIDEOS = ['IGL3iYdkXas', 'T3FS3cuYnqo', 'u7UFjiLfTbc']
NOTICES = [] # { 'id': 1, 'title': '제목', 'content': '내용', 'image': '파일명' }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/intro')
def intro():
    return render_template('intro.html', intro_text=CHURCH_INTRO)

@app.route('/notices')
def notice_list():
    return render_template('notices.html', notices=NOTICES)

@app.route('/sermons')
@app.route('/sermons/<int:page>')
def sermons(page=1):
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    current_videos = SERMON_VIDEOS[start:end]
    total_pages = (len(SERMON_VIDEOS) + per_page - 1) // per_page
    return render_template('sermons.html', videos=current_videos, page=page, total_pages=total_pages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('user_id') == ADMIN_ID and request.form.get('user_pw') == ADMIN_PW:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        return "<script>alert('Invalid login.'); history.back();</script>"
    return render_template('login.html')

# --- 관리자 페이지 (모든 기능 통합) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global CHURCH_INTRO
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 1. 교회 소개 수정
        if 'church_intro' in request.form:
            CHURCH_INTRO = request.form.get('church_intro')
            return "<script>alert('Intro updated.'); location.href='/admin';</script>"

        # 2. 영상 추가
        video_url = request.form.get('video_url', '').strip()
        if video_url:
            video_id = ""
            if 'youtu.be/' in video_url: video_id = video_url.split('youtu.be/')[1].split('?')[0]
            elif 'v=' in video_url: video_id = video_url.split('v=')[1].split('&')[0]
            if video_id:
                SERMON_VIDEOS.insert(0, video_id)
                return "<script>alert('Video added.'); location.href='/admin';</script>"

        # 3. 공지사항 업로드
        if 'notice_title' in request.form:
            title = request.form.get('notice_title')
            content = request.form.get('notice_content')
            file = request.files.get('notice_image')
            filename = ""
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            notice_id = len(NOTICES) + 1
            NOTICES.insert(0, {'id': notice_id, 'title': title, 'content': content, 'image': filename})
            return "<script>alert('Notice uploaded.'); location.href='/admin';</script>"
    
    return render_template('admin.html', videos=SERMON_VIDEOS, intro_text=CHURCH_INTRO, notices=NOTICES)

# --- 삭제 기능들 ---
@app.route('/delete_video/<video_id>')
def delete_video(video_id):
    if session.get('logged_in') and video_id in SERMON_VIDEOS:
        SERMON_VIDEOS.remove(video_id)
    return redirect(url_for('admin'))

@app.route('/delete_notice/<int:notice_id>')
def delete_notice(notice_id):
    global NOTICES
    if session.get('logged_in'):
        NOTICES = [n for n in NOTICES if n['id'] != notice_id]
    return "<script>alert('Notice deleted.'); location.href='/admin';</script>"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)