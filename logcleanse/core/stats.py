# logcleanse/core/stats.py
import math
from typing import Optional

class RunningStats:
    """
    Numerically stable online computation of mean and sample variance
    using Welford's Algorithm.
    """
    __slots__ = ("_count", "_mean", "_m2")

    def __init__(self) -> None:
        self._count: int = 0
        self._mean: float = 0.0
        self._m2: float = 0.0  # Sum of squared deviations from the running mean

    def update(self, val: float) -> None:
        """Updates internal state with a new observation in O(1) time."""
        self._count += 1
        delta = val - self._mean
        self._mean += delta / self._count
        delta2 = val - self._mean
        self._m2 += delta * delta2

    @property
    def count(self) -> int:
        return self._count

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def sample_variance(self) -> float:
        """Returns unbiased sample variance (N - 1 denominator)."""
        return self._m2 / (self._count - 1) if self._count > 1 else 0.0

    @property
    def population_variance(self) -> float:
        """Returns population variance (N denominator)."""
        return self._m2 / self._count if self._count > 0 else 0.0

    @property
    def std_dev(self) -> float:
        return math.sqrt(self.sample_variance)