import math
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forge import astro, physics  # noqa: E402


class Physics(unittest.TestCase):
    def test_rk4_conserves_energy(self):
        _, drift = physics.double_pendulum(2.1, 2.5, 9.81, 10, 24)
        self.assertLess(drift, 1e-4)

    def test_small_angle_period(self):
        # small-angle double pendulum is regular; just check it stays bounded
        frames, _ = physics.double_pendulum(0.05, 0.05, 9.81, 5, 24)
        self.assertTrue(all(abs(f[3]) < 2.1 for f in frames))

    def test_kepler_exponent(self):
        self.assertAlmostEqual(physics.kepler_period(4, 1, 10) / 10, 8.0)

    def test_drop_lands_and_rests(self):
        ys = physics.drop(0.2, 200, 2600, 0.4, 30, 4)
        self.assertEqual(ys[0], -200)
        self.assertEqual(ys[-1], 0.0)
        self.assertTrue(all(y <= 0 for y in ys))

    def test_persistent_ball_never_settles(self):
        ys = physics.persistent_ball(900, 44, 0.78, 30, 7)
        self.assertLess(min(ys[-60:]), -20)  # still high bounces near the end

    def test_layout_in_bounds(self):
        pos = [[i * 10.0, i * 7.0] for i in range(8)]
        physics.force_layout(pos, [(0, 1), (1, 2), (2, 3)], 400, 300, iters=100)
        self.assertTrue(all(0 <= x <= 400 and 0 <= y <= 300 for x, y in pos))


class Astro(unittest.TestCase):
    def test_julian_day_j2000(self):
        self.assertAlmostEqual(astro.julian_day(datetime(2000, 1, 1, 12, tzinfo=timezone.utc)), 2451545.0)

    def test_equinox_noon_elevation(self):
        # near the March equinox, solar noon elevation ≈ 90 - latitude
        best = max(astro.sun_elevation(datetime(2026, 3, 20, h, m, tzinfo=timezone.utc), *astro.LUCKNOW)
                   for h in range(4, 8) for m in range(0, 60, 5))
        self.assertAlmostEqual(best, 90 - astro.LUCKNOW[0], delta=1.0)

    def test_night_is_negative(self):
        self.assertLess(astro.sun_elevation(datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc), *astro.LUCKNOW), 0)

    def test_moon_reference_phases(self):
        self.assertLess(astro.moon_illumination(astro.moon_age(datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc))), 0.01)
        self.assertGreater(astro.moon_illumination(astro.moon_age(datetime(2000, 1, 21, 4, 40, tzinfo=timezone.utc))), 0.99)


if __name__ == "__main__":
    unittest.main()
