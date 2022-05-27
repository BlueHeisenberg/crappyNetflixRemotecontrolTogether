import asyncio
import time
from aiohttp import web
import socketio
import pynput
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl

store = {}

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


def transmit_keys():
    # Start a keyboard listener that transmits keypresses into an
    # asyncio queue, and immediately return the queue to the caller.
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def on_press(key):
        # this callback is invoked from another thread, so we can't
        # just queue.put_nowait(key.char), we have to go through
        # call_soon_threadsafe
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        loop.call_soon_threadsafe(queue.put_nowait, k)
    pynput.keyboard.Listener(on_press=on_press).start()
    return queue


async def main():
    key_queue = transmit_keys()

    client = WebOSClient("192.168.1.75")
    client.connect()

    status = WebOSClient.PROMPTED

    while status != WebOSClient.REGISTERED:
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
                print("Please accept the connect on the TV!")
            elif status == WebOSClient.REGISTERED:
                print("Registration successful!")
        time.sleep(5)

    media = MediaControl(client)

    while True:
        key = await key_queue.get()
        if key == "p":
            print("Sending Play/Pause")
            await sio.emit("play_pause")
            media.play()
        if key == "r":
            print("Sending goto Start")
            await sio.emit("goto_start")
            media.rewind()


async def init_app():
    sio.start_background_task(main)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), port=2003)


@sio.event
def connect():
    print("Client connected!")


@sio.event
def connect_error(data):
    print("Client connection failed!")


@sio.event
def disconnect():
    print("Clients disconnected!")
