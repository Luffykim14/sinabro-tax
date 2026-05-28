"""
세금계산서 자동 입력 프로그램 - 시나브로마케팅
실행: python app.py → http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import os
import base64
import re
import io
import shutil
from datetime import datetime
from functools import wraps
from PIL import Image
from parser import parse_image_with_claude
from excel_writer import create_excel, save_template, TEMPLATE_PATH

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

APP_PASSWORD = os.environ.get('APP_PASSWORD', '')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if APP_PASSWORD and password == APP_PASSWORD:
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            error = '비밀번호가 일치하지 않습니다.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    template_exists = os.path.exists(TEMPLATE_PATH)
    return render_template('index.html', template_exists=template_exists)


@app.route('/upload-template', methods=['POST'])
@login_required
def upload_template():
    """국세청 양식 템플릿 업로드"""
    if 'template' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
    file = request.files['template']
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'xlsx 파일만 업로드 가능합니다.'}), 400
    try:
        tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'template_tmp.xlsx')
        file.save(tmp_path)
        save_template(tmp_path)
        return jsonify({'success': True, 'message': '템플릿이 저장되었습니다!'})
    except Exception as e:
        return jsonify({'error': f'템플릿 저장 실패: {str(e)}'}), 500


@app.route('/parse', methods=['POST'])
@login_required
def parse():
    """이미지 파싱 API"""
    if 'files' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400

    files = request.files.getlist('files')
    results = []

    for file in files:
        if file.filename == '':
            continue
        try:
            filename = file.filename
            date_info = extract_date_from_filename(filename)
            image_data = file.read()
            compressed_data, media_type = compress_image(image_data)
            base64_image = base64.b64encode(compressed_data).decode('utf-8')
            parsed = parse_image_with_claude(base64_image, media_type, filename)
            parsed['date_info'] = date_info
            parsed['filename'] = filename
            results.append({'success': True, 'data': parsed})
        except Exception as e:
            results.append({'success': False, 'filename': file.filename, 'error': f'파싱 실패: {str(e)}'})

    return jsonify({'results': results})


@app.route('/export', methods=['POST'])
@login_required
def export():
    """엑셀 다운로드 API"""
    try:
        data = request.json.get('rows', [])
        if not data:
            return jsonify({'error': '데이터가 없습니다.'}), 400
        output_path = create_excel(data, app.config['OUTPUT_FOLDER'])
        return send_file(output_path, as_attachment=True, download_name='세금계산서_업로드양식.xlsx')
    except Exception as e:
        return jsonify({'error': f'엑셀 생성 실패: {str(e)}'}), 500


def compress_image(image_data: bytes, max_size: int = 1000, quality: int = 85):
    img = Image.open(io.BytesIO(image_data))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    return output.read(), 'image/jpeg'


def extract_date_from_filename(filename):
    match = re.search(r'(\d{2})(\d{2})', filename)
    if match:
        month = match.group(1)
        day = match.group(2)
        year = str(datetime.now().year)
        return {'year': year, 'month': month, 'day': day, 'full_date': f"{year}{month}{day}"}
    today = datetime.now()
    return {
        'year': str(today.year),
        'month': str(today.month).zfill(2),
        'day': str(today.day).zfill(2),
        'full_date': today.strftime('%Y%m%d')
    }


if __name__ == '__main__':
    print("=" * 50)
    print(" 시나브로마케팅 세금계산서 자동 입력 프로그램")
    print(" 브라우저에서 http://localhost:5000 을 여세요")
    print("=" * 50)
    app.run(debug=True, port=5000)
