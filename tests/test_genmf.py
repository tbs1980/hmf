'''
This module contains a number of tests that check hmf's results against those of genmf and/or CAMB.

Firstly we test transfer functions/power spectra against the output from CAMB to make sure we
are producing them correctly (with pycamb within hmf). We also check the normalisation of the 
power spectrum done with hmf vs. genmf.

Then we check results for sigma, lnsigma, and the differential and cumulative mass functions against
genmf using two different methods. The first is to produce a power spectrum straight from CAMB to use
in genmf (we have to modify the first and last values so that genmf can actually use it), while using
a generated power spectrum from hmf (with same parameters) within hmf. The second is to use the same
generated power from hmf in both genmf and hmf. These should be equivalent of course, but this is a 
check. 

We then also check the effects of redshift (z=2) on all above quantities.

The data files in the data/ directory are the following:
ST_0 etc :: output from genmf with given fit and redshift, produced with default cosmology here
hmf_power :: the output (normalised) power spectrum from hmf, between exp(-21), exp(21)
camb_power :: the output (un-normalised) power spec from camb with parameters as set here. [CAMB VERSION MAR13]
params.ini :: the params.ini file input to CAMB for all camb results (just for legacy)
genmf_power :: the power spectrum (normalised) produced by genmf

To be more explicit, the power spectrum in all cases is produced with the following parameters:

        self._transfer_cosmo = {"w_lam"    :-1,
                               "omegab"   : 0.05,
                               "omegac"   : 0.25,
                               "omegav"   : 0.7,
                               "omegan"   : 0.0,
                               "H0"       : 70,
                               'cs2_lam'  : 1,
                               'TCMB'     : 2.725,
                               'yhe'      : 0.24,
                               'Num_Nu_massless' : 3.04,
                               'reion__redshift': 10.3,
                               'reion__optical_depth': 0.085
                               }

        self._extra_cosmo = {"sigma_8":0.8,
                            "n":1,
                            "delta_c":1.686,
                            "crit_dens":27.755 * 10 ** 10
                            }

        self._transfer_options = {'Num_Nu_massive'  : 0,
                                 'reion__fraction' :-1,
                                 'reion__delta_redshift' : 1.5,
                                 'Scalar_initial_condition' : 1,
                                 'scalar_amp'      : 1,
                                 'scalar_running'  : 0,
                                 'tensor_index'    : 0,
                                 'tensor_ratio'    : 1,
                                 'lAccuracyBoost' : 1,
                                 'lSampleBoost'   : 1,
                                 'AccuracyBoost'  : 1,
                                 'WantScalars'     : True,
                                 'WantTensors'     : False,
                                 'reion__reionization' : True,
                                 'reion__use_optical_depth' : True,
                                 'w_perturb'      : False,
                                 'DoLensing'       : False,
                                 'transfer__k_per_logint': 50,
                                 'transfer__kmax':10}
'''
#===============================================================================
# Some Imports
#===============================================================================
import numpy as np
from hmf import MassFunction
# from scipy.interpolate import InterpolatedUnivariateSpline as spline
import inspect
import os

LOCATION = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#=======================================================================
# Some general functions used in tests
#=======================================================================
def rms_diff(vec1, vec2, tol):
    mask = np.logical_and(np.logical_not(np.isnan(vec1)), np.logical_not(np.isnan(vec2)))
    vec1 = vec1[mask]
    vec2 = vec2[mask]
    err = np.sqrt(np.mean(((vec1 - vec2) / vec2) ** 2))
    print "RMS Error: ", err, "(> ", tol, ")"
    return err < tol

def max_diff_rel(vec1, vec2, tol):
    mask = np.logical_and(np.logical_not(np.isnan(vec1)), np.logical_not(np.isnan(vec2)))
    vec1 = vec1[mask]
    vec2 = vec2[mask]
    err = np.max(np.abs((vec1 - vec2) / vec2))
    print "Max Diff: ", err, "(> ", tol, ")"
    return err < tol

def max_diff(vec1, vec2, tol):
    mask = np.logical_and(np.logical_not(np.isnan(vec1)), np.logical_not(np.isnan(vec2)))
    vec1 = vec1[mask]
    vec2 = vec2[mask]
    err = np.max(np.abs((vec1 - vec2)))
    print "Max Diff: ", err, "(> ", tol, ")"
    return err < tol

#===============================================================================
# The Test Classes
#===============================================================================
class TestGenMF(object):
    def check_col(self, pert, fit, redshift, origin, col):
        """ Able to check all columns only dependent on base cosmology (not fit) """


        data = np.genfromtxt(LOCATION + "/data/" + fit + '_' + str(int(redshift)) + '_' + origin)[::-1][400:1201]

        # We have to do funky stuff to the data if its been cut by genmf
        if col is "sigma":
            assert max_diff_rel(pert.sigma, data[:, 5], 0.01)
        elif col is "lnsigma":  # We just do diff on this one because it passes through 0
            assert max_diff(pert.lnsigma, data[:, 3], 0.01)
        elif col is "n_eff":
            assert max_diff_rel(pert.n_eff, data[:, 6], 0.01)
        elif col is "dndlog10m":
            assert rms_diff(pert.dndlog10m, 10 ** data[:, 1], 0.02)
        elif col is "fsigma":
            assert rms_diff(pert.fsigma, data[:, 4], 0.01)
        elif col is "ngtm":
            assert rms_diff(pert.ngtm, 10 ** data[:, 2], 0.05)

    def test_sigmas(self):
        hmf = MassFunction(M=np.linspace(7, 15, 801), omegab=0.05, omegac=0.25,
                            omegav=0.7, sigma_8=0.8, n=1, H0=70.0,
                            lnk=np.linspace(-21, 21, 500), transfer__kmax=10,
                            transfer__k_per_logint=50, mf_fit='ST', z=0.0)
        for redshift in [0.0, 2.0]:
            hmf.update(z=redshift)
            for origin in ['camb', 'hmf']:
                for col in ['sigma', 'lnsigma', 'n_eff']:
                    yield self.check_col, hmf, "ST", redshift, origin, col

    def test_fits(self):
        hmf = MassFunction(M=np.linspace(7, 15, 801), omegab=0.05, omegac=0.25,
                           omegav=0.7, sigma_8=0.8, n=1, H0=70.0,
                           lnk=np.linspace(-21, 21, 500), transfer__kmax=10,
                           transfer__k_per_logint=50, mf_fit='ST', z=0.0)
        for redshift in [0.0, 2.0]:
            hmf.update(z=redshift)
            for fit in ["ST", "PS", "Reed03", "Warren", "Jenkins", "Reed07"]:
                hmf.update(mf_fit=fit)
                for origin in ['camb', 'hmf']:
                    for col in ['dndlog10m', 'ngtm', 'fsigma']:
                        yield self.check_col, hmf, fit, redshift, origin, col

