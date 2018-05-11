import rospy
from audio_common_msgs.msg import AudioData
import pyaudio

import threading
from Queue import Queue
import subprocess
import numpy as np

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                output=True)

class LameDecoder(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.lame = None
        self.setDaemon(True)
        self.subscriber = rospy.Subscriber("/mp3_audio_encoder", AudioData, self.callback)
        self.publisher = rospy.Publisher("/audio", AudioData)

    def callback(self, data):
        received_sample = data.data
        array = np.array(received_sample)
        array.tofile(self.lame.stdin)

    def start(self, *args, **kwargs):
        """
        Start the LAME encoder process
        """
        call = ['lame']
        call.append('--decode')
        call.append('--mp3input')
        call.append('-x')
        # call.append('-t')
        call.extend(["-", "-"])
        print(call)
        self.lame = subprocess.Popen(
            call,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        threading.Thread.start(self, *args, **kwargs)

    def run(self):
        """
        Receive decoded LAME stdout data and process it.
        """
        buffer = ""
        wav_file = open("testjes.wav", "wb")
        while True:
            decoded_std = self.lame.stdout.readline()
            # stream.write(decoded_std)
            self.publisher.publish(decoded_std)
            # buffer += decoded_std
            # print(len(buffer))
            # if len(buffer) > 100000:
            #     buffer = ""
                # stream.write(decoded_std)
                # wav_file.write(decoded_std)



if __name__ == '__main__':
    rospy.init_node('audio_encoder', anonymous=True)

    lame = LameDecoder()
    lame.start()
    rospy.spin()
