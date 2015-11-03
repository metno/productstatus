import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:9797")
socket.setsockopt(zmq.SUBSCRIBE, '')

while True:
    print "Listening..."
    msg = socket.recv_json()
    print "Modelstatus msg:%s" % (msg)
