from nilearn.image import image as niimage
import os
import matplotlib.pyplot as plt
import numpy as np
import utils as ut
from nilearn import plotting as niplot
from . import display


def ddfnc_state_local_stats(args):
    state, inputs, cache = ut.resolve_args(args)
    cluster_labels = ut.resolve_input('cluster_labels', inputs, cache)
    window_index_file = ut.resolve_input('window_indices', inputs, cache)
    window_indices = np.load(window_index_file)
    remote_centroids = ut.resolve_input('remote_centroids', inputs, cache)
    #subject_sms = ut.resolve_input('subject_sms', inputs, cache)
    k = max(cluster_labels)+1
    subjects = [[] for subject in np.unique(window_indices)]
    for window_index, label in zip(window_indices, cluster_labels):
        subjects[window_index].append(label)
    compiled_subject_stats = [display.statevector_stats(subject, k) for subject in subjects]

    centroid_files = []

    for i, centroid in enumerate(remote_centroids):
        c = display.display_centroid(centroid,
                                     basedir=state['outputDirectory'],
                                     title='Centroid %d' % i)
        centroid_files.append(c)

    #sm_files = []
    # for i, sm in enumerate(subject_sms):
    #    d = display.display_fmri(sm, result_dir=state['outputDirectory'])
    #    sm_files.append(d)

    computation_output = ut.default_computation_output(args)
    computation_output['output'] = dict(
        compiled_subject_stats=compiled_subject_stats,
        centroid_files=centroid_files,
        sm_files=sm_files
    )
    return computation_output
