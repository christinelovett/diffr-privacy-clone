import numpy as np
from unittest import TestCase

from diffprivlib.mechanisms import Staircase


class TestStaircase(TestCase):
    def setup_method(self, method):
        self.mech = Staircase

    def teardown_method(self, method):
        del self.mech

    def test_class(self):
        from diffprivlib.mechanisms import DPMechanism
        self.assertTrue(issubclass(Staircase, DPMechanism))

    def test_zero_sensitivity(self):
        mech = self.mech(epsilon=1, gamma=0.5, sensitivity=0)

        for i in range(1000):
            self.assertAlmostEqual(mech.randomise(1), 1)

    def test_neg_epsilon(self):
        with self.assertRaises(ValueError):
            self.mech(epsilon=-1, sensitivity=1, gamma=0.5)

    def test_complex_epsilon(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon=1 + 2j, sensitivity=1, gamma=0.5)

    def test_string_epsilon(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon="Two", sensitivity=1, gamma=0.5)

    def test_non_zero_delta(self):
        mech = self.mech(epsilon=1, sensitivity=1, gamma=0.5)
        mech.delta = 0.5

        with self.assertRaises(ValueError):
            mech.randomise(1)

    def test_bad_gamma(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon=1, sensitivity=1, gamma="1")

        with self.assertRaises(ValueError):
            self.mech(epsilon=1, sensitivity=1, gamma=-1)

        with self.assertRaises(ValueError):
            self.mech(epsilon=1, sensitivity=1, gamma=1.1)

    def test_default_gamma(self):
        mech = self.mech(epsilon=1, sensitivity=1)
        self.assertTrue(mech._check_all(1))
        self.assertTrue(0 <= mech.gamma <= 1.0)

    def test_non_numeric(self):
        mech = self.mech(epsilon=1, sensitivity=1, gamma=0.5)
        with self.assertRaises(TypeError):
            mech.randomise("Hello")

    def test_zero_median_prob(self):
        mech = self.mech(epsilon=1, sensitivity=1, gamma=0.5, random_state=0)
        vals = []

        for i in range(10000):
            vals.append(mech.randomise(0))

        median = float(np.median(vals))
        self.assertAlmostEqual(np.abs(median), 0, delta=0.1)

    def test_neighbors_prob(self):
        epsilon = 1
        runs = 10000
        mech = self.mech(epsilon=epsilon, sensitivity=1, gamma=0.5, random_state=0)
        count = [0, 0]

        for i in range(runs):
            val0 = mech.randomise(0)
            if val0 <= 0:
                count[0] += 1

            val1 = mech.randomise(1)
            if val1 <= 0:
                count[1] += 1

        # print("0: %d; 1: %d" % (count[0], count[1]))
        self.assertGreater(count[0], count[1])
        self.assertLessEqual(count[0] / runs, np.exp(epsilon) * count[1] / runs + 0.1)

    def test_random_state(self):
        mech1 = self.mech(epsilon=1, sensitivity=1, gamma=0.5, random_state=42)
        mech2 = self.mech(epsilon=1, sensitivity=1, gamma=0.5, random_state=42)
        self.assertEqual([mech1.randomise(0) for _ in range(100)], [mech2.randomise(0) for _ in range(100)])

        self.assertNotEqual([mech1.randomise(0)] * 100, [mech1.randomise(0) for _ in range(100)])

        rng = np.random.RandomState(0)
        mech1 = self.mech(epsilon=1, sensitivity=1, gamma=0.5, random_state=rng)
        mech2 = self.mech(epsilon=1, sensitivity=1, gamma=0.5, random_state=rng)
        self.assertNotEqual([mech1.randomise(0) for _ in range(100)], [mech2.randomise(0) for _ in range(100)])

    def test_repr(self):
        repr_ = repr(self.mech(epsilon=1, sensitivity=1, gamma=0.5))
        self.assertIn(".Staircase(", repr_)

    def test_bias(self):
        self.assertEqual(0.0, self.mech(epsilon=1, sensitivity=1, gamma=0.5).bias(0))

    def test_variance(self):
        self.assertRaises(NotImplementedError, self.mech(epsilon=1, sensitivity=1).variance, 0)
