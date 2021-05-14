from flask import Flask
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for
from flask import Flask, request
import json, logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

# from computer_vision.object_detection import run_with_srobot
from threading import Thread, currentThread
import pickle
import socket
from robot import Robot
from command import Command

# ROBOT_IP = "127.0.0.1"
# ROBOT_PORT = 65431
PORT = 65431
# VIDEO_STREAM = "http://192.168.0.190:8080/video"
VIDEO_STREAM = "http://192.168.0.190:8080/browserfs.html"

logging.getLogger("flask_cors").level = logging.DEBUG

app = Flask(__name__)

CORS(app, resources={r"/robots/": {"origins": "*"}}, supports_credentials=True)
# app.UseCors(CorsOptions.AllowAll)
# CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
# All robots
vRobot1 = {"id": 1, "name": "Vn1", "status": 0}
vRobot2 = {"id": 2, "name": "Vn2", "status": 0}
sRobot1 = {"id": 3, "name": "Swd1", "status": 0}
sRobot2 = {"id": 4, "name": "Swd2", "status": 0}

robotList = []

# ADD ROBOT HERE:
# robotList.append(Robot(len(robotList), "test1", "ROBOT_IP", "ROBOT_PORT", "VIDEO_STREAM","1"))
# robotList.append(vRobot1)
# robotList.append(vRobot2)
# robotList.append(sRobot1)
# robotList.append(sRobot2)

# All pattern
patternList = [
    {"id": 1, "src": "https://quarrymill.com/wp-content/uploads/2019/07/ashlar.png"},
    {"id": 2, "src": "https://quarrymill.com/wp-content/uploads/2019/07/castlerock.png"},
    {"id": 3, "src": "https://quarrymill.com/wp-content/uploads/2019/07/cobblestone.png"},
    {"id": 4, "src": "https://quarrymill.com/wp-content/uploads/2019/07/dimensional-ledgestone.png"},
    {"id": 5, "src": "https://quarrymill.com/wp-content/uploads/2019/07/dimensional-ledgestone.png"},
    {"id": 6, "src": "https://quarrymill.com/wp-content/uploads/2019/07/ashlar.png"},
]

# check trang thai tay (On lifting up or lifting down)
robotArm = {"state": 0}


@app.route("/")
@cross_origin()
def hello_world():
    return "Hello World!"


# getAllRobots
@app.route("/robots")
@cross_origin()
def listAllRobots():
    return jsonify(robots=[robot.to_json() for robot in robotList])


# choose Robot
@app.route("/robots/<int:robot_id>")
@cross_origin()
def chooseRobot(robot_id):
    print(robotList)
    for robot in robotList:
        if robot.id == robot_id:
            # if robot.status != 0:
            #     return make_response(jsonify(ErrorMessage="Robot is using", robot=robot.to_json()), 400)
            # else:
            robot.status = 1
            if robot.is_closed():
                robotList.remove(robot)
                return make_response(jsonify(Message="Cannot create socket"), 400)
            else:
                return make_response(jsonify(Message="Chose robot succesfully", robot=robot.to_json()), 200)

    return make_response(jsonify(ErrorMessage="Not exist robot you chosen"), 400)


# Start working
@app.route("/robots/start/<int:robot_id>")
@cross_origin()
def startRobotWork(robot_id):
    for robot in robotList:
        if robot.id == robot_id:
            if robot.status != 1:
                return make_response(jsonify(ErrorMessage="Wrong status", robot=robot.to_json()), 400)
            else:
                # Start CV control.
                # TODO: Store thread in robot?
                # t = Thread(target=run_with_robot, args=(robot, ))
                # t.start()
                robot.status = 3
                return make_response(jsonify(Message="Start Working", robot=robot.to_json()), 200)

    return make_response(jsonify(ErrorMessage="Robot Not Found"), 400)


# Disconnected
@app.route("/robots/disconnect/<int:robot_id>")
@cross_origin()
def disConnectRobot(robot_id):
    for robot in robotList:
        if robot.id == robot_id:
            if robot.status != 0:
                robot.status = 0
                return make_response(jsonify(message="Disconnected successfully", robot=robot.to_json()), 200)
            else:
                return make_response(jsonify(message="Wrong status", robot=robot.to_json()), 400)
    return make_response(jsonify(ErrorMessage="Robot Not Found"), 400)


# Get all pattern
@app.route("/patterns")
@cross_origin()
def listAllPattern():

    return make_response(jsonify(patern=patternList), 200)


# Choose all pattern
@app.route("/patterns/<int:id>")
@cross_origin()
def choosePattern(id):
    for pattern in patternList:
        if pattern["id"] == id:
            return make_response(jsonify(Message="Successfully", ChosenPattern=pattern["id"]), 200)
    return make_response(jsonify(ErroMessage="Wrong id pattern"), 400)


# Pause un pause
@app.route("/robots/set-pause-status")
@cross_origin()
def pause():
    robot_id = request.args.get("robot_id", None)
    if robot_id is not None:
        robot_id = int(robot_id)
        for robot in robotList:
            if robot.id == robot_id:
                # TODO: close
                # self.
                if robot.status == 2:
                    robot.status = 3
                    return make_response(jsonify(message="UnPause", robot=robot.to_json()), 200)
                elif robot.status == 3:
                    robot.status = 2
                    return make_response(jsonify(message="Pause", robot=robot.to_json()), 200)
                else:
                    return make_response(jsonify(Errormessage="Wrong status", robot=robot.to_json()), 400)
    return make_response(jsonify(ErrorMessage="Robot Not Found"), 400)


# - get infomation of current connected robot
@app.route("/robots/worksprogress")
@cross_origin()
def getWorkProgress():
    robot_id = request.args.get("id", None)
    if robot_id is not None:
        robot_id = int(robot_id)
        for robot in robotList:
            if robot.id == robot_id:
                # Suppose data is data got from socket
                data = {
                    "pattern": 1,
                    "isDone": 0,
                    "startAt": datetime.utcnow(),
                    "stoneDone": 10,
                    "totalStone": 100,
                    "remainTime": datetime.utcnow(),
                }
                return make_response(jsonify(current_work=data), 200)
    return make_response(jsonify(ErrorMessage="Robot Not Found"), 400)


# Remote
@app.route("/robots/remote")
@cross_origin()
def move():
    robot_id = request.args.get("robot_id", None)
    cmd_id = request.args.get("cmd_id", None)
    if robot_id is None:
        return make_response(jsonify(ErrorMessage="Robot Not Found"), 400)
    if cmd_id is None:
        return make_response(jsonify(ErrorMessage="Command Not Found"), 400)
    robot_id = int(robot_id)
    cmd_id = int(cmd_id)
    try:
        cmd = Command(cmd_id)
    except ValueError:
        return make_response(jsonify(ErrorMessage="Command Not Found"), 400)
    for robot in robotList:
        if robot.id == robot_id:
            if robot.is_closed():
                robotList.remove(robot)
                return make_response(jsonify(ErrorMessage="Cannot connect to robot"), 400)
            else:
                robot.conn.sendall(pickle.dumps(cmd))
                return make_response(jsonify(ErrorMessage="Executed"), 200)
    return make_response(jsonify(ErrorMessage="Command not executed"), 400)


def socket_handler(robotList):
    count = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", PORT))
    # s.bind(("runestone2021-server.herokuapp.com", PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print("Connected by", addr[0], addr[1])
        robotList.append(Robot(len(robotList), "test{}".format(count), addr[0], addr[1], VIDEO_STREAM, conn))
        count += 1

if __name__ == "__main__":
    app.debug = False
    t_server = Thread(target=socket_handler, args=(robotList,))
    t_server.daemon = True
    t_server.start()
    app.run()

