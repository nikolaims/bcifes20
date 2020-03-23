from pynfb.protocols.ssd.topomap_selector_ica import ICADialog
import numpy as np
from PyQt5.QtWidgets import QApplication

def run_ica(data, channels, fs):
    app = QApplication([])
    ica = ICADialog(data, channels, fs)
    ica.exec_()
    ica_results = {
        'spatial_filter': ica.spatial,
        'spatial_filter_ind': ica.table.get_checked_rows()[0],
        'filters': ica.decomposition.filters,
        'topographies': ica.decomposition.topographies
    }
    return ica_results

if __name__ == "__main__":
    # run ica on data from the latest results folder
    import os
    all_subdirs = ['results/'+d for d in os.listdir('results')]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    probes_npz = np.load(latest_subdir + '/probes.npz')
    fs = int(probes_npz['fs'])
    channels = list(probes_npz['channels'])[:-1]
    data = probes_npz['data'][:, :-1]
    ica_results  = run_ica(data, channels, fs)
    np.savez(latest_subdir + '/ica.npz', **ica_results)