#!/usr/bin/env python2.7

import datetime
import argparse
import zmq
import pprint

parser = argparse.ArgumentParser()
parser.add_argument('socket', action='store', default='tcp://127.0.0.1:9797', nargs='?')
args = parser.parse_args()

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(args.socket)
socket.setsockopt(zmq.SUBSCRIBE, '')

print '********************'
print 'Listening for events'
print 'Remote:', args.socket
print '********************'

events = 0

while True:
    msg = socket.recv_json()
    events += 1
    print
    print '---', 'Event', events, 'received on', datetime.datetime.now()
    pprint.pprint(msg)
