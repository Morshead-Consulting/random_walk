# Coin Toss Random Walk — Teaching Simulation

An interactive visualisation of fluctuations in a random walk, built with Python and Matplotlib.

## What it shows

When a fair coin is tossed repeatedly, three quantities evolve in distinctly different ways:

| Panel | Quantity | Standard deviation | Behaviour |
|-------|----------|--------------------|-----------|
| Left | Heads minus expected &nbsp; W_n = H_n − n/2 | ½√n | Wanders, grows in magnitude |
| Centre | Distribution of W_n across 500 independent walks | ½√n | Histogram spreads and converges to Normal(0, ½√n) |
| Right | Proportion of heads &nbsp; H_n / n | ½ / √n | Converges to 0.5 |

The centre panel makes the Central Limit Theorem visible: at small n the histogram is lumpy and discrete; at large n it converges to the overlaid Normal(0, ½√n) curve. The ±1σ and ±2σ dashed lines track the growing spread, mirroring the shaded bands on the left panel.

## The mathematics

Each toss is a Bernoulli trial with p = ½. After n tosses:

- **E[H_n] = n/2**, so W_n = H_n − n/2 has mean zero.
- **Var(W_n) = n · p(1−p) = n/4**, giving **SD(W_n) = ½√n**.
- H_n/n = W_n/n + ½, so **SD(H_n/n) = ½/√n → 0** (Law of Large Numbers).
- By the Central Limit Theorem, W_n is approximately Normal(0, ½√n) for large n.

The centre panel runs 500 independent walks in parallel and displays their histogram of W_n at each step n. At small n, the histogram is visibly discrete (W_n can only take half-integer values); as n grows the bins fill in and the histogram converges to the overlaid theoretical Normal curve.

The shaded bands on each panel show the 1σ (brighter blue) and 2σ (darker blue) regions. A normally distributed walk stays within 2σ about 95% of the time.

## Running the simulation

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync          # install dependencies (first run only)
uv run python main.py
```

Dependencies (`numpy`, `matplotlib`) are declared in `pyproject.toml` and installed automatically by `uv sync`.

## Controls

| Control | Action |
|---------|--------|
| **Start / Stop** | Begin or pause the animation |
| **Reset** | Generate a new random walk |
| **Speed slider** | Set how many tosses are revealed per frame (1–200) |

The n counter in the title updates as the walk progresses. At the default speed of 20 tosses per frame (~30 fps) the full 5,000-toss walk completes in roughly 8 seconds.
