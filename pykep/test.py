## Copyright 2023, 2024 Dario Izzo (dario.izzo@gmail.com), Francesco Biscani
## (bluescarni@gmail.com)
##
## This file is part of the pykep library.
##
## This Source Code Form is subject to the terms of the Mozilla
## Public License v. 2.0. If a copy of the MPL was not distributed
## with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest as _ut


def float_abs_error(a: float, b: float):
    return abs(a - b)

class anomaly_conversions_tests(_ut.TestCase):
    def test_m2e(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.m2e(pk.e2m(0.1, 0.1), 0.1), 0.1) < 1e-14)

    def test_m2f(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.m2f(pk.f2m(0.1, 0.1), 0.1), 0.1) < 1e-14)

    def test_f2e(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.f2e(pk.e2f(0.1, 0.1), 0.1), 0.1) < 1e-14)

    def test_n2h(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.n2h(pk.h2n(0.1, 10.1), 10.1), 0.1) < 1e-14)

    def test_n2f(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.n2f(pk.f2n(0.1, 10.1), 10.1), 0.1) < 1e-14)

    def test_f2h(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.f2h(pk.h2f(0.1, 10.1), 10.1), 0.1) < 1e-14)

    def test_f2zeta(self):
        import pykep as pk

        self.assertTrue(float_abs_error(pk.f2zeta(pk.zeta2f(0.1, 10.1), 10.1), 0.1) < 1e-14)

class epoch_test(_ut.TestCase):
    def test_epoch_construction(self):
        import pykep as pk
        import datetime

        ep1 = pk.epoch(0., pk.epoch.julian_type.MJD2000)
        ep2 = pk.epoch(0., pk.epoch.julian_type.MJD)
        ep3 = pk.epoch(0., pk.epoch.julian_type.JD)
        self.assertTrue(ep1.mjd2000 == 0.0)
        self.assertTrue(ep2.mjd == 0.0)
        self.assertTrue(ep3.jd == 0.0)

        ep_py = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        ep4 = pk.epoch(ep_py)
        self.assertTrue(ep4.mjd2000 == 0.0)
        self.assertRaises(TypeError, pk.epoch, datetime.timedelta(1.2))

        self.assertTrue(pk.epoch("2000-01") == ep1)
        self.assertTrue(pk.epoch("2000-01-01") == ep1)
        self.assertTrue(pk.epoch("2000-01-01T00") == ep1)
        self.assertTrue(pk.epoch("2000-01-01T00:00") == ep1)
        self.assertTrue(pk.epoch("2000-01-01T00:00:00") == ep1)


    def test_epoch_operators(self):
        import pykep as pk
        import datetime
        ep1 = pk.epoch(0.)
        ep2 = pk.epoch(1.)
        dt = datetime.timedelta(days=1)
        self.assertTrue(ep1 + dt == ep1 + 1.)
        self.assertTrue(ep2 > ep1)
        self.assertTrue(ep2 >= ep1)
        self.assertTrue(ep1 < ep2)
        self.assertTrue(ep1 <= ep2)
        self.assertTrue(ep1 == ep2 - 1)
        self.assertTrue(ep2 == ep1 + 1)

class my_udpla:
    def eph(self, ep):
        return [[1.,0.,0.],[0.,1.,0.]]
    def get_name(self):
        return "Boh"
    def get_mu_central_body(self):
        return 1.

class my_udpla_malformed1:
    def ephs(self, ep):
        return [[1.,0.,0.],[0.,1.,0.]]
    
class my_udpla_with_optionals:
    def eph(self, ep):
        # Some weird return value just to make it not constant
        return [[ep,0.,0.],[0.,1.,0.]]
    def eph_v(self, eps):
        retval = []
        [retval.extend([item,0.,0,.0,1.,.0]) for item in eps]
        return retval
    def elements(self, ep, el_type ):
        return [1.,2.,3.,4.,5.,6.]
    def period(self, mjd2000):
        return 3.14
    
class planet_test(_ut.TestCase):
    def test_planet_construction(self):
        import pykep as pk

        udpla_cpp = pk.udpla.keplerian(ep = pk.epoch(0), elem = [1.,0.,0.,0.,0.,0.], mu_central_body = 1.)
        udpla_py = my_udpla()
        pla1 = pk.planet(udpla_cpp)
        pla2 = pk.planet(udpla_py)
        # Cannot construct from pk.planet
        self.assertRaises(TypeError, pk.planet, pla1)
        # Cannot construct from instance
        self.assertRaises(TypeError, pk.planet, pk.planet)
        # Cannot construct from malformed udpla
        self.assertRaises(NotImplementedError, pk.planet, my_udpla_malformed1())

    def test_udpla_extraction(self):
        import pykep as pk

        udpla_cpp = pk.udpla.keplerian(ep = pk.epoch(0), elem = [1.,0.,0.,0.,0.,0.], mu_central_body = 1.)
        udpla_py = my_udpla()
        pla1 = pk.planet(udpla_cpp)
        pla2 = pk.planet(udpla_py)
        #self.assertTrue(pla1.extract(pk.udpla.keplerian) is udpla_cpp) questo fails ... perche'?
        self.assertTrue(pla2.extract(my_udpla) is udpla_py)
        self.assertTrue(pla1.extract(my_udpla) is None)
        self.assertTrue(pla2.extract(pk.udpla.keplerian) is None)
        self.assertTrue(pla1.is_(pk.udpla.keplerian))
        self.assertTrue(pla2.is_(my_udpla))
        self.assertTrue(not pla1.is_(my_udpla))
        self.assertTrue(not pla2.is_(pk.udpla.keplerian))

    def test_udpla_getters(self):
        import pykep as pk

        udpla_cpp = pk.udpla.keplerian(ep = pk.epoch(0), elem = [1.,0.,0.,0.,0.,0.], mu_central_body = 1.56, added_params=[3., 2., 2.1])
        udpla_py = my_udpla()
        pla1 = pk.planet(udpla_cpp)
        pla2 = pk.planet(udpla_py)
        self.assertTrue(pla1.get_mu_central_body() == 1.56)
        self.assertTrue(pla1.get_mu_self() == 3.)
        self.assertTrue(pla1.get_radius() == 2.)
        self.assertTrue(pla1.get_safe_radius() == 2.1)
        self.assertTrue(pla2.get_mu_central_body() == 1.)
        self.assertTrue(pla2.get_mu_self() == -1)
        self.assertTrue(pla2.get_radius() == -1)
        self.assertTrue(pla2.get_safe_radius() == -1)

    def test_udpla_optional_methods(self):
        import pykep as pk
        import numpy as np
        # Testing eph_v
        udpla = my_udpla_with_optionals()
        pla = pk.planet(udpla)
        self.assertTrue(pla.elements(0.) == [1.,2.,3.,4.,5.,6.])
        r0, v0 = pla.eph(0.)
        r1, v1 = pla.eph(1.)
        self.assertTrue(np.all(pla.eph_v([0., 1]) == [r0+v0,r1+v1]))
        # Testing period
        self.assertTrue(pla.period() == 3.14)
        self.assertTrue(pla.period(when = 0.) == 3.14)
        self.assertTrue(pla.period(when = pk.epoch(0.)) == 3.14)
        # Testing elements
        self.assertTrue(pla.elements() == [1.,2.,3.,4.,5.,6.])
        self.assertTrue(pla.elements(when = 0.) == [1.,2.,3.,4.,5.,6.])
        self.assertTrue(pla.elements(when = pk.epoch(0.)) == [1.,2.,3.,4.,5.,6.])

class py_udplas_test(_ut.TestCase):
    def test_tle(self):
        import pykep as pk
        from sgp4.api import Satrec
        from sgp4 import exporter
        import numpy as np
        data_file = pk.__path__[0] + "/data/tle.txt"
        file = open(data_file, "r")
        while(True):
            header = file.readline()
            if header == "":
                break
            line1 = file.readline()
            line2 = file.readline()
            udpla = pk.udpla.tle(line1 = line1, line2 = line2)
            pla = pk.planet(udpla)
            ref_epoch = pk.epoch("2023-10")
            rpk,vpk = pla.eph(ref_epoch)
            satellite = Satrec.twoline2rv(line1, line2)
            jd = ref_epoch.mjd2000 + 2451544.5
            jd_i = int(jd)
            jd_fr = jd-jd_i
            e, r, v = satellite.sgp4(jd_i, jd_fr)
            self.assertTrue(np.allclose(np.array(r) * 1000, rpk, equal_nan=True, atol=1e-13))
            self.assertTrue(np.allclose(np.array(v) * 1000, vpk, equal_nan=True, atol=1e-13))







def run_test_suite():
    suite = _ut.TestSuite()
    suite.addTest(anomaly_conversions_tests("test_m2e"))
    suite.addTest(anomaly_conversions_tests("test_m2f"))
    suite.addTest(anomaly_conversions_tests("test_f2e"))
    suite.addTest(anomaly_conversions_tests("test_n2h"))
    suite.addTest(anomaly_conversions_tests("test_n2f"))
    suite.addTest(anomaly_conversions_tests("test_f2h"))
    suite.addTest(anomaly_conversions_tests("test_f2zeta"))
    suite.addTest(planet_test("test_planet_construction"))
    suite.addTest(planet_test("test_udpla_extraction"))
    suite.addTest(planet_test("test_udpla_getters"))
    suite.addTest(planet_test("test_udpla_optional_methods"))
    suite.addTest(epoch_test("test_epoch_construction"))
    suite.addTest(epoch_test("test_epoch_operators"))
    suite.addTest(py_udplas_test("test_tle"))


    test_result = _ut.TextTestRunner(verbosity=2).run(suite)
