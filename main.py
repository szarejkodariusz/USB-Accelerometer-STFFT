#!/usr/bin/env python
from scipy.fftpack import fft, ifft
import serial
import matplotlib.pyplot as plt
import numpy as np
import math

# SERIAL
ser = serial.Serial()
ser.port = "/dev/ttyACM0"  # may be called something different
ser.baudrate = 115200  # may be different
ser.open()

# DATA Nb POINTS
nb_step = 200
nb_of_samples = 3200 # Number of samples per second
data = [] * nb_of_samples
# Sampling rate
fs = 800
# Frequency resolution
df = float(fs) / float(nb_of_samples)
# Nyquist frequency
fn = fs / 2
# Half of frequency vector
if (nb_of_samples%2 == 0):
    frequencies = np.linspace(0, fn, nb_of_samples/2+1)
else:
    frequencies = np.linspace(0, fn, (nb_of_samples+1)/2)

window = np.hamming(nb_of_samples)

def get_data():
    global data
    global ser
    global nb_of_samples
    global window
    data = [] * nb_of_samples
    index = 0
    while index < nb_of_samples:
        response = ser.readline()
        data.extend(response.splitlines())
        index = index + 1
    splited_line = [x.split(',') for x in data]
    ax = [float(x[0]) for x in splited_line]
    ay = [float(x[1]) for x in splited_line]
    az = [float(x[2]) for x in splited_line]
    a = [math.sqrt(x ** 2 + y ** 2 + z ** 2) for (x, y, z) in zip(ax, ay, az)]
    ax = np.multiply(ax, window)
    ay = np.multiply(ay, window)
    az = np.multiply(az, window)
    a = np.multiply(a, window)
    return a, ax, ay, az



# MAIN LOOP
if ser.isOpen():
    print "Port is open!"
    print "Frequency resolution: ", df, " Hz"
    ser.write("FREQ " + str(fs) )
    plt.ion()
    while (True):
        _, _, a, _  = get_data()
        fourier = fft(a)
        # extract    magnitude and only    take    half(fft is mirrored)
        if (nb_of_samples%2 == 0):
            Ymag = np.abs(fourier) / float(nb_of_samples)
            Ymag = Ymag[0:(nb_of_samples / 2 + 1)]
            Ymag[0:-2] = 2.0 * Ymag[0:-2]
            #Yphase = unwrap(angle(Y(1:N / 2 + 1)))
        else:
            Ymag = np.abs(fourier) / float(nb_of_samples)
            Ymag = Ymag[0:(nb_of_samples + 1) / 2]
            Ymag[1:-2] = 2 * Ymag[1:-2]
            #Yphase = unwrap(angle(Y(1:(N + 1) / 2)));
        plt.clf()
        plt.semilogx(frequencies, Ymag, linewidth=2)
        axes = plt.gca()
        axes.grid()
        plt.pause(0.05)
        plt.show()

ser.close()
