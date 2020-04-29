from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory

import asyncio, sys, os
from onvif import ONVIFCamera
from imutils.video import VideoStream
import time
#import cv2


app = Flask(__name__)
camera_ids = [
    'rtsp://admin:intflow3121@192.168.0.110:554/Streaming/Channels/102',
    # 'rtsp://admin:kmjeon3121@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1'
   ]


img_ids = [
    'left_up.png',
    'up.png',
    'right_up.png',
    'left.png',
    'home.png',
    'right.png',
    'left_down.png',
    'down.png',
    'right_down.png',
    'zoom_in.png',
    'zoom_out.png'
]

IP="192.168.0.110"   # Camera IP address
PORT=80           # Port
USER="admin"         # Username
PASS="intflow3121"        # Password

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
ZMAX = 1.0
ZMIN = 0
positionrequest = None
ptz = None
active = False
homerequest = None

def do_move(ptz, request):
    # Start continuous move
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.ContinuousMove(request)

def do_move_home(ptz, request):
    # Start continuous move
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.AbsoluteMove(request)

def do_zoom(ptz, request):
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.AbsoluteMove(request)

def move_up(ptz, request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMAX
    do_move(ptz, request)

def move_down(ptz, request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
    do_move(ptz, request)

def move_right(ptz, request):
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = 0
    do_move(ptz, request)

def move_left(ptz, request):
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = 0
    do_move(ptz, request)
    

def move_upleft(ptz, request):
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = YMAX
    do_move(ptz, request)
    
def move_upright(ptz, request):
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = YMAX
    do_move(ptz, request)
    
def move_downleft(ptz, request):
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = YMIN
    do_move(ptz, request)
    
def move_downright(ptz, request):
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = YMIN
    do_move(ptz, request)

def move_home(ptz, request):
    request.Position.PanTilt.x = 1
    request.Position.PanTilt.y = 0
    request.Position.Zoom = 0
    do_move_home(ptz,request)

def Zoom_in(ptz,request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = ZMAX
    do_move(ptz, request)

def Zoom_out(ptz,request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = ZMIN
    do_move(ptz,request)

def setup_move():
    mycam = ONVIFCamera(IP, PORT, USER, PASS)
    # Create media service object
    media = mycam.create_media_service()
    
    # Create ptz service object
    global ptz 
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    global positionrequest, homerequest
    positionrequest = ptz.create_type('ContinuousMove')
    positionrequest.ProfileToken = media_profile.token
    if positionrequest.Velocity is None:
        positionrequest.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        positionrequest.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        positionrequest.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

    homerequest = ptz.create_type('AbsoluteMove')
    homerequest.ProfileToken = media_profile.token
    if homerequest.Position is None :
        homerequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        homerequest.Position.PanTilt.space = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].URI
        homerequest.Position.Zoom.space = ptz_configuration_options.Spaces.AbsoluteZoomPositionSpace[0].URI

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN, ZMAX, ZMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
    ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max
    ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min



def readin():
    """Reading from stdin and displaying menu"""
    global positionrequest, ptz
    
    selection = sys.stdin.readline().strip("\n")
    lov=[ x for x in selection.split(" ") if x != ""]
    if lov:
        
        if lov[0].lower() in ["u","up"]:
            move_up(ptz,positionrequest)
        elif lov[0].lower() in ["d","do","dow","down"]:
            move_down(ptz,positionrequest)
        elif lov[0].lower() in ["l","le","lef","left"]:
            move_left(ptz,positionrequest)
        elif lov[0].lower() in ["l","le","lef","left"]:
            move_left(ptz,positionrequest)
        elif lov[0].lower() in ["r","ri","rig","righ","right"]:
            move_right(ptz,positionrequest)
        elif lov[0].lower() in ["ul"]:
            move_upleft(ptz,positionrequest)
        elif lov[0].lower() in ["ur"]:
            move_upright(ptz,positionrequest)
        elif lov[0].lower() in ["dl"]:
            move_downleft(ptz,positionrequest)
        elif lov[0].lower() in ["dr"]:
            move_downright(ptz,positionrequest)
        elif lov[0].lower() in ["s","st","sto","stop"]:
            ptz.Stop({'ProfileToken': positionrequest.ProfileToken})
            active = False
        else:
            print("What are you asking?\tI only know, 'up','down','left','right', 'ul' (up left), \n\t\t\t'ur' (up right), 'dl' (down left), 'dr' (down right) and 'stop'")
         
    print("")
    print("Your command: ", end='',flush=True)
       

def find_camera(list_id):
    return camera_ids[int(list_id)]

def find_img(list_id):
    return img_ids[int(list_id)]

def gen_frames(camera_id):
    cam = find_camera(camera_id)  # return the camera access link with credentials. Assume 0?
    cap = VideoStream(cam).start()
    time.sleep(2.0)
    while True:
        try:
            frame = cap.read()

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        except:
            cam = find_camera(camera_id)  # return the camera access link with credentials. Assume 0?
            cap = VideoStream(cam).start()
            time.sleep(2.0)

@app.route('/')
def index():
    return render_template('index.html', cameras_id=len(camera_ids), img_id = len(img_ids))

@app.route('/video_feed/<string:list_id>/', methods=["GET"])
def video_feed(list_id):
    return Response(gen_frames(list_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_img/<string:list_id>/', methods=["GET"])
def get_img(list_id):
    
    return send_from_directory("templates/img/",find_img(list_id))

@app.route('/up', methods=["POST"])
def up():

    move_up(ptz,positionrequest)
    return 'OK'

@app.route('/down', methods=["POST"])
def down():

    move_down(ptz,positionrequest)
    return 'OK'

@app.route('/left', methods=["POST"])
def left():

    move_left(ptz,positionrequest)
    return 'OK'

@app.route('/right', methods=["POST"])
def right():

    move_right(ptz,positionrequest)
    return 'OK'

@app.route('/left_up', methods=["POST"])
def left_up():

    move_upleft(ptz,positionrequest)
    return 'OK'

@app.route('/right_up', methods=["POST"])
def right_up():

    move_upright(ptz,positionrequest)
    return 'OK'

@app.route('/left_down', methods=["POST"])
def left_down():

    move_downleft(ptz,positionrequest)
    return 'OK'

@app.route('/right_down', methods=["POST"])
def right_down():

    move_downright(ptz,positionrequest)
    return 'OK'

@app.route('/zoom_in', methods=["POST"])
def zoom_in():

    Zoom_in(ptz,positionrequest)
    return 'OK'

@app.route('/zoom_out', methods=["POST"]) 
def zoom_out():

    Zoom_out(ptz,positionrequest)
    return 'OK'

@app.route('/home', methods=["POST"])
def home():
    move_home(ptz,homerequest)
    return 'OK'

@app.route('/stop', methods=["POST"])
def stop():
    ptz.Stop({'ProfileToken': positionrequest.ProfileToken})
    return 'OK'

if __name__ == '__main__': 
    setup_move()
    app.run(host='192.168.0.58',port = "7011", debug=False)