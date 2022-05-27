import win32api
import time
import socketio

from win32con import *

sio = socketio.Client()
sio.connect("http://localhost:2003")

@sio.on("goto_start")
def go_to_start():
    print("Going to start")
    time.sleep(3)
    for x in range(0, 20):
        time.sleep(0.1)
        win32api.keybd_event(VK_LEFT, 0, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(1)

@sio.on("play_pause")
def play_pause():
    print("Play/Pause")
    win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)


@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")