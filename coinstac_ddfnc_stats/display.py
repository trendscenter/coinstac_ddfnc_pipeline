from nilearn.image import image as niimage
import os
import matplotlib.pyplot as plt
import numpy as np
import utils as ut
from nilearn import plotting as niplot
from nipype.interfaces.base import File, traits
from nipype.interfaces.matlab import MatlabCommand, MatlabInputSpec
import scipy.io as sio


class StatevectorInputSpec(MatlabInputSpec):
    k = traits.Int(mandatory=True)
    a = traits.List(mandatory=True,
                    desc='List of Files for Back-Reconstruction')


class StatevectorOutputSpec(MatlabInputSpec):
    F = traits.List(exists=True)
    TM = traits.List(exists=True)
    MDT = traits.List(exists=True)
    NT = traits.List(exists=True)
    matlab_output = traits.String(exists=True)


class StatevectorStats(MatlabCommand):
    """ Basic Hello World that displays Hello <name> in MATLAB

    Returns
    -------

    matlab_output : capture of matlab output which may be
                    parsed by user to get computation results

    Example
    --------

    >>> recon = BackRecon()
    >>> recon.inputs.files = ['subject_1.nii', 'subject_2.nii']
    >>> recon.inputs.mask = 'mask.nii'
    >>> recon.inputs.ica_sig = 'gica_signal.mat'
    >>> recon.inputs.ica_varname = 'SM'
    >>> recon.inputs.preproc_type = 'time_mean'
    >>> recon.inputs.algorithm = 'gigica'
    >>> out = recon.run()
    """
    input_spec = StatevectorInputSpec
    output_spec = StatevectorOutputSpec

    def _runner_script(self):
        script = """
           [F, TM, MDT, NT] = statevector_stats(%s, %d);
           save('statevector_results.mat');
        """ % (self.inputs.a,
               self.inputs.k
               )
        #print("MATLAB SCRIPT IS %s" % script)
        return script

    def run(self, **inputs):
        # inject your script
        self.inputs.script = self._runner_script()
        results = super().run(**inputs)
        stdout = results.runtime.stdout
        matresults = sio.loadmat('statevector_results.mat')
        results.outputs.F = matresults.get('F').tolist()
        results.outputs.TM = matresults.get('TM').tolist()
        results.outputs.MDT = matresults.get('MDT').tolist()
        results.outputs.NT = matresults.get('NT').tolist()
        # attach stdout to outputs to access matlab results
        results.outputs.matlab_output = stdout
        return results

    def _list_outputs(self):
        outputs = self._outputs().get()
        print(outputs)
        return outputs


def statevector_stats(a, k):
    # Number of Windows
    number_windows = len(a)
    a = np.array(a)
    # state_fraction_timeraction of time in each state
    state_fraction_time = np.zeros((1, k)).flatten()
    for label in range(k):
        state_fraction_time[label] = (sum(a == label)) / number_windows

    # Numnber of Transitions
    number_transitions = sum(np.abs(np.diff(a)) > 0)

    # Mean Dwell Time in Each State
    mean_dwell_time = np.zeros((1, k)).flatten()
    for jj in range(k):
        start_t = np.where(np.array(np.diff(a == jj) == 1, dtype=int))[0]
        end_t = np.where(np.array(np.diff(a == jj) == -1, dtype=int))[0]
        if a[1] == jj:
            start_t = np.hstack((np.array(0), start_t))
        if a[-1] == jj:
            end_t = np.hstack((np.array(number_windows), end_t))
        print(jj, 'start', start_t, 'end', end_t)
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
