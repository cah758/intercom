import pyaudio
import socket
from threading import Thread
import numpy as np
import pywt as wt
import scipy   
from scipy.signal import firwin
from scipy.signal import lfilter
from io import BytesIO
import codec as comp
import matplotlib.pyplot as plt

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
ITERACIONESDWT = 9
FRAMES_TO_SEND = []
FRAMES_TO_PLAY = []

P = pyaudio.PyAudio()

INPUT_STREAM = P.open(format = FORMAT,
            channels = CHANNELS,
            rate = RATE,
            input = True,
            frames_per_buffer = CHUNK,
            )

OUTPUT_STREAM = P.open(format = FORMAT,
            channels = CHANNELS,
            rate = RATE,
            output = True,
            frames_per_buffer = CHUNK,
            )


def udpSenderStream():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #while True:
        #if len(FRAMES_TO_SEND) > 0:
            #udp.sendto(FRAMES_TO_SEND.pop(0), ("127.0.0.1", 12345))

    udp.close()

def udpReceiverStream():

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", 12345))

    #while True:
        #soundData, addr = udp.recvfrom(CHUNK * CHANNELS *2)
        #FRAMES_TO_PLAY.append(soundData)

    udp.close()

def record(stream):
    while True:
        data = stream.read(CHUNK)

        #x = np.arange(0, 2048)
        #plt.plot(x, np.fromstring(data, np.int16), linewidth=2, linestyle="-", c="b")
        #plt.show()
        #plt.close()

        #print('--------------------------------------------------')
        #print("DATA RECORDED")
        #print('--------------------------------------------------')
        #print(np.fromstring(data, np.int16))        

        real, imaginaria = comp.trasnformada(np.fromstring(data, np.int16))
        xrn = comp.normalizar(real, True)
        xin = comp.normalizar(imaginaria, False)
                
        imagR = comp.comprimirImagen(xrn)
        imagI = comp.comprimirImagen(xin)

        #FRAMES.append(imagR)
        #FRAMES.append(imagI)

        imagRObtenida = comp.Image.open(BytesIO(imagR))
        imagIObtenida = comp.Image.open(BytesIO(imagI))

        xr = comp.denormalizar(imagRObtenida.getdata(), True)
        xi = comp.denormalizar(imagIObtenida.getdata(), False)
        complejo = comp.unir(xr, xi)
        inversa = comp.fourier.ifft(complejo)
        print(np.int16(inversa.real))
        # Esto es trampa
        FRAMES_TO_PLAY.append(np.int16(inversa.real))

        #print('--------------------------------------------------')
        #print("DATA DECODED")
        #print('--------------------------------------------------')
        #print(inversa.real) 
        #input()

def play(stream):
    BUFFER = 10
    while True:
            #if len(FRAMES_TO_PLAY) == BUFFER:
                while True:
                    if len(FRAMES_TO_PLAY) > 0:
                        # POR AHORA EL AUDIO A REPRODUCIR LO COGEMOS DIRECTAMENTE
                        # DEL INVERSA.REAL QUE SE DECODIFICA ANTES DE ENVIARLO A 
                        # TRAVÉS DE LA RED
                        audioData = FRAMES_TO_PLAY.pop(0).copy(order='C')
                        
                        # FILTER 1
                        # spell out the args that were passed to the Matlab function
                        N = 10
                        Fc = 40
                        Fs = 1600
                        # provide them to firwin
                        h = scipy.signal.firwin(numtaps=N, cutoff=40, nyq=Fs/2)
                        # 'x' is the time-series data you are filtering
                        audioData1 = scipy.signal.lfilter(h, 1.0, audioData)

                        # FILTER 2
                        #n = 15  # the larger n is, the smoother curve will be
                        #b = [1.0 / n] * n
                        #a = 1
                        #audioData2 = lfilter(b, a, audioData)                        
                        
                        # PLOTS
                        #x = np.arange(0, 2048)
                        
                        #plt.plot(x, audioData1, linewidth=2, linestyle="-", c="b")
                        #plt.show()
                        #plt.close()

                        #plt.plot(x, audioData2, linewidth=2, linestyle="-", c="b")
                        #plt.show()
                        #plt.close()

                        stream.write(audioData1, CHUNK)
                        #print('--------------------------------------------------')
                        #print("DATA RECEIVED")
                        #print('--------------------------------------------------')
                        #print(audioData)
                        #input()


def main():
    t_r = Thread(target = record, args = (INPUT_STREAM,))
    t_p = Thread(target = play, args=(OUTPUT_STREAM,))
    t_us = Thread(target = udpSenderStream)
    t_ur = Thread(target = udpReceiverStream)
    t_r.setDaemon(True)
    t_p.setDaemon(True)
    t_us.setDaemon(True)
    t_ur.setDaemon(True)
    t_r.start()
    t_p.start()
    t_us.start()
    t_ur.start()
    t_r.join()
    t_p.join()
    t_us.join()
    t_ur.join()


if __name__ == '__main__':
    main()