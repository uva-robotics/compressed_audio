from tornado import websocket, web, ioloop

class SocketHandler(websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        """ Initialize the Redis store and framerate monitor. """

        super(SocketHandler, self).__init__(*args, **kwargs)
        self.store = redis.Redis()
        # self._fps = coils.RateTicker((1, 5, 10))
        # self._prev_image_id = None

    def open(self):
        print("Client connected")

    def on_message(self, message):
        audio = self.store.get('mp3_encoded_audio')
        audio_b64 = base64.b64encode(audio)
        print(type(audio_b64))
        self.write_message(audio_b64)


app = web.Application([
    (r'/ws', SocketHandler),
])

app.listen(9000)
ioloop.IOLoop.instance().start()
