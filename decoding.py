from settings import NFBLAB_PATH
import sys
sys.path.insert(0, NFBLAB_PATH)

import numpy as np
import scipy.signal as sg


class BandPowerDetector:
    def __init__(self, spatial_filter, fs, band, n_taps_bandpass=125, n_taps_ma=100):
        # spatial filter
        self.spatial_filter = spatial_filter
        # bandpass filter
        filt_freqs = [0, band[0], band[0], band[1], band[1], fs/2]
        filt_gain = [0, 0, 1, 1, 0, 0]
        self.b_bandpass = sg.firwin2(n_taps_bandpass, filt_freqs, filt_gain, fs=fs)
        self.zi_bandpass = np.zeros(len(self.b_bandpass)-1)
        #moving average filter
        self.b_ma = np.ones(n_taps_ma) / n_taps_ma
        self.zi_ma = np.zeros(len(self.b_ma)-1)

    def apply(self, chunk):
        x = chunk.dot(self.spatial_filter)
        x, self.zi_bandpass = sg.lfilter(self.b_bandpass, [1, 0], x, zi=self.zi_b)
        x = np.abs(x)
        x, self.zi_ma = sg.lfilter(self.b_ma, [1, 0], x, zi=self.zi_ma)
        return x
