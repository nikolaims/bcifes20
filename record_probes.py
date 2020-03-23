from settings import NFBLAB_PATH
import sys
sys.path.insert(0, NFBLAB_PATH)

import os
import json
import numpy as np
from datetime import datetime
from pynfb.inlets.lsl_inlet import LSLInlet
from find_ica_filter import run_ica


# parse sys args
if '-s' in sys.argv:
    exp_settings_path = sys.argv[sys.argv.index('-s')+1]
else:
    exp_settings_path = 'exp_settings_example.json'
    print('There is no exp-settings provided. Using "exp_settings_example.json"')

# load experiment settings
with open(exp_settings_path) as f:
    exp_settings = json.loads(f.read())

# create results folder
timestamp_str = datetime.strftime(datetime.now(), '%m-%d_%H-%M-%S')
results_path = 'results/{}_{}/'.format(exp_settings['exp_name'], timestamp_str)
os.makedirs(results_path)

# connect to LSL stream
inlet = LSLInlet(name=exp_settings['lsl_stream_name'])
channels = inlet.get_channels_labels()
n_channels = len(channels)
fs = int(inlet.get_frequency())

# prepare recording utils
block_durations = [exp_settings['blocks'][block_name]['duration'] for block_name in exp_settings['sequence']]
n_seconds = sum(block_durations)
buffer = np.empty((n_seconds*fs + 100*fs, n_channels + 1))
n_samples_received = 0

# record data
for block_name in exp_settings['sequence']:
    print(block_name)
    n_samples = fs * exp_settings['blocks'][block_name]['duration']
    block_id = exp_settings['blocks'][block_name]['id']
    n_samples_received_in_block = 0
    while n_samples_received_in_block < n_samples:
        chunk, t_stamp = inlet.get_next_chunk()
        if chunk is not None:
            n_samples_in_chunk = len(chunk)
            buffer[n_samples_received:n_samples_received + n_samples_in_chunk, :-1] = chunk
            buffer[n_samples_received:n_samples_received + n_samples_in_chunk, -1] = block_id
            n_samples_received_in_block += n_samples_in_chunk
            n_samples_received += n_samples_in_chunk

# save recorded data
recorded_data = buffer[:n_samples_received]
np.savez(results_path + 'probes.npz', data=recorded_data, channels=channels + ['STIM'], fs=fs)

# ica
ica_results = run_ica(recorded_data[:, :-1], channels, fs)
np.savez(results_path + 'ica.npz', **ica_results)
