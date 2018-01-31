import pyaudio
import socket
from threading import Thread
import pywt as wt
import numpy as np
import compresor as com

from scipy.fftpack import fft, ifft
import numpy.fft as fourier
from time import time
from PIL import Image
from io import BytesIO
from heapq import merge

frames = []
ITERACIONESDWT = 9

def udpStream():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), ("127.0.0.1", 12345))

    udp.close()

def record(stream, CHUNK):
    while True:
        data = stream.read(CHUNK)
        trama = np.asarray(np.fromstring(data, np.int16))



        real, imaginario = com.trasformada(trama)

        XRN = com.normalizar(real, True)
        XRI = com.normalizar(imaginario, False)

        im_R = com.comprimirImagen(XRN)
        im_I = com.comprimirImagen(XRI)
        imagine = Image.open(BytesIO(im_I.getvalue()))
        reale  = imagine = Image.open(BytesIO(im_R.getvalue()))
        XR = com.denormalizar(list(reale.tobytes()), True)#np.array(imagen)[0])#XRN, True)
        XI = com.denormalizar(list(imagine.tobytes()), False)
        complejo = com.unir(XR, XI)

        lista = []
        otra = []

        for elemento in  range(0, int(len(complejo)/2)):
            lista.append(complejo[elemento])
        for elem in lista:
            otra.append(elem.conjugate())

        for conjugado in otra:
            lista.append(conjugado)
        inversa = fourier.ifft(lista)
        #terminamos de comprimir
                ##Comenzamos a comprimir
        filtrado = com.low_pass_filter(np.int16(inversa.real))
        frames.append(filtrado)

if __name__ == "__main__":
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK,
                    )


    Tr = Thread(target = record, args = (stream, CHUNK,))
    Ts = Thread(target = udpStream)
    Tr.setDaemon(True)
    Ts.setDaemon(True)
    Tr.start()
    Ts.start()
    Tr.join()
    Ts.join()
