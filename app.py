from flask import Flask, render_template, request, Response
import cv2
from gpiozero import Motor

frontleft = Motor(3,2)
frontright = Motor(14,15)
backleft = Motor(17,27)
backright = Motor(24,23)

app = Flask(__name__)

def gen_frames(): 
    camera = cv2.VideoCapture(0)  

    while True:
        ret, frame = camera.read()  
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') 

@app.route('/control', methods=['POST'])
def control():
    direction = request.form['direction']
    if direction == 'forward':
        print('forward')
        # frontleft.forward() 
        # frontright.forward()
        backleft.forward()
        backright.forward()

    elif direction == 'backward':
        print('backward')
        # frontleft.backward()
        # frontright.backward()
        backleft.backward()
        backright.backward()
    elif direction == 'right':
        
        backleft.forward()
        backright.backward()
    elif direction == 'left':
        
        backleft.backward()
        backright.forward()
    elif direction == 'stop':
        # frontleft.stop()
        # frontright.stop()
        backleft.stop()
        backright.stop()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
