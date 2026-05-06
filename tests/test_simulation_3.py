import numpy as np
import pytest
from src.simulations.simulation_3 import generate_walk


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def small_walk():
    np.random.seed(42)
    return generate_walk(n_max=100, m=20)


@pytest.fixture
def large_ensemble():
    """Large m so statistical assertions are reliable."""
    np.random.seed(0)
    return generate_walk(n_max=500, m=10_000)


# ── Output structure ──────────────────────────────────────────────────────────

class TestOutputStructure:
    def test_returns_all_keys(self, small_walk):
        assert set(small_walk.keys()) == {'W', 'P', 'W_all'}

    def test_w_length(self, small_walk):
        assert len(small_walk['W']) == 100

    def test_p_length(self, small_walk):
        assert len(small_walk['P']) == 100

    def test_w_all_shape(self, small_walk):
        assert small_walk['W_all'].shape == (20, 100)

    def test_w_is_float_array(self, small_walk):
        assert small_walk['W'].dtype.kind == 'f'

    def test_w_all_is_float_array(self, small_walk):
        assert small_walk['W_all'].dtype.kind == 'f'


# ── Mathematical correctness ──────────────────────────────────────────────────

class TestMathematicalCorrectness:
    def test_w_increments_are_half_integers(self, small_walk):
        # W_n = H_n - n/2 where H_n ∈ ℤ, so W_n is a multiple of 0.5.
        # Equivalently 2*W must be integer-valued.
        doubled = small_walk['W'] * 2
        assert np.allclose(doubled, np.round(doubled))

    def test_w_all_increments_are_half_integers(self, small_walk):
        doubled = small_walk['W_all'] * 2
        assert np.allclose(doubled, np.round(doubled))

    def test_p_bounded_between_zero_and_one(self, small_walk):
        assert np.all(small_walk['P'] >= 0.0)
        assert np.all(small_walk['P'] <= 1.0)

    def test_p_first_step_is_zero_or_one(self):
        # After a single toss the proportion must be exactly 0 or 1.
        outcomes = {generate_walk(1, 1)['P'][0] for _ in range(200)}
        assert outcomes <= {0.0, 1.0}

    def test_w_first_step_is_minus_half_or_plus_half(self):
        # After one toss W_1 = H_1 - 0.5 ∈ {-0.5, +0.5}.
        outcomes = {generate_walk(1, 1)['W'][0] for _ in range(200)}
        assert outcomes <= {-0.5, 0.5}

    def test_w_within_absolute_maximum(self, small_walk):
        # W_n is bounded: |W_n| ≤ n/2 (all heads or all tails).
        n = np.arange(1, 101)
        assert np.all(np.abs(small_walk['W']) <= n / 2)

    def test_w_all_within_absolute_maximum(self, small_walk):
        n = np.arange(1, 101)
        assert np.all(np.abs(small_walk['W_all']) <= n[np.newaxis, :] / 2)

    def test_p_and_w_are_consistent(self):
        # W_n = P_n * n - n/2.  Check with a fixed seed.
        np.random.seed(7)
        d = generate_walk(200, 1)
        n = np.arange(1, 201)
        reconstructed_w = d['P'] * n - n / 2
        assert np.allclose(d['W'], reconstructed_w)

    def test_w_differences_are_plus_or_minus_half(self):
        # Each step changes W by exactly +0.5 (heads) or -0.5 (tails).
        np.random.seed(3)
        d = generate_walk(500, 1)
        diffs = np.diff(d['W'])
        assert set(np.unique(np.round(diffs * 2).astype(int))) == {-1, 1}


# ── Statistical properties (CLT) ─────────────────────────────────────────────

class TestStatisticalProperties:
    def test_mean_of_w_all_near_zero(self, large_ensemble):
        # E[W_n] = 0 for all n; with m=10_000 the standard error is tiny.
        column_means = np.mean(large_ensemble['W_all'], axis=0)
        # Worst-case σ of sample mean is 0.5*sqrt(500)/sqrt(10000) ≈ 0.035.
        assert np.all(np.abs(column_means) < 0.2)

    def test_std_of_w_all_near_half_sqrt_n(self, large_ensemble):
        # Var[W_n] = n/4, so std = sqrt(n)/2.
        n_max = 500
        n = np.arange(1, n_max + 1)
        expected_std = 0.5 * np.sqrt(n)
        observed_std = np.std(large_ensemble['W_all'], axis=0)
        # Allow 5 % relative tolerance, loosened further for small n.
        assert np.allclose(observed_std[9:], expected_std[9:], rtol=0.05)

    def test_mean_of_p_near_half(self):
        # P_n → 0.5 as n → ∞ (law of large numbers).
        np.random.seed(99)
        d = generate_walk(100_000, 1)
        assert abs(d['P'][-1] - 0.5) < 0.01

    def test_w_variance_grows_with_n(self, large_ensemble):
        # Var[W_n] should be strictly increasing on average.
        variances = np.var(large_ensemble['W_all'], axis=0)
        # Sample every 50th step to reduce noise.
        sampled = variances[::50]
        assert np.all(np.diff(sampled) > 0)


# ── Determinism and independence ──────────────────────────────────────────────

class TestDeterminism:
    def test_same_seed_same_result(self):
        np.random.seed(123)
        d1 = generate_walk(100, 10)
        np.random.seed(123)
        d2 = generate_walk(100, 10)
        assert np.array_equal(d1['W'],     d2['W'])
        assert np.array_equal(d1['P'],     d2['P'])
        assert np.array_equal(d1['W_all'], d2['W_all'])

    def test_different_calls_differ(self):
        # Without seeding, two calls should almost certainly differ.
        d1 = generate_walk(100, 10)
        d2 = generate_walk(100, 10)
        assert not np.array_equal(d1['W'], d2['W'])


# ── Sigma and PDF formulas used in the animation ──────────────────────────────

class TestAnimationMath:
    @pytest.mark.parametrize("n", [1, 10, 100, 1000, 5000])
    def test_sigma_formula(self, n):
        sigma = 0.5 * np.sqrt(n)
        assert sigma == pytest.approx(np.sqrt(n) / 2)

    def test_normal_pdf_peak_at_zero(self):
        sigma = 0.5 * np.sqrt(1000)
        x = np.array([0.0])
        pdf = np.exp(-0.5 * (x / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        assert pdf[0] == pytest.approx(1 / (sigma * np.sqrt(2 * np.pi)))

    def test_normal_pdf_integrates_to_one(self):
        sigma = 0.5 * np.sqrt(500)
        x = np.linspace(-6 * sigma, 6 * sigma, 50_000)
        pdf = np.exp(-0.5 * (x / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        assert np.trapezoid(pdf, x) == pytest.approx(1.0, abs=1e-5)

    def test_normal_pdf_symmetric(self):
        sigma = 0.5 * np.sqrt(200)
        xs = np.array([1.0, 5.0, 10.0, 20.0])
        pdf_pos = np.exp(-0.5 * (xs / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        pdf_neg = np.exp(-0.5 * ((-xs) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        assert np.allclose(pdf_pos, pdf_neg)

    def test_histogram_density_sums_to_one(self):
        # The density histogram used in the animation should integrate to ~1.
        np.random.seed(5)
        d = generate_walk(n_max=500, m=5000)
        w_vals = d['W_all'][:, -1]
        hist_lim = 1.5 * np.sqrt(500)
        bins = np.linspace(-hist_lim, hist_lim, 51)
        counts, _ = np.histogram(w_vals, bins=bins, density=True)
        bin_w = bins[1] - bins[0]
        assert np.sum(counts) * bin_w == pytest.approx(1.0, abs=0.02)
