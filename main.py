import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider

N_MAX = 5000

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
    walk['W'] = heads - n / 2      # heads minus expected
    walk['D'] = 2 * heads - n      # heads minus tails
    walk['P'] = heads / n          # proportion of heads


generate()

n_all = np.arange(1, N_MAX + 1)
sq    = np.sqrt(n_all)
WMAX  = sq[-1]   # sqrt(5000) ~= 70.71

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
ax2.set_title(r'Heads $-$ Tails   $D_n = H_n - T_n$',
              color=C['text'], fontsize=10, pad=8, fontweight='bold')
ax3.set_title(r'Proportion of Heads   $H_n / n$',
              color=C['text'], fontsize=10, pad=8, fontweight='bold')

ax1.set_ylabel(r'$W_n$', color=C['text'], fontsize=10)
ax2.set_ylabel(r'$D_n$', color=C['text'], fontsize=10)
ax3.set_ylabel(r'$H_n / n$', color=C['text'], fontsize=10)

# ── Static band fills ─────────────────────────────────────────────────────────

# Panel 1: sigma_W = 0.5*sqrt(n)  →  1-sigma: ±0.5*sqrt(n),  2-sigma: ±sqrt(n)
ax1.fill_between(n_all, -sq,     sq,     alpha=0.18, color=C['b2'])
ax1.fill_between(n_all, -0.5*sq, 0.5*sq, alpha=0.38, color=C['b1'])
ax1.axhline(0, color=C['zero'], lw=0.9, ls='--', alpha=0.7)
ax1.set_xlim(0, N_MAX)
ax1.set_ylim(-1.5 * WMAX, 1.5 * WMAX)   # ±3-sigma headroom

# Panel 2: sigma_D = sqrt(n)  →  1-sigma: ±sqrt(n),  2-sigma: ±2*sqrt(n)
ax2.fill_between(n_all, -2*sq, 2*sq, alpha=0.18, color=C['b2'])
ax2.fill_between(n_all, -sq,   sq,   alpha=0.38, color=C['b1'])
ax2.axhline(0, color=C['zero'], lw=0.9, ls='--', alpha=0.7)
ax2.set_xlim(0, N_MAX)
ax2.set_ylim(-3 * WMAX, 3 * WMAX)        # ±3-sigma headroom

# Panel 3: sigma_P = 0.5/sqrt(n)  →  1-sigma: ±0.5/sqrt(n),  2-sigma: ±1/sqrt(n)
ax3.fill_between(n_all, 0.5 - 1/sq,    0.5 + 1/sq,    alpha=0.18, color=C['b2'])
ax3.fill_between(n_all, 0.5 - 0.5/sq,  0.5 + 0.5/sq,  alpha=0.38, color=C['b1'])
ax3.axhline(0.5, color=C['zero'], lw=0.9, ls='--', alpha=0.7)
ax3.set_xlim(0, N_MAX)
ax3.set_ylim(0, 1)

# Band labels
xL = int(N_MAX * 0.60)
kw = dict(fontsize=7.5, va='bottom')
ax1.text(xL, 0.5*sq[xL]*1.05, r'$1\sigma = \pm\frac{1}{2}\sqrt{n}$', color=C['b1'], **kw)
ax1.text(xL,     sq[xL]*1.05, r'$2\sigma = \pm\sqrt{n}$',            color=C['b2'], **kw)
ax2.text(xL,     sq[xL]*1.05, r'$1\sigma = \pm\sqrt{n}$',            color=C['b1'], **kw)
ax2.text(xL, 2*sq[xL]*1.05,   r'$2\sigma = \pm 2\sqrt{n}$',          color=C['b2'], **kw)
x3 = 60
ax3.text(x3, 0.5 + 0.5/np.sqrt(x3) + 0.03, r'$1\sigma$', color=C['b1'], fontsize=7.5)
ax3.text(x3, 0.5 + 1/np.sqrt(x3)   + 0.03, r'$2\sigma$', color=C['b2'], fontsize=7.5)

# ── Walk lines (start empty) ──────────────────────────────────────────────────

line1, = ax1.plot([], [], color=C['walk'], lw=0.9)
line2, = ax2.plot([], [], color=C['walk'], lw=0.9)
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
    line1.set_data(x, walk['W'][:end])
    line2.set_data(x, walk['D'][:end])
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
    line2.set_data([], [])
    line3.set_data([], [])
    caption.set_text('Coin Toss Random Walk  —  n = 0')
    fig.canvas.draw_idle()


btn_go.on_clicked(toggle)
btn_rst.on_clicked(reset)

ani = animation.FuncAnimation(fig, step, interval=33, cache_frame_data=False)
plt.show()
