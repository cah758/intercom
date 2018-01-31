from scipy.fftpack import *
import numpy as np
import numpy.fft as fourier
from numpy import fft
from time import time
from PIL import Image
from io import BytesIO

max_r = 0
min_r = 0
max_i = 0
min_i = 0

def low_pass_filter(x, samples = 20):
  """ fft based brute force low pass filter """
  a = fft.rfft(x)
  tot = len(a)
  for x in range(tot-samples):
    a[samples + x] = 0.0
  return fft.irfft(a)

def normalizar(trasformada, real = True):

   global max_r, max_i, min_r, min_i

   conjugado = 0
   min_a = 0

   if real:
       max_r = np.amax(trasformada)
       min_r = np.amin(trasformada)
       min_a = min_r
       if(max_r != min_r):
           conjugado = 255/(max_r-min_r)
   else:

       max_i = np.amax(trasformada)
       min_i = np.amin(trasformada)
       min_a = min_i
       if(max_i != min_i):
           conjugado = 255/(max_i-min_i)

   XRN = []
   for pixel in trasformada:
       XRN.append((pixel-min_a)*conjugado)

   return XRN


def denormalizar(tramaNormalizada, real = True):

   XN = []

   if real:

       for elemento in tramaNormalizada:

           XN.append((elemento * (max_r - min_r) / 255) + min_r)

   else:

       for elemento in tramaNormalizada:

           XN.append((elemento * (max_i - min_i) / 255) + min_i)


   return XN


def trasformada(trama):
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
   dimension = len(trama)/2

   grayscData = np.asarray(trama).reshape(1, len(trama))
   im = Image.fromarray(np.uint8(grayscData), 'L')
   #im = Image.fromarray(np.asarray(trama).reshape(1,len(trama)), mode='L')
   #print('--------------------------------------------------')
   #print('TRAMA')
   #print('--------------------------------------------------')
   #print(trama)

   imBuffer = BytesIO()

   im.save(imBuffer, 'PNG')

   #im.show()
   return imBuffer #im
