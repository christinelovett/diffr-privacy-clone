import numpy as np
from unittest import TestCase

from diffprivlib.mechanisms import Binary


class TestBinary(TestCase):
    def setup_method(self, method):
        self.mech = Binary

    def teardown_method(self, method):
        del self.mech

    def test_class(self):
        from diffprivlib.mechanisms import DPMechanism
        self.assertTrue(issubclass(Binary, DPMechanism))

    def test_inf_epsilon(self):
        mech = self.mech(epsilon=float("inf"), value0="0", value1="1")

        for i in range(1000):
            self.assertEqual(mech.randomise("1"), "1")
            self.assertEqual(mech.randomise("0"), "0")

    def test_complex_epsilon(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon=1 + 2j, value0="0", value1="1")

    def test_string_epsilon(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon="Two", value0="0", value1="1")

    def test_non_string_labels(self):
        with self.assertRaises(TypeError):
            self.mech(epsilon=1, value0=0, value1=1)

    def test_non_string_input(self):
        self.mech = self.mech(epsilon=1, value0="0", value1="1")
        with self.assertRaises(TypeError):
            self.mech.randomise(0)

    def test_empty_label(self):
        with self.assertRaises(ValueError):
            self.mech(epsilon=1, value0="0", value1="")

    def test_same_labels(self):
        with self.assertRaises(ValueError):
            self.mech(epsilon=1, value0="0", value1="0")

    def test_randomise_wrong_label(self):
        mech = self.mech(epsilon=1, value0="1", value1="2")
        with self.assertRaises(ValueError):
            mech.randomise("0")

    def test_distrib_prob(self):
        epsilon = np.log(2)
        runs = 20000
        mech = self.mech(epsilon=epsilon, value0="0", value1="1", random_state=0)
        count = [0, 0]

        for i in range(runs):
            val = mech.randomise("0")
            count[int(val)] += 1

        # print("%d / %d = %f" % (count[0], count[1], count[0] / count[1]))
        self.assertAlmostEqual(count[0] / count[1], np.exp(epsilon), delta=0.1)

    def test_random_state(self):
        mech1 = self.mech(epsilon=1, value0="0", value1="1", random_state=42)
        mech2 = self.mech(epsilon=1, value0="0", value1="1", random_state=42)
        self.assertEqual([mech1.randomise("1") for _ in range(100)], [mech2.randomise("1") for _ in range(100)])

        self.assertNotEqual([mech1.randomise("1")] * 100, [mech1.randomise("1") for _ in range(100)])

        mech2 = self.mech(epsilon=1, value0="0", value1="1", random_state=np.random.RandomState(42))
        self.assertNotEqual([mech1.randomise("1") for _ in range(100)], [mech2.randomise("1") for _ in range(100)])

    def test_repr(self):
        repr_ = repr(self.mech(epsilon=1, value0="0", value1="1"))
        self.assertIn(".Binary(", repr_)

    def test_bias(self):
        self.assertRaises(NotImplementedError, self.mech(epsilon=1, value0="0", value1="1").bias, "0")

    def test_variance(self):
        self.assertRaises(NotImplementedError, self.mech(epsilon=1, value0="0", value1="1").variance, "0")
