"""
UvA Intelligent Robotics Lab
Author: Janne Spijkervet

Non-frame aware, real-time mp3 encoding of raw audio.
"""

import rospy
from audio_common_msgs.msg import AudioData

import os
import subprocess
import threading
from Queue import Queue
import time
import numpy as np
import base64

import redis

class Record(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        process = subprocess.Popen(['arecord', '-f', 'cd', '-t', 'wav'], stdout=subprocess.PIPE)
        while process.poll() is None:
            sample = process.stdout.readline()
            queue.put(sample)


class Lame(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)

        self.store = redis.Redis()

        self.iqueue = queue

        self.lame = None
        self.finished = False
        self.ready = threading.Semaphore()
        self.encode = threading.Semaphore()
        self.setDaemon(True)

        self.__write_queue = Queue()
        self.__write_thread = threading.Thread(target=self.__lame_write)
        self.__write_thread.setDaemon(True)
        self.__write_thread.start()

        self.publisher = rospy.Publisher('mp3_audio_encoder', AudioData, queue_size=10)

    def start(self, *args, **kwargs):
        """
        Start the LAME encoder process
        """
        call = ['lame']
        call.append('-r')
        call.extend(["-", "-"])
        self.lame = subprocess.Popen(
            call,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        threading.Thread.start(self, *args, **kwargs)

    def run(self):
        """
        Receive LAME process stdout data and process it.
        """
        # mp3_file = open("t.mp3", "wb")
        buffer = ""
        while True:
            encoded_std = self.lame.stdout.readline()
            # self.store.set('mp3_encoded_audio', encoded_std)
            self.publisher.publish(encoded_std)
            
    def __lame_write(self):
        """
        Receive raw audio data from Recorder process and send to LAME stdin.
        """
        while True:
            received_sample = self.iqueue.get()
            array = np.array(received_sample)
            array.tofile(self.lame.stdin)



if __name__ == '__main__':
    rospy.init_node('mp3_audio_encoder', anonymous=True)

    queue = Queue()
    encode_queue = Queue()

    record = Record(queue)
    record.start()

    lame = Lame(queue)
    lame.start()
