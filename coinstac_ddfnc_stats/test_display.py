
import utils as ut
import numpy as np
import os
import display

BASE = os.path.join('..', 'test')

clustering_file = os.path.join(BASE, 'output', 'local0', 'simulatorRun', 'final_full_clustering.npy')

inputs = {}
cache = np.load(clustering_file).item()
cluster_labels = ut.resolve_input('cluster_labels', inputs, cache)
window_index_file = ut.resolve_input('window_indices', inputs, cache)
window_indices = np.load(os.path.join(BASE, window_index_file[1:]))
remote_centroids = ut.resolve_input('remote_centroids', inputs, cache)
# subject_sms = ut.resolve_input('subject_sms', inputs, cache)
k = max(cluster_labels)+1
subjects = [[] for subject in np.unique(window_indices)]
for window_index, label in zip(window_indices, cluster_labels):
    subjects[window_index].append(label)
SV = display.StatevectorStats()
SV.inputs.a = subjects[0]
SV.inputs.k = k
out = SV.run()

#compiled_subject_stats = [display.statevector_stats(subject, k) for subject in subjects]
# compiled_subject_stats = [display.statevector_stats(subject, k) for subject in subjects]
