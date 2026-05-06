import numpy as np
import pytest
from src.simulations.simulation_2 import generate_walk, pct_time_positive, arcsine_pdf


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def small_walk():
    np.random.seed(42)
    return generate_walk(100)


@pytest.fixture
def large_ensemble():
    """10,000 walks of length 500 — enough for tight statistical assertions."""
    np.random.seed(0)
    steps = np.where(np.random.randint(0, 2, (10_000, 500)), 1, -1)
    return steps.cumsum(axis=1)


# ── generate_walk ─────────────────────────────────────────────────────────────

class TestGenerateWalk:
    def test_returns_ndarray(self, small_walk):
        assert isinstance(small_walk, np.ndarray)

    @pytest.mark.parametrize("n", [1, 20, 100, 500])
    def test_length(self, n):
        assert len(generate_walk(n)) == n

    def test_integer_dtype(self, small_walk):
        assert small_walk.dtype.kind == 'i'

    def test_steps_are_plus_or_minus_one(self, small_walk):
        diffs = np.diff(small_walk)
        assert set(np.unique(diffs)) == {-1, 1}

    def test_first_value_is_plus_or_minus_one(self):
        outcomes = {generate_walk(1)[0] for _ in range(200)}
        assert outcomes <= {-1, 1}

    def test_parity_invariant(self, small_walk):
        n = np.arange(1, 101)
        assert np.all(small_walk % 2 == n % 2)

    def test_same_seed_same_result(self):
        np.random.seed(7)
        w1 = generate_walk(100)
        np.random.seed(7)
        w2 = generate_walk(100)
        assert np.array_equal(w1, w2)


# ── pct_time_positive ─────────────────────────────────────────────────────────

class TestPctTimePositive:
    def test_all_positive(self):
        profit = np.array([1, 2, 3, 4, 5])
        assert pct_time_positive(profit) == pytest.approx(100.0)

    def test_all_negative(self):
        profit = np.array([-1, -2, -3])
        assert pct_time_positive(profit) == pytest.approx(0.0)

    def test_all_zero(self):
        # zero is not positive
        profit = np.array([0, 0, 0])
        assert pct_time_positive(profit) == pytest.approx(0.0)

    def test_half_positive(self):
        profit = np.array([1, -1, 1, -1])
        assert pct_time_positive(profit) == pytest.approx(50.0)

    def test_range_is_zero_to_100(self, large_ensemble):
        pcts = np.array([pct_time_positive(row) for row in large_ensemble[:100]])
        assert pcts.min() >= 0.0
        assert pcts.max() <= 100.0

    def test_output_is_float(self, small_walk):
        result = pct_time_positive(small_walk)
        assert isinstance(result, float)


# ── arcsine_pdf ───────────────────────────────────────────────────────────────

class TestArcsinePdf:
    def test_symmetric(self):
        p = np.array([0.1, 0.3, 0.5])
        assert np.allclose(arcsine_pdf(p), arcsine_pdf(1 - p))

    def test_minimum_at_half(self):
        p = np.linspace(0.01, 0.99, 200)
        pdf = arcsine_pdf(p)
        assert pdf.argmin() == pytest.approx(len(p) // 2, abs=5)

    def test_increases_toward_extremes(self):
        p = np.linspace(0.01, 0.49, 100)
        pdf = arcsine_pdf(p)
        # PDF should be strictly decreasing from 0 toward 0.5
        assert np.all(np.diff(pdf) < 0)

    def test_integrates_to_one(self):
        p = np.linspace(0, 1, 100_000)
        # Trapezoid rule — exclude exact endpoints (singularities)
        p_inner = p[1:-1]
        integral = np.trapezoid(arcsine_pdf(p_inner), p_inner)
        assert integral == pytest.approx(1.0, abs=0.01)

    def test_value_at_half(self):
        # f(0.5) = 1 / (π * √(0.5 * 0.5)) = 1/(π * 0.5) = 2/π ≈ 0.6366
        assert arcsine_pdf(np.array([0.5]))[0] == pytest.approx(2 / np.pi, rel=1e-6)

    def test_clips_boundary_inputs(self):
        # Should not raise for p=0 or p=1 (clips internally)
        result = arcsine_pdf(np.array([0.0, 1.0]))
        assert np.all(np.isfinite(result))


# ── Arc-sine law: statistical convergence ────────────────────────────────────

class TestArcsineLaw:
    """Verify that the distribution of pct_time_positive converges to the
    arc-sine distribution as the number of runs grows."""

    def test_mean_near_50_pct(self, large_ensemble):
        # The arc-sine law has mean 0.5, but for finite N with strictly-positive
        # counting (~3–4% of steps sit exactly at zero), the sample mean sits
        # slightly below 50%.  Allow ±3 percentage points.
        pcts = np.array([pct_time_positive(row) for row in large_ensemble])
        assert pcts.mean() == pytest.approx(50.0, abs=3.0)

    def test_variance_near_arcsine_variance(self, large_ensemble):
        # Var[arc-sine] = 1/8, so Var[% positive] = 10000/8 = 1250 (in % units).
        # SE of sample variance ≈ 2 * 1250 / sqrt(10000) ≈ 25; allow 3× margin.
        pcts = np.array([pct_time_positive(row) for row in large_ensemble])
        assert pcts.var() == pytest.approx(1250.0, abs=75.0)

    def test_u_shaped_distribution(self, large_ensemble):
        # The arc-sine law is U-shaped: extreme bins must contain more mass than
        # the central bin.  With 20 bins, compare bins 0-1 (near 0%) and 9-10
        # (near 50%) using a sample.
        pcts = np.array([pct_time_positive(row) for row in large_ensemble])
        extreme_freq = np.mean((pcts < 10) | (pcts > 90))
        central_freq = np.mean((pcts > 40) & (pcts < 60))
        assert extreme_freq > central_freq

    def test_50pct_is_rare(self, large_ensemble):
        # Only ~6% of runs should end up in the 40–60% window.
        pcts = np.array([pct_time_positive(row) for row in large_ensemble])
        near_half = np.mean((pcts >= 40) & (pcts <= 60))
        assert near_half < 0.15
