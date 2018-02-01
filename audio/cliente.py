import socket
from threading import Thread
from io import BytesIO
import pyaudio
import numpy as np
import numpy.fft as fourier
from PIL import Image
import compresor as com

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

P = pyaudio.PyAudio()

INPUT_STREAM = P.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK,
                )
                
FRAMES = []

def upd_stream():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if len(FRAMES) > 0:
            udp.sendto(FRAMES.pop(0).copy(order='C'), ("127.0.0.1", 12345))

    udp.close()

def record():
    while True:
        # RECEPCIÓN DE DATOS
        # Se almacenan los bytes de audio a través del stream de entrada
        data = INPUT_STREAM.read(CHUNK)
        # Se transforman los bytes a enteros de 16 bits
        trama = np.fromstring(data, np.int16)

        # TRANSFORMADA
        # Se obtienen los coeficientes complejos de la FFT
        real, imaginario = com.transformada(trama)

        # CODIFICACIÓN
        # Se normalizan los valores reales e imaginarios para que estén 
        # comprendidos entre 0 y 255
        xrn = com.normalizar(real, True)
        xin = com.normalizar(imaginario, False)

        # COMPRESIÓN
        # Se comprimen los valores normalizados en una imagen equivalente.
        # Estas imágenes son lo que se debería enviar a través del socket,
        # además de los máximos y mínimos reales e imaginarios obtenidos 
        # en la normalización.
        im_r = com.comprimir_imagen(xrn)
        im_i = com.comprimir_imagen(xin)

        # DECOMPRESIÓN
        # Se descomprimen las imágenes.
        reale  = Image.open(BytesIO(im_r.getvalue()))
        imagine = Image.open(BytesIO(im_i.getvalue()))
        
        # DECODIFICACIÓN
        # Se desnormalizan.
        xr = com.denormalizar(list(reale.tobytes()), True)
        xi = com.denormalizar(list(imagine.tobytes()), False)
        # Se unen los valores reales con los imaginarios.
        complejo = com.unir(xr, xi)

        # DESHACER TRANSFORMADA
        # Se realiza la inversa de la FFT para obtener los valores iniciales.
        inversa = fourier.ifft(complejo)
        
        # Incluímos en los FRAMES a enviar a través del socket lo obtenido 
        # en la inversa de la FFT.
        FRAMES.append(inversa.real)


def main():
    t_r = Thread(target = record)
    t_s = Thread(target = upd_stream)
    t_r.setDaemon(True)
    t_s.setDaemon(True)
    t_r.start()
    t_s.start()
    t_r.join()
    t_s.join()

if __name__ == '__main__':
    main()

