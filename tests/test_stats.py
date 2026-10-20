# tests/test_stats.py
import unittest
from logcleanse.core.stats import RunningStats

class TestWelfordStats(unittest.TestCase):
    def test_numerical_stability(self):
        """Tests that adding huge offsets does not destroy sample variance."""
        stats = RunningStats()
        offset = 1e9  # 1,000,000,000
        values = [offset + 1.0, offset + 2.0, offset + 3.0]

        for v in values:
            stats.update(v)

        # Expected sample variance for [1, 2, 3] is exactly 1.0
        self.assertAlmostEqual(stats.sample_variance, 1.0, places=5)
        self.assertAlmostEqual(stats.mean, offset + 2.0, places=5)

    def test_single_value_edge_case(self):
        stats = RunningStats()
        stats.update(42.0)
        self.assertEqual(stats.count, 1)
        self.assertEqual(stats.sample_variance, 0.0)

if __name__ == "__main__":
    unittest.main()