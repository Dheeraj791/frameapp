import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploaded_videos'
EXTRACTED_FOLDER = 'extracted_images'
ALLOWED_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_b_mode(video_path, output_folder):
    cap = cv2.VideoCapture(video_path)
    frame_number = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        b_mode_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        output_filename = f"{output_folder}/frame_{frame_number:04d}.png"
        cv2.imwrite(output_filename, b_mode_frame)

        frame_number += 1

    cap.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_video.mp4')
            file.save(video_path)
            extract_b_mode(video_path, EXTRACTED_FOLDER)

            return redirect(url_for('results'))

    return render_template('index.html')

@app.route('/results')
def results():
    extracted_images = os.listdir(EXTRACTED_FOLDER)
    return render_template('results.html', images=extracted_images)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(EXTRACTED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
