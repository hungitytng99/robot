ROBOT_STATUS = {0: "OFF", 1: "CONNECTED", 2: "PAUSING", 3: "WORKING"}
import socket


class Robot:
    id = int()
    name = str()
    status = int()
    ip = str()
    port = int()
    conn = None

    def __init__(self, id, name, ip, port, camera, conn):
        self.id = id
        self.name = name
        self.ip = ip
        self.port = port
        self.camera = camera
        self.conn = conn

    def is_closed(self):
        try:
            self.conn.sendall(b"test")
            self.conn.sendall(b"test")
            return False
        except Exception as e:
            print(e)
            return True

    def to_json(self):
       return {"id": self.id, "name": self.name, "status": ROBOT_STATUS.get(self.status), "camera": self.camera}


CMD = {
    1: "moveForward",
    2: "turnLeft",
    3: "turnRight",
    4: "moveBackward",
    5: "pickup",
    6: "drop",
    # 7: "rotate",
    # 1: "pickup",
    # 1: "drop",
}
