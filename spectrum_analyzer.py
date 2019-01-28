#!/usr/bin/env python
# encoding: utf-8

## Module infomation ###
# Python (3.4.4)
# numpy (1.10.2)
# PyAudio (0.2.9)
# matplotlib (1.5.1)
# All 32bit edition
########################

import numpy as np
import matplotlib.pyplot as plt
import pyaudio
CHANNELS = 1
RATE = 44100
CHUNK = 1024
START = 0
N = 1024
framespacing = RATE / N
lowcut = int(250 / framespacing)
midlowcut = int(500 / framespacing)
midcut = int(2000 / framespacing)
midhighcut = int(4000 / framespacing)
highcut = int(20000 / framespacing)
lowaven = lowcut
midlowaven = midlowcut - lowcut
midaven = midcut - midlowcut
midhighaven = midhighcut - midcut
highaven = highcut - midhighcut
print (framespacing,
       'lowcut', lowcut, (int(lowcut) * framespacing),
       'midlowcut', midlowcut, (int(midlowcut) * framespacing),
       'midcut', midcut, (int(midcut) * framespacing),
       'midhighcut', midhighcut, (int(midhighcut) * framespacing),
       'highcut', highcut, (int(highcut) * framespacing),
       'averagers', lowaven, midlowaven, midaven, midhighaven, highaven)
wave_x = 0
wave_y = 0
spec_x = 0
spec_y = 0
data = []

class SpectrumAnalyzer:
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    START = 0
    N = 1024

    wave_x = 0
    wave_y = 0
    spec_x = 0
    spec_y = 0
    data = []


    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format = self.FORMAT,
            channels = self.CHANNELS,
            rate = self.RATE,
            input = True,
            output = False,
            frames_per_buffer = self.CHUNK)

        # Main loop
        # self.loop()

    def loop(self):
        try:
            while True:
                self.data = self.audioinput()
                self.fft()
                self.graphplot()
        except KeyboardInterrupt:
            self.pa.close()
        print("End...")

    def one_run(self, bandvals):
            self.data = self.audioinput()
            fivebandvals = self.fft(bandvals)
            # self.graphplot()
            return fivebandvals

    def audioinput(self):
        ret = self.stream.read(self.CHUNK, exception_on_overflow=False)
        ret = np.fromstring(ret, np.float32)
        return ret

    def fft(self, bandvals):
        self.wave_x = range(self.START, self.START + self.N)
        self.wave_y = self.data[self.START:self.START + self.N]
        self.spec_x = np.fft.fftfreq(self.N, d = 1.0 / self.RATE)
        y = np.fft.fft(self.data[self.START:self.START + self.N])
        self.spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
        sum1 = 0
        sum2 = 0
        sum3 = 0
        sum4 = 0
        sum5 = 0

        for s in range(0, lowcut):
            sum1 = self.spec_y[s] + sum1
            s += 1
        for s in range(lowcut, midlowcut):
            sum2 = self.spec_y[s] + sum2
            s += 1
        for s in range(midlowcut, midcut):
            sum3 = self.spec_y[s] + sum3
            s += 1
        for s in range(midcut, midhighcut):
            sum4 = self.spec_y[s] + sum4
            s += 1
        for s in range(midhighcut, highcut):
            sum5 = self.spec_y[s] + sum5
            s += 1

        ave1 = int(sum1 / lowaven * 15)
        ave2 = int(sum2 / midlowaven * 15)
        ave3 = int(sum3 / midaven * 30)
        ave4 = int(sum4 / midhighaven * 30)
        ave5 = int(sum5 / highaven * 20)

        bandvals = [ave1, ave2, ave3, ave4, ave5]
        print bandvals
        return bandvals

    def graphplot(self):
        plt.clf()
        # wave
        plt.subplot(311)
        plt.plot(self.wave_x, self.wave_y)
        plt.axis([self.START, self.START + self.N, -0.5, 0.5])
        plt.xlabel("time [sample]")
        plt.ylabel("amplitude")
        #Spectrum
        plt.subplot(312)
        plt.plot(self.spec_x, self.spec_y, marker= 'o', linestyle='-')
        plt.axis([0, self.RATE / 2, 0, 50])
        plt.xlabel("frequency [Hz]")
        plt.ylabel("amplitude spectrum")
        #Pause
        plt.pause(.001)

if __name__ == "__main__":
    spec = SpectrumAnalyzer()
    # print data
    # data = spec.one_run(bandvals=data)
    # print data