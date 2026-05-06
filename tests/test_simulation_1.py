import numpy as np
import pytest
from src.simulations.simulation_1 import generate_walk


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def small_walk():
    np.random.seed(42)
    return generate_walk(100)


@pytest.fixture
def large_ensemble():
    """10,000 independent walks — enough for tight statistical assertions."""
    np.random.seed(0)
    return np.array([generate_walk(500) for _ in range(10_000)])


# ── Output structure ──────────────────────────────────────────────────────────

class TestOutputStructure:
    def test_returns_ndarray(self, small_walk):
        assert isinstance(small_walk, np.ndarray)

    def test_length(self, small_walk):
        assert len(small_walk) == 100

    @pytest.mark.parametrize("n", [1, 10, 100, 500])
    def test_length_parametrised(self, n):
        assert len(generate_walk(n)) == n

    def test_integer_dtype(self, small_walk):
        # Steps are ±1 integers, so the cumulative sum must be integer-typed.
        assert small_walk.dtype.kind == 'i'


# ── Mathematical correctness ──────────────────────────────────────────────────

class TestMathematicalCorrectness:
    def test_steps_are_plus_or_minus_one(self, small_walk):
        diffs = np.diff(small_walk)
        assert set(np.unique(diffs)) == {-1, 1}

    def test_first_value_is_plus_or_minus_one(self):
        outcomes = {generate_walk(1)[0] for _ in range(200)}
        assert outcomes <= {-1, 1}

    def test_bounded_by_n(self, small_walk):
        # |profit_n| ≤ n: worst case is all heads or all tails.
        n = np.arange(1, 101)
        assert np.all(np.abs(small_walk) <= n)

    def test_parity_invariant(self, small_walk):
        # profit_n = 2*H_n - n  ⟹  profit_n ≡ n (mod 2).
        # After an odd number of flips the profit must be odd; after even, even.
        n = np.arange(1, 101)
        assert np.all(small_walk % 2 == n % 2)

    def test_parity_invariant_large(self):
        np.random.seed(5)
        w = generate_walk(500)
        n = np.arange(1, 501)
        assert np.all(w % 2 == n % 2)

    def test_each_step_changes_by_exactly_one(self, small_walk):
        assert np.all(np.diff(small_walk) ** 2 == 1)

    def test_values_are_integer_valued(self, small_walk):
        assert np.all(small_walk == np.round(small_walk))


# ── Statistical properties ────────────────────────────────────────────────────

class TestStatisticalProperties:
    def test_mean_near_zero(self, large_ensemble):
        # E[profit_n] = 0 for all n.
        # SE ≈ sqrt(500) / sqrt(10_000) ≈ 0.22; allow 3× margin.
        col_means = large_ensemble.mean(axis=0)
        assert np.all(np.abs(col_means) < 0.7)

    def test_std_near_sqrt_n(self, large_ensemble):
        # SD(profit_n) = sqrt(n)  (steps are ±1, variance per step = 1).
        n = np.arange(1, 501)
        expected = np.sqrt(n)
        observed = large_ensemble.std(axis=0)
        # Skip first 9 steps where the sample estimate is noisiest.
        assert np.allclose(observed[9:], expected[9:], rtol=0.05)

    def test_variance_grows_with_n(self, large_ensemble):
        # Var(profit_n) = n should be strictly increasing.
        variances = large_ensemble.var(axis=0)
        sampled   = variances[::50]   # every 50th step to reduce noise
        assert np.all(np.diff(sampled) > 0)

    def test_profit_over_n_converges_to_zero(self):
        # Law of Large Numbers: profit_n / n → 0.
        np.random.seed(42)
        w = generate_walk(100_000)
        assert abs(w[-1] / 100_000) < 0.01

    def test_std_is_double_sim3_std(self):
        # profit_n (sim1) = 2 * W_n (sim3), so std(sim1) = 2 * std(sim3).
        from src.simulations.simulation_3 import generate_walk as gw3
        np.random.seed(1)
        sim1 = np.array([generate_walk(200) for _ in range(5_000)])
        np.random.seed(2)
        sim3 = np.array([gw3(200, 1)['W'] for _ in range(5_000)])
        ratio = sim1.std(axis=0) / sim3.std(axis=0)
        assert np.allclose(ratio[9:], 2.0, rtol=0.05)


# ── Determinism ───────────────────────────────────────────────────────────────

class TestDeterminism:
    def test_same_seed_same_result(self):
        np.random.seed(99)
        w1 = generate_walk(100)
        np.random.seed(99)
        w2 = generate_walk(100)
        assert np.array_equal(w1, w2)

    def test_different_calls_differ(self):
        w1 = generate_walk(100)
        w2 = generate_walk(100)
        assert not np.array_equal(w1, w2)
