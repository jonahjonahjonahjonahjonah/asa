from flask import Flask, render_template, request, Response
import cv2
import time
import threading
import requests
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
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  

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

@app.route('/train', methods=["POST"])
def train():   
    if request.form['train'] == 'train':
        # upload the video to api

        url = 'http://127.0.0.1:5000/upload' # or some other url
        file_path = 'test.txt'

        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)

        print(response.json())

        # process and train and viewer url
        url = 'http://127.0.0.1:5000/train'
        response = requests.post(url)
        print(response.json())  
        
    return '',204




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
