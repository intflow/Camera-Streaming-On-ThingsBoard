from flask import Flask, render_template, Response
import cv2
from imutils.video import VideoStream

app = Flask(__name__)
camera_ids = [
    'rtsp://admin:intflow3121@192.168.1.62:554/Streaming/Channels/102',
    'rtsp://admin:kmjeon3121@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1'
   ]

def find_camera(list_id):
    return camera_ids[int(list_id)]

def gen_frames(camera_id):
    cam = find_camera(camera_id)  # return the camera access link with credentials. Assume 0?
   
    cap = VideoStream(cam).start()
    while True:
        frame = cap.read()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/', methods=["GET"])
def index():
    return render_template('index.html', cameras_id=len(camera_ids))

@app.route('/video_feed/<string:list_id>/', methods=["GET"])
def video_feed(list_id):
    return Response(gen_frames(list_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.0.58',port = "7000", debug=False)