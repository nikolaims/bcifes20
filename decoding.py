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


class TemporalFilter:
    def __init__(self, b, a=(1, ), n_channels=None):
        self.b = b
        self.a = a
        if n_channels is None:
            self.zi = np.zeros((max(len(self.b), len(self.a)) - 1,))
        else:
            self.zi = np.zeros((max(len(self.b), len(self.a)) - 1, n_channels))

    def apply(self, chunk):
        x, self.zi = sg.lfilter(self.b, self.a, chunk, zi=self.zi, axis=0)
        return x


class SpatialFilter:
    def __init__(self, weights):
        self.weights = weights

    def apply(self, chunk):
        x = chunk.dot(self.weights)
        return x


class PointFunctionFilter:
    def __init__(self, function):
        self.function = function

    def apply(self, chunk):
        x = self.function(chunk)
        return x


class FilterSequence:
    def __init__(self, filter_sequence):
        self.sequence = filter_sequence

    def apply(self, chunk: np.ndarray):
        for filter_ in self.sequence:
            chunk = filter_.apply(chunk)
        return chunk


if __name__ == '__main__':
    eeg = np.load('data/eeg_example_2_45Hz.npz')
    band = [8, 12]

    filt_freqs = [0, band[0], band[0], band[1], band[1], eeg['fs'] / 2]
    filt_gain = [0, 0, 1, 1, 0, 0]
    b = sg.firwin2(250, filt_freqs, filt_gain, fs=eeg['fs'])

    weights = np.zeros(30)
    weights[0] = 1

    filter_seq = FilterSequence([SpatialFilter(weights), TemporalFilter(b), PointFunctionFilter(np.abs),
                                 TemporalFilter(np.arange(250)/250)])

    import pylab as plt
    plt.plot(np.concatenate([filter_seq.apply(x) for x in np.split(eeg['data'], 10)]))
