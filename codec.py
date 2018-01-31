import numpy as np
import numpy.fft as fourier
from scipy.fftpack import fft, ifft
from PIL import Image
from io import BytesIO


MAX_R = 0
MIN_R = 0
MAX_I = 0
MIN_I = 0

def normalizar(trasformada, real = True):

    global MAX_R, MAX_I, MIN_R, MIN_I
    conjugado = 0
    min_a = 0

    if real:
        MAX_R = np.amax(trasformada)
        MIN_R = np.amin(trasformada)
        min_a = MIN_R
        if(MAX_R != MIN_R):
            conjugado = 255/(MAX_R-MIN_R)
    else:

        MAX_I = np.amax(trasformada)
        MIN_I = np.amin(trasformada)
        min_a = MIN_I
        if(MAX_I != MIN_I):
            conjugado = 255/(MAX_I-MIN_I)

    XRN = []
    for pixel in trasformada:
        XRN.append((pixel-min_a)*conjugado)

    return XRN

def denormalizar(tramaNormalizada, real = True):

    XN = []

    if real:
        for elemento in tramaNormalizada:
            XN.append((elemento * (MAX_R - MIN_R) / 255) + MIN_R)

    else:
        for elemento in tramaNormalizada:
            XN.append((elemento * (MAX_I - MIN_I) / 255) + MIN_I)

    return XN

def trasnformada(trama):
    fft = fourier.fft(trama)
    imaginario = fft.imag
    real       = fft.real
    return (real, imaginario)

def unir(real, imaginario):

    complejo = []

    for r,i in zip(real,imaginario):
        complejo.append(np.complex(r,i))

    return complejo

def comprimirImagen(trama):
    grayscData = np.asarray(trama).reshape(32, 64)
    im = Image.fromarray(np.uint8(grayscData), 'L')
    imBuffer = BytesIO()
    im.save(imBuffer, 'PNG')

    return imBuffer.getvalue()
