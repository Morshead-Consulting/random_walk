import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider

N_MAX  = 5000
M      = 500   # parallel walks for the distribution panel
N_BINS = 50

C = dict(
    bg='#0d1117', panel='#161b22',
    b2='#1f6feb', b1='#58a6ff',
    walk='#ffa657', zero='#8b949e',
    text='#e6edf3', grid='#21262d',
)

walk = {}


def generate():
    tosses    = np.random.randint(0, 2, N_MAX)
    heads     = np.cumsum(tosses)
    n         = np.arange(1, N_MAX + 1)
    walk['W'] = heads - n / 2
    walk['P'] = heads / n

    all_tosses   = np.random.randint(0, 2, (M, N_MAX))
    all_heads    = np.cumsum(all_tosses, axis=1)
    walk['W_all'] = all_heads - n[np.newaxis, :] / 2   # shape (M, N_MAX)


generate()

n_all = np.arange(1, N_MAX + 1)
sq    = np.sqrt(n_all)
WMAX  = sq[-1]   # sqrt(5000) ~= 70.71

HIST_LIM = 1.5 * WMAX
bins     = np.linspace(-HIST_LIM, HIST_LIM, N_BINS + 1)
bin_ctrs = (bins[:-1] + bins[1:]) / 2
bin_w    = bins[1] - bins[0]
pdf_x    = np.linspace(-HIST_LIM, HIST_LIM, 400)

# Fix the centre-panel y-axis at 1.75× the PDF peak reached at n = N_MAX.
# At that point σ = ½√N_MAX, so peak height = 1 / (σ √(2π)).  This gives
# enough headroom at large n without the axis jumping around at small n.
_sigma_final = 0.5 * np.sqrt(N_MAX)
Y2_MAX = 1.75 / (_sigma_final * np.sqrt(2 * np.pi))

# ── Figure ────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(17, 7), facecolor=C['bg'])
try:
    fig.canvas.manager.set_window_title('Coin Toss Random Walk')
except Exception:
    pass
plt.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.22, wspace=0.33)

ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2)
ax3 = fig.add_subplot(1, 3, 3)

for ax in (ax1, ax2, ax3):
    ax.set_facecolor(C['panel'])
    ax.tick_params(colors=C['text'], labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor(C['grid'])
    ax.grid(color=C['grid'], lw=0.5, alpha=0.8)
    ax.set_xlabel('Tosses  n', color=C['text'], fontsize=8)

ax1.set_title(r'Heads $-$ Expected   $W_n = H_n - n/2$',
              color=C['text'], fontsize=10, pad=8, fontweight='bold')
ax2.set_title(fr'Distribution of $W_n$  across {M} simulations',
              color=C['text'], fontsize=10, pad=8, fontweight='bold')
ax3.set_title(r'Proportion of Heads   $H_n / n$',
              color=C['text'], fontsize=10, pad=8, fontweight='bold')

ax1.set_ylabel(r'$W_n$', color=C['text'], fontsize=10)
ax2.set_ylabel('Probability density', color=C['text'], fontsize=9)
ax3.set_ylabel(r'$H_n / n$', color=C['text'], fontsize=10)

# Panel 2 x-axis is W_n values, not tosses
ax2.set_xlabel(r'$W_n$', color=C['text'], fontsize=10)

# ── Panel 1 static elements ────────────────────────────────────────────────────

ax1.fill_between(n_all, -sq,     sq,     alpha=0.18, color=C['b2'])
ax1.fill_between(n_all, -0.5*sq, 0.5*sq, alpha=0.38, color=C['b1'])
ax1.axhline(0, color=C['zero'], lw=0.9, ls='--', alpha=0.7)
ax1.set_xlim(0, N_MAX)
ax1.set_ylim(-1.5 * WMAX, 1.5 * WMAX)

xL = int(N_MAX * 0.60)
kw = dict(fontsize=7.5, va='bottom')
ax1.text(xL, 0.5*sq[xL]*1.05, r'$1\sigma = \pm\frac{1}{2}\sqrt{n}$', color=C['b1'], **kw)
ax1.text(xL,     sq[xL]*1.05, r'$2\sigma = \pm\sqrt{n}$',            color=C['b2'], **kw)

# ── Panel 2: evolving histogram + normal PDF ───────────────────────────────────

ax2.set_xlim(-HIST_LIM, HIST_LIM)
ax2.set_ylim(0, Y2_MAX)
ax2.axvline(0, color=C['zero'], lw=0.9, ls='--', alpha=0.7)

bar2     = ax2.bar(bin_ctrs, np.zeros(N_BINS), width=bin_w * 0.92,
                   color=C['walk'], alpha=0.75, zorder=3)
pdf_line, = ax2.plot(pdf_x, np.zeros(len(pdf_x)), color=C['b1'], lw=2.0, zorder=5,
                     label=r'$\mathcal{N}(0,\,\tfrac{1}{2}\sqrt{n})$')

# Sigma indicator lines (invisible until animation starts)
vl_1p = ax2.axvline(x=0, color=C['b1'], lw=1.0, ls='--', alpha=0.0)
vl_1m = ax2.axvline(x=0, color=C['b1'], lw=1.0, ls='--', alpha=0.0)
vl_2p = ax2.axvline(x=0, color=C['b2'], lw=1.0, ls='--', alpha=0.0)
vl_2m = ax2.axvline(x=0, color=C['b2'], lw=1.0, ls='--', alpha=0.0)

sigma_ann = ax2.text(0.97, 0.97, '', transform=ax2.transAxes,
                     ha='right', va='top', color=C['text'], fontsize=8,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor=C['panel'], alpha=0.8))

# ── Panel 3 static elements ────────────────────────────────────────────────────

ax3.fill_between(n_all, 0.5 - 1/sq,    0.5 + 1/sq,    alpha=0.18, color=C['b2'])
ax3.fill_between(n_all, 0.5 - 0.5/sq,  0.5 + 0.5/sq,  alpha=0.38, color=C['b1'])
ax3.axhline(0.5, color=C['zero'], lw=0.9, ls='--', alpha=0.7)
ax3.set_xlim(0, N_MAX)
ax3.set_ylim(0, 1)

x3 = 60
ax3.text(x3, 0.5 + 0.5/np.sqrt(x3) + 0.03, r'$1\sigma$', color=C['b1'], fontsize=7.5)
ax3.text(x3, 0.5 + 1/np.sqrt(x3)   + 0.03, r'$2\sigma$', color=C['b2'], fontsize=7.5)

# ── Walk lines (start empty) ──────────────────────────────────────────────────

line1, = ax1.plot([], [], color=C['walk'], lw=0.9)
line3, = ax3.plot([], [], color=C['walk'], lw=0.9)

# ── Title counter ─────────────────────────────────────────────────────────────

caption = fig.text(0.5, 0.95, 'Coin Toss Random Walk  —  n = 0',
                   ha='center', color=C['text'], fontsize=14, fontweight='bold')

# ── Controls ──────────────────────────────────────────────────────────────────

ax_spd = fig.add_axes([0.25, 0.09, 0.40, 0.035], facecolor=C['panel'])
slider = Slider(ax_spd, 'Speed (tosses / frame)', 1, 200, valinit=20, valstep=1)
slider.label.set_color(C['text'])
slider.valtext.set_color(C['text'])
slider.poly.set_facecolor(C['b1'])

ax_go  = fig.add_axes([0.08, 0.03, 0.10, 0.055])
ax_rst = fig.add_axes([0.20, 0.03, 0.10, 0.055])
btn_go  = Button(ax_go,  'Start', color='#238636', hovercolor='#2ea043')
btn_rst = Button(ax_rst, 'Reset', color='#6e4040', hovercolor='#8b5050')
for btn in (btn_go, btn_rst):
    btn.label.set_color('white')
    btn.label.set_fontweight('bold')

state = {'k': 0, 'go': False}

# ── Animation callback ────────────────────────────────────────────────────────

def step(_frame):
    if not state['go'] or state['k'] >= N_MAX:
        return
    end        = min(state['k'] + max(1, int(slider.val)), N_MAX)
    state['k'] = end
    x          = n_all[:end]

    # Panel 1: single walk trajectory
    line1.set_data(x, walk['W'][:end])

    # Panel 2: distribution of W_n across M walks at step n = end
    w_vals         = walk['W_all'][:, end - 1]
    counts, _      = np.histogram(w_vals, bins=bins, density=True)
    for rect, h in zip(bar2.patches, counts):
        rect.set_height(h)

    sigma    = 0.5 * np.sqrt(end)
    pdf_vals = np.exp(-0.5 * (pdf_x / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    pdf_line.set_ydata(pdf_vals)

    vl_1p.set_xdata([ sigma,  sigma])
    vl_1m.set_xdata([-sigma, -sigma])
    vl_2p.set_xdata([ 2*sigma,  2*sigma])
    vl_2m.set_xdata([-2*sigma, -2*sigma])
    for vl in (vl_1p, vl_1m, vl_2p, vl_2m):
        vl.set_alpha(0.75)

    sigma_ann.set_text(f'σ = {sigma:.1f}')

    # Panel 3: proportion of heads
    line3.set_data(x, walk['P'][:end])

    caption.set_text(f'Coin Toss Random Walk  —  n = {end:,}')
    if end >= N_MAX:
        state['go'] = False
        btn_go.label.set_text('Start')
        btn_go.ax.set_facecolor('#238636')


def toggle(_event):
    if state['k'] >= N_MAX:
        return
    state['go'] = not state['go']
    if state['go']:
        btn_go.label.set_text('Stop')
        btn_go.ax.set_facecolor('#b62324')
    else:
        btn_go.label.set_text('Start')
        btn_go.ax.set_facecolor('#238636')
    fig.canvas.draw_idle()


def reset(_event):
    state['go'] = False
    state['k']  = 0
    btn_go.label.set_text('Start')
    btn_go.ax.set_facecolor('#238636')
    generate()

    line1.set_data([], [])
    line3.set_data([], [])

    for rect in bar2.patches:
        rect.set_height(0)
    pdf_line.set_ydata(np.zeros(len(pdf_x)))
    for vl in (vl_1p, vl_1m, vl_2p, vl_2m):
        vl.set_alpha(0.0)
    sigma_ann.set_text('')
    ax2.set_ylim(0, Y2_MAX)

    caption.set_text('Coin Toss Random Walk  —  n = 0')
    fig.canvas.draw_idle()


btn_go.on_clicked(toggle)
btn_rst.on_clicked(reset)

ani = animation.FuncAnimation(fig, step, interval=33, cache_frame_data=False)
plt.show()
