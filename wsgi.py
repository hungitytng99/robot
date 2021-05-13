from app.main import *
from threading import Thread, currentThread
if __name__ == "__main__":
    app.debug = False
    t_server = Thread(target=socket_handler, args=(robotList,))
    t_server.daemon = True
    t_server.start()
    app.run()