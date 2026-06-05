from flask import Flask, request
from datetime import datetime
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'images'
METADATA_FOLDER = 'metadata'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    try:
        return open('index.html').read()
    except FileNotFoundError:
        return "Index file not found", 404

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files.get('image')
    metadata = request.form.get('metadata')

    if image:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(UPLOAD_FOLDER, f'snapshot_{timestamp}.png')
        image.save(image_path)

        meta_path = os.path.join(METADATA_FOLDER, 'latest.json')
        data = {
            'client_ip': request.remote_addr,
            'metadata': json.loads(metadata) if metadata else {},
            'timestamp': timestamp
        }

        with open(meta_path, 'w') as f:
            json.dump(data, f, indent=2)

        return 'Uploaded', 200

    return 'No image', 400

if __name__ == '__main__':
    # التعديل هنا: قراءة المنفذ من متغير بيئة Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
