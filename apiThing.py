from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

upload_folder = './uploads' 
app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/upload', methods=['POST'])
def upload_file():

    file = request.files['file']
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return jsonify({'message': 'File uploaded'}), 200
  
    
@app.route('/train', methods=['POST'])
def train():

    PROCESSED_DATA_DIR=''
    #process the video file
    subprocess.run(f'ns-process-data video --data {upload_folder} --output-dir {PROCESSED_DATA_DIR}', shell=True)

    # train model and get viwer 
    result = subprocess.run(f'ns-train nerfacto --data {PROCESSED_DATA_DIR} --viewer.make-share-url True | grep "Shareable viewer URL"', shell=True, capture_output=True, text=True)  
    return jsonify({"url": result.stdout})

if __name__ == '__main__':
    app.run(debug=True)