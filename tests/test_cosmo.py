import inspect
import os

LOCATION = "/".join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))).split("/")[:-1])
from nose.tools import raises
import sys
sys.path.insert(0, LOCATION)
from hmf.cosmo import Cosmology

def eq(actual, expected):
    return abs(actual - expected) < 0.000001

@raises(ValueError)
def test_silly_parameter():
    c = Cosmology(a_stupid_param=85)
    assert c.a_stupid_param == 85

def test_h_and_H0_same():
    c = Cosmology(h=0.7, H0=70)
    assert c.h == 0.7

def test_h_and_H0_different():
    c = Cosmology(h=0.8, H0=60)
    assert c.h == 0.8 and c.H0 == 80

def test_force_flat_omegav():
    c = Cosmology(force_flat=True, omegav=0.7)
    print c.omegav
    print c.omegam
    assert eq(c.omegav, 0.7) and eq(c.omegam, 0.3)

@raises(AttributeError)
def test_invalid_omegax():
    c = Cosmology(omegab_h2=0.02, omegac=0.25)
    assert c.omegam == 0.3

def test_omegam_only():
    c = Cosmology(omegam=0.3, force_flat=True)
    assert c.omegam == 0.3 and c.omegav == 0.7

@raises(AttributeError)
def test_no_h_input():
    c = Cosmology(omegab_h2=0.02, omegac_h2=0.15)
    assert c.omegab == 0.04

def test_get_non_h_from_h():
    c = Cosmology(omegab_h2=0.02, omegac_h2=0.15, h=0.5)
    print c.omegab, c.omegac, c.omegam
    assert eq(c.omegab, 0.08) and eq(c.omegac, 0.6) and eq(c.omegam, 0.68)

def test_get_h_from_non_h():
    c = Cosmology(omegab=0.05, omegac=0.24, h=0.5)
    assert eq(c.omegab_h2, 0.0125) and eq(c.omegac_h2, 0.06) and eq(c.omegam, 0.29)

def test_force_flat_after():
    c = Cosmology(omegab=0.05, omegac=0.25, force_flat=True)
    assert c.omegav == 0.7 and c.omegak == 0.0

def test_pycamb_dict():
    bits = ["w_lam", "TCMB", "yhe", "reion__redshift", "Num_Nu_massless", "omegab",
            "omegac", "H0", "omegav", "omegak", "omegan", "cs2_lam",
            "scalar_index", "Num_Nu_massive"]
    c = Cosmology(w=-1, t_cmb=2.74, y_he=0.24, z_reion=10, N_nu=3.04, omegab=0.2,
                  omegac=0.25, h=0.7, force_flat=True, omegan=0.0, cs2_lam=-1,
                  n=1, N_nu_massive=0)

    for bit in bits:
        assert bit in c.pycamb_dict()

def test_cosmolopy_dict():
    bits = ["tau", "w", "z_reion", "omega_b_0", "h", "omega_lambda_0",
            "omega_k_0", "omega_n_0", "n", "N_nu", "omega_M_0",
            "sigma_8"]
    c = Cosmology(w=-1, t_cmb=2.74, y_he=0.24, z_reion=10, N_nu=3.04, omegab=0.2,
                  omegac=0.25, h=0.7, force_flat=True, omegan=0.0, cs2_lam=-1,
                  n=1, N_nu_massive=0, tau=0.85, sigma_8=0.8)

    print c.cosmolopy_dict()
    print bits
    for bit in bits:
        assert bit in c.cosmolopy_dict()

@raises(ValueError)
def test_bounds_low():
    c = Cosmology(omegab=0, omegac=0.25)
    assert c.omegab == 0

@raises(ValueError)
def test_bounds_high():
    c = Cosmology(sigma_8=400)
    assert c.sigma_8 == 400
