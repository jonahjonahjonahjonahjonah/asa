from flask import Flask, request, jsonify
import os
import subprocess
import requests

app = Flask(__name__)

upload_folder = 'uploads' 
os.makedirs(upload_folder, exist_ok=True)  
app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/upload', methods=['POST'])
def upload_file():

    file = request.files.get('file')

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return jsonify({'message': 'File uploaded'}), 200 

@app.route('/train', methods=['POST'])
def train():

    PROCESSED_DATA_DIR=''
    #process the video file
    subprocess.run(f'ns-process-data video --data {upload_folder} --output-dir {PROCESSED_DATA_DIR}', shell=True)

    # train model and get viwer 
    result = subprocess.run(f'ns-train nerfacto --data {PROCESSED_DATA_DIR} --viewer.make-share-url True | grep "Shareable viewer URL"', shell=True, capture_output=True, text=True)  

    return jsonify({"url": result.stdout})

@app.route('/send', methods=['POST','GET'])
def send():
    send back the files to the car
    url = 'http://127.0.0.1:5000/recieve'
    modelpath = 'folder/test.txt'
    camerapathpath = 'folder/lol.json'
    files = {'model': modelpath,
             'camera_path':  camerapathpath}
    requests.post(url, files=files)
    return '',204

# if __name__ == '__main__':
#     app.run(debug=True)
app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
