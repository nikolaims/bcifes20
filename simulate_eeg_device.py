from settings import NFBLAB_PATH
import sys
sys.path.insert(0, NFBLAB_PATH)

from pynfb.generators import run_eeg_sim

if __name__ == '__main__':
    run_eeg_sim(500, name='EEG_Data')

