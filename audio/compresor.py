from scipy.fftpack import *
import numpy as np
import numpy.fft as fourier
from PIL import Image
from io import BytesIO

MAX_R = 0
MIN_R = 0
MAX_I = 0
MIN_I = 0

def low_pass_filter(x, samples = 20):
  """ fft based brute force low pass filter """
  a = fourier.rfft(x)
  tot = len(a)
  for x in range(tot-samples):
    a[samples + x] = 0.0
  return fourier.irfft(a)

def normalizar(trasformada, real = True):
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

   xrn = []
   for pixel in trasformada:
       xrn.append((pixel-min_a)*conjugado)

   return xrn


def denormalizar(trama_normalizada, real = True):
   xn = []
   if real:
       for elemento in trama_normalizada:
           xn.append((elemento * (MAX_R - MIN_R) / 255) + MIN_R)
   else:
       for elemento in trama_normalizada:
           xn.append((elemento * (MAX_I - MIN_I) / 255) + MIN_I)

   return xn

def transformada(trama):
   fft = fourier.fft(trama)
   imaginario = fft.imag
   real       = fft.real

   return (real, imaginario)

def unir(real, imaginario):
   complejo = []
   for r,i in zip(real,imaginario):
       complejo.append(np.complex(r,i))

   return complejo

def comprimir_imagen(trama):
    # Se crea una imagen a escala de grises a partir de la trama.
    graysc_data = np.asarray(trama).reshape(1, len(trama))
    im = Image.fromarray(np.uint8(graysc_data), 'L')
    im_buffer = BytesIO()
    # Comprimimos la imagen a PNG
    im.save(im_buffer, 'PNG')

    return im_buffer
