from pynfb.protocols.ssd.topomap_selector_ica import ICADialog
from pynfb.protocols.signals_manager.band_selector import BandSelectorWidget

import numpy as np
import scipy.signal as sg
from PyQt5.QtWidgets import QApplication

def run_ica_and_select_band(data, channels, fs):
    app = QApplication([])
    ica = ICADialog(data, channels, fs)
    ica.exec_()
    band = select_band(data.dot(ica.spatial), fs)
    results = {
        'spatial_filter': ica.spatial,
        'spatial_filter_ind': ica.table.get_checked_rows()[0],
        'filters': ica.decomposition.filters,
        'topographies': ica.decomposition.topographies,
        'band': band
    }
    return results

def select_band(x, fs):
    f, pxx = sg.welch(x, fs, nperseg=2*fs, nfft=4*fs)
    return BandSelectorWidget.select(f, pxx)

if __name__ == "__main__":
    # run ica on data from the latest results folder
    import os
    all_subdirs = ['results/'+d for d in os.listdir('results')]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    probes_npz = np.load(latest_subdir + '/probes.npz')
    fs = int(probes_npz['fs'])
    channels = list(probes_npz['channels'])[:-1]
    data = probes_npz['data'][:, :-1]
    results  = run_ica_and_select_band(data, channels, fs)
    np.savez(latest_subdir + '/ica.npz', **results)