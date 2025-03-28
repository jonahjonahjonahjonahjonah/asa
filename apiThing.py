from flask import Flask, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename
import os
import subprocess
import requests
import time
from flask_cors import CORS
import shutil

app = Flask(__name__)
CORS(app)

def run_command(command): # running and output command

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in process.stdout:
        yield f"data: {line.strip()}\n\n" 

UPLOAD_FOLDER = 'uploads' 
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return jsonify({'message':'The server is running'})

@app.route('/upload', methods=['POST'])
def upload_file(): # save uploaded video file 

    file = request.files.get('file')
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded'}), 200 

@app.route('/train', methods=['GET'])
def train(): # process video and train nerfstudio

    PROCESSED_DATA_DIR = 'processed'
    OUTPUT_DIR = 'outputs'

    # terminal commands to process the video file & train nerf model
    processcmd = f'ns-process-data video --data {UPLOAD_FOLDER}/video.avi --output-dir {PROCESSED_DATA_DIR}'
    #'ns-train nerfacto --data data/nerfstudio/poster --output-dir outputs/ --experiment-name test --timestamp none'
    
    traincmd = f'ns-train nerfacto --data {PROCESSED_DATA_DIR} --output-dir {OUTPUT_DIR} --experiment-name test --timestamp none'
    # processcmd = f'sl'
    # traincmd = f'echo "done"'

    shutil.rmtree(f'{OUTPUT_DIR}/test')

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*" 
    }
    return Response(run_command(processcmd + '&&' + traincmd), headers=headers)

@app.route('/send', methods=['POST','GET'])
def send():
    global OUTPUT_DIR
    folder_path = f'{OUTPUT_DIR}/test/nerfacto/none'

    #zip
    shutil.make_archive('output', 'zip', folder_path)
    #send
    return send_file('output.zip', as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
