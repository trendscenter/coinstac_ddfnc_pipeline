from nilearn.image import image as niimage
import os
import matplotlib.pyplot as plt
import numpy as np
import utils as ut
from nilearn import plotting as niplot


def statevector_stats(a, k):
    # Number of Windows
    number_windows = len(a)
    a = np.array(a)
    # state_fraction_timeraction of time in each state
    state_fraction_time = np.zeros((1, k))
    for label in range(k):
        state_fraction_time[label] = (sum(a == label)) / number_windows

    # Numnber of Transitions
    number_transitions = sum(np.abs(np.diff(a)) > 0)

    # Mean Dwell Time in Each State
    mean_dwell_time = np.zeros((1, k))
    for jj in range(k):
        start_t = np.where(np.diff(a == jj) == 1)
        end_t = np.where(np.diff(a == jj) == -1)
        if a[1] == jj:
            start_t = np.vstack((0, start_t))
        if a[-1] == jj:
            end_t = np.vstack(number_windows)
        mean_dwell_time[jj] = np.mean(end_t - start_t)
        if start_t.size == 0 and end_t.size == 0:
            mean_dwell_time[jj] = 0

    # Full Transition Matrix
    transition_matrix = np.zeros((k, k))
    for t in range(1, number_windows):
        transition_matrix[a[t - 1], a[t]] = transition_matrix[a[t - 1], a[t]] + 1
    for jj in range(k):
        if sum(transition_matrix[jj, :]) > 0:
            transition_matrix[jj, :] = transition_matrix[jj, :] / \
                sum(a[: (number_windows - 1)] == jj)
        else:
            transition_matrix[jj, jj] = 1

    output = dict(
        computation_phase='ddfnc_statevector_stats',
        number_windows=number_windows,
        state_fraction_time=state_fraction_time,
        number_transitions=number_transitions,
        mean_dwell_time=mean_dwell_time,
        transition_matrix=transition_matrix
    )
    return output


def display_centroid(centroid, N=100, basedir='.', title='centroid'):
    centroid_unflat = np.zeros((N, N))
    indices = np.triu_indices(N, 1)
    centroid_unflat[indices] = centroid
    centroid_unflat = centroid_unflat.T
    centroid_unflat[indices] = centroid
    plt.imshow(centroid_unflat)
    plt.title('%s' % title)
    fname = os.path.join(basedir, '%s.png' % title)
    plt.savefig(fname, bbox_inches='tight')
    return fname


def display_fmri(img_path, result_dir='.', NC=100):
    for i in range(NC):
        display = niplot.plot_img(
            niimage.mean_img(img_path),
            draw_cross=False,
            cut_coords=(0, 0, 0)
        )
    img_filename = os.path.basename(img_path)
    save_filename = os.path.join(result_dir, img_filename.replace('.nii', '.png'))
    display.savefig(save_filename)
    return save_filename
