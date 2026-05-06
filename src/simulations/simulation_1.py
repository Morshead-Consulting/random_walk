import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
from itertools import cycle


_PALETTE = [
    '#ff7b7b', '#7bc8ff', '#7bffaa', '#ffb07b', '#c87bff',
    '#ffff7b', '#7bffff', '#ff7bc8', '#b0ff7b', '#9090ff',
]


def generate_walk(n_max: int) -> np.ndarray:
    """Simulate one Peter-Paul game of n_max coin flips.

    Returns Peter's cumulative profit in pennies: +1 per head, -1 per tail.
    Shape: (n_max,).
    """
    steps = np.where(np.random.randint(0, 2, n_max), 1, -1)
    return np.cumsum(steps)


def run():
    N_MAX = 500

    C = dict(
        bg='#0d1117', panel='#161b22',
        b2='#1f6feb', b1='#58a6ff',
        walk='#ffa657', zero='#8b949e',
        text='#e6edf3', grid='#21262d',
        pos='#3fb950', neg='#f85149',
    )

    n_all = np.arange(1, N_MAX + 1)
    sq    = np.sqrt(n_all)
    YMAX  = 3.0 * np.sqrt(N_MAX)   # ±3σ headroom ≈ ±67

    state = {
        'k':        0,
        'go':       False,
        'profit':   generate_walk(N_MAX),
        'archived': False,
    }
    history   = []   # list of (x_arr, profit_arr) for completed / saved runs
    hcolours  = []
    colour_it = cycle(_PALETTE)
    fills     = {}   # mutable holders for the dynamic Panel 1 fill patches

    # ── Figure ────────────────────────────────────────────────────────────────

    fig = plt.figure(figsize=(14, 6), facecolor=C['bg'])
    try:
        fig.canvas.manager.set_window_title('Peter and Paul — Coin Flip Game')
    except Exception:
        pass
    plt.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.22, wspace=0.33)

    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    for ax in (ax1, ax2):
        ax.set_facecolor(C['panel'])
        ax.tick_params(colors=C['text'], labelsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor(C['grid'])
        ax.grid(color=C['grid'], lw=0.5, alpha=0.8)
        ax.set_xlabel('Coin flips  n', color=C['text'], fontsize=9)
        ax.set_xlim(0, N_MAX)
        ax.set_ylim(-YMAX, YMAX)
        ax.axhline(0, color=C['zero'], lw=0.9, ls='--', alpha=0.7)

    # ── Panel 1: current run ──────────────────────────────────────────────────

    ax1.set_title("Peter's Profit", color=C['text'], fontsize=11, pad=8, fontweight='bold')
    ax1.set_ylabel('Profit (pennies)', color=C['text'], fontsize=9)

    # ±1σ and ±2σ bands — for a ±1 random walk, SD(n) = √n
    ax1.fill_between(n_all,   -sq,  sq,  alpha=0.15, color=C['b1'], zorder=1)
    ax1.fill_between(n_all, -2*sq, 2*sq, alpha=0.08, color=C['b2'], zorder=1)
    xL = int(N_MAX * 0.62)
    ax1.text(xL,   sq[xL] * 1.08, r'$\pm\sqrt{n}$',   color=C['b1'], fontsize=8, va='bottom')
    ax1.text(xL, 2*sq[xL] * 1.08, r'$\pm 2\sqrt{n}$', color=C['b2'], fontsize=8, va='bottom')

    # Dynamic fills: green when Peter leads, red when he trails
    fills['pos'] = ax1.fill_between([0], [0], 0, color=C['pos'], alpha=0.30, zorder=2)
    fills['neg'] = ax1.fill_between([0], [0], 0, color=C['neg'], alpha=0.30, zorder=2)
    line1, = ax1.plot([], [], color=C['walk'], lw=1.5, zorder=5)

    profit_ann = ax1.text(
        0.97, 0.97, '', transform=ax1.transAxes,
        ha='right', va='top', color=C['text'], fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=C['panel'], alpha=0.8),
    )

    # ── Panel 2: run gallery ──────────────────────────────────────────────────

    ax2.set_title('Previous Runs', color=C['text'], fontsize=11, pad=8, fontweight='bold')
    ax2.set_ylabel('Profit (pennies)', color=C['text'], fontsize=9)

    # Same σ bands, slightly fainter, so the gallery lines read clearly
    ax2.fill_between(n_all,   -sq,  sq,  alpha=0.10, color=C['b1'], zorder=1)
    ax2.fill_between(n_all, -2*sq, 2*sq, alpha=0.05, color=C['b2'], zorder=1)

    no_runs_msg = ax2.text(
        0.5, 0.5,
        'No previous runs yet.\n\nComplete a run or click\n"New Run" to archive it here.',
        transform=ax2.transAxes, ha='center', va='center',
        color=C['zero'], fontsize=10, linespacing=1.8,
    )
    run_count_ann = ax2.text(
        0.02, 0.97, '', transform=ax2.transAxes,
        ha='left', va='top', color=C['text'], fontsize=8,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=C['panel'], alpha=0.8),
    )

    # ── Title bar ─────────────────────────────────────────────────────────────

    caption = fig.text(
        0.5, 0.95, 'Peter and Paul  —  n = 0',
        ha='center', color=C['text'], fontsize=14, fontweight='bold',
    )

    # ── Controls ──────────────────────────────────────────────────────────────

    ax_spd = fig.add_axes([0.20, 0.09, 0.40, 0.035], facecolor=C['panel'])
    slider = Slider(ax_spd, 'Speed (flips / frame)', 1, 50, valinit=5, valstep=1)
    slider.label.set_color(C['text'])
    slider.valtext.set_color(C['text'])
    slider.poly.set_facecolor(C['b1'])

    ax_go   = fig.add_axes([0.05, 0.03, 0.10, 0.055])
    ax_new  = fig.add_axes([0.17, 0.03, 0.12, 0.055])
    ax_menu = fig.add_axes([0.82, 0.03, 0.15, 0.055])

    btn_go   = Button(ax_go,   'Start',          color='#238636', hovercolor='#2ea043')
    btn_new  = Button(ax_new,  'New Run',        color='#6e4040', hovercolor='#8b5050')
    btn_menu = Button(ax_menu, 'Return to Menu', color='#30363d', hovercolor='#444c56')
    for btn in (btn_go, btn_new, btn_menu):
        btn.label.set_color('white')
        btn.label.set_fontweight('bold')

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_panel1(end):
        x = n_all[:end]
        y = state['profit'][:end]
        line1.set_data(x, y)

        # Recreate the fills so the green/red regions track the profit line.
        fills['pos'].remove()
        fills['neg'].remove()
        fills['pos'] = ax1.fill_between(x, np.maximum(y, 0), 0,
                                         color=C['pos'], alpha=0.30, zorder=2)
        fills['neg'] = ax1.fill_between(x, np.minimum(y, 0), 0,
                                         color=C['neg'], alpha=0.30, zorder=2)

        current = int(y[-1])
        sign    = '+' if current >= 0 else ''
        profit_ann.set_text(f'profit = {sign}{current}p')
        profit_ann.set_color(C['pos'] if current >= 0 else C['neg'])

    def _archive_current():
        """Copy the current run into the Panel 2 gallery (once only)."""
        if state['k'] == 0 or state['archived']:
            return
        x   = n_all[:state['k']].copy()
        y   = state['profit'][:state['k']].copy()
        col = next(colour_it)
        history.append((x, y))
        hcolours.append(col)
        state['archived'] = True

        ax2.plot(x, y, color=col, lw=0.9, alpha=0.75, zorder=3)
        no_runs_msg.set_visible(False)
        n = len(history)
        run_count_ann.set_text(f'{n} run{"s" if n != 1 else ""}')

    # ── Animation callbacks ───────────────────────────────────────────────────

    def step(_frame):
        if not state['go'] or state['k'] >= N_MAX:
            return
        end        = min(state['k'] + max(1, int(slider.val)), N_MAX)
        state['k'] = end
        _update_panel1(end)
        caption.set_text(f'Peter and Paul  —  n = {end}')
        if end >= N_MAX:
            state['go'] = False
            btn_go.label.set_text('Start')
            btn_go.ax.set_facecolor('#238636')
            _archive_current()

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

    def new_run(_event):
        _archive_current()

        state['go']       = False
        state['k']        = 0
        state['profit']   = generate_walk(N_MAX)
        state['archived'] = False

        btn_go.label.set_text('Start')
        btn_go.ax.set_facecolor('#238636')

        line1.set_data([], [])
        fills['pos'].remove()
        fills['neg'].remove()
        fills['pos'] = ax1.fill_between([0], [0], 0, color=C['pos'], alpha=0.30, zorder=2)
        fills['neg'] = ax1.fill_between([0], [0], 0, color=C['neg'], alpha=0.30, zorder=2)
        profit_ann.set_text('')

        caption.set_text('Peter and Paul  —  n = 0')
        fig.canvas.draw_idle()

    btn_go.on_clicked(toggle)
    btn_new.on_clicked(new_run)
    btn_menu.on_clicked(lambda _: plt.close(fig))

    ani = animation.FuncAnimation(fig, step, interval=33, cache_frame_data=False)
    plt.show()
    plt.close('all')
