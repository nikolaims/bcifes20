from settings import NFBLAB_PATH
import sys
sys.path.insert(0, NFBLAB_PATH)

import scipy.signal as sg
from pynfb.generators import run_eeg_sim
import numpy as np
if __name__ == '__main__':
    eeg = np.load('data/eeg_example_2_45Hz.npz')
    run_eeg_sim(eeg['fs'], name='EEG_Data', source_buffer=eeg['data'].T, labels=list(eeg['channels']))

