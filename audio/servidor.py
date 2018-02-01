import socket
from threading import Thread
import pyaudio
import numpy as np

FORMAT = pyaudio.paInt16
CHUNK = 1024
CHANNELS = 2
RATE = 44100

P = pyaudio.PyAudio()

OUTPUT_STREAM = P.open(format=FORMAT,
                channels = CHANNELS,
                rate = RATE,
                output = True,
                frames_per_buffer = CHUNK,
                )

FRAMES = []

def udp_stream():

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", 12345))

    while True:
        sound_data, addr = udp.recvfrom(CHUNK * CHANNELS *2)
        FRAMES.append(sound_data)

    udp.close()

def play():
    buffer = 10
    while True:
            if len(FRAMES) == buffer:
                while True:
                    if len(FRAMES)>0:
                        data = FRAMES.pop(0)
                        OUTPUT_STREAM.write(np.fromstring(data, np.int16), CHUNK)

def main():
    t_s = Thread(target = udp_stream)
    t_p = Thread(target = play)
    t_s.setDaemon(True)
    t_p.setDaemon(True)
    t_s.start()
    t_p.start()
    t_s.join()
    t_p.join()

if __name__ == '__main__':
    main()
