from flask import Flask, request, render_template, send_file
from PIL import Image
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename == '':
            return 'No selected file', 400
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)

            # Open image and convert to RGBA mode (if not already)
            img = Image.open(filepath)
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Make the image transparent (example: sets alpha channel to 50% transparency)
            datas = img.getdata()
            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            
            img.putdata(newData)

            # Save the processed image with a new filename
            processed_img_filename = 'processed_' + filename
            processed_img_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_img_filename)
            img.save(processed_img_path)

            return send_file(processed_img_path, as_attachment=True)

    return 'No photo uploaded', 400

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
