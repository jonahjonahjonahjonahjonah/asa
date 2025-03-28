from flask import Flask, render_template, request, Response
import cv2
import time
import threading
import requests
import subprocess
import zipfile
# from gpiozero import Motor

# frontleft = Motor(3,2)
# frontright = Motor(14,15)
# backleft = Motor(17,27)
# backright = Motor(24,23)

app = Flask(__name__)
recording = False
def record():
    global recording

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    frame_width = int(cap.get(3)) 
    frame_height = int(cap.get(4)) 
    size = (frame_width,frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    result = cv2.VideoWriter('video.avi', fourcc, 30, size)

    while recording:
        success, frame =  cap.read()
        print(success)

        if success == True:
            result.write(frame)
            
    result.release()
    print("recording stopped")

    while not recording:
        time.sleep(0.1)

def gen_frames(): 
    camera = cv2.VideoCapture(0)  
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        ret, frame = camera.read()  
        if ret == True:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    direction = request.form['direction']
    if direction == 'forward':
        print('forward')
        # frontleft.forward() 
        # frontright.forward()
        # backleft.forward()
        # backright.forward()
        
    elif direction == 'backward':
        print('backward')
        # frontleft.backward()
        # frontright.backward()
        # backleft.backward()
        # backright.backward()
    elif direction == 'right':
        print('right')
        # backleft.forward()
        # backright.backward()
    elif direction == 'left':
        print('left')
        # backleft.backward()
        # backright.forward()
    elif direction == 'stop':
        print('stop')
        # frontleft.stop()
        # frontright.stop()
        # backleft.stop()
        # backright.stop()
    return '',204
        
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') 

@app.route('/record', methods=["POST"])
def recordcontrol():    
    global recording
    if request.form['recording'] == 'start':
        recording = True
        threading.Thread(target=record).start()
    else:
        recording = False 
    print("recording"+str(recording))
    return '',204

upload_folder = 'uploads' 
app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/train', methods=["POST", "GET"])
def train():
    url = 'http://localhost:5001'
    # url = 'http://server.emmerich.co.id:5001'
    train_value = request.form.get('train') # options; what to do from button

    if train_value == 'upload':
        # Upload the video to API
        uploadurl = f'{url}/upload' 
        file_path = 'video.avi'

        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(uploadurl, files=files)

        return render_template('index.html', text=response.text)

    elif train_value == 'train':
        # Process and train and return viewer URL
        trainurl = f'{url}/train'
        response = requests.get(trainurl)
        
        return render_template('stream.html', producer_url=trainurl) 

    elif train_value == 'send':
        # Tell the API to send the file back to the car
            url='http://localhost:5000/send'
            response = requests.get(url)

            # download zip
            if response.status_code == 200:
                with open('output.zip', 'wb') as f:
                    f.write(response.content)
                print("zip downloaded")
            else:
                print(f"Failed to download: {response.status_code}")

            # extract zip
            zip_path = 'output.zip'
            folder = 'output'
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(folder)
            print('unzipped')

            return '',204
    
    return '', 204  

@app.route('/viewer')
def recieve():
    
    def run():
        if request.form.get('viewer') == 'start':
            traincmd = 'ns-viewer --load-config output/config.yml --viewer.make-share-url True'
            #traincmd = 'ping -c 5 google.com'
            process = subprocess.Popen(traincmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                yield f'data: {line}\n\n'
    
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*" 
    }
    return Response(run(), headers=headers)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
