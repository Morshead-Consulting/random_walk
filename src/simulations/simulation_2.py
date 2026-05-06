import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider


_N_BINS = 40


def generate_walk(n: int) -> np.ndarray:
    """Return Peter's cumulative profit for n coin flips: +1 head, -1 tail."""
    return np.where(np.random.randint(0, 2, n), 1, -1).cumsum()


def pct_time_positive(profit: np.ndarray) -> float:
    """Return the percentage of steps where profit > 0."""
    return 100.0 * np.sum(profit > 0) / len(profit)


def arcsine_pdf(p: np.ndarray) -> np.ndarray:
    """Arc-sine distribution PDF on (0, 1): 1 / (π * sqrt(p * (1-p)))."""
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return 1.0 / (np.pi * np.sqrt(p * (1 - p)))


def run():
    N_DEFAULT = 200

    C = dict(
        bg='#0d1117', panel='#161b22',
        b2='#1f6feb', b1='#58a6ff',
        walk='#ffa657', zero='#8b949e',
        text='#e6edf3', grid='#21262d',
        pos='#3fb950', neg='#f85149',
        theory='#c87bff',
        hist='#58a6ff',
    )

    BIN_EDGES = np.linspace(0, 100, _N_BINS + 1)
    BIN_CENTERS = 0.5 * (BIN_EDGES[:-1] + BIN_EDGES[1:])
    BIN_WIDTH = BIN_EDGES[1] - BIN_EDGES[0]

    state = {
        'k': 0,
        'go': False,
        'n': N_DEFAULT,
        'profit': generate_walk(N_DEFAULT),
        'pct_times': [],
        'show_theory': False,
    }

    fills = {}
    ax1_art = {}  # line, annotation — rebuilt when ax1 is cleared

    # ── Figure ────────────────────────────────────────────────────────────────

    fig = plt.figure(figsize=(14, 7), facecolor=C['bg'])
    try:
        fig.canvas.manager.set_window_title('Peter and Paul — The Arcsine Law')
    except Exception:
        pass
    plt.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.28, wspace=0.35)

    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    # ── Panel 2: histogram (built once; bar heights updated in place) ─────────

    ax2.set_facecolor(C['panel'])
    ax2.tick_params(colors=C['text'], labelsize=8)
    for sp in ax2.spines.values():
        sp.set_edgecolor(C['grid'])
    ax2.grid(color=C['grid'], lw=0.5, alpha=0.8)
    ax2.set_title('Distribution of Time in Profit', color=C['text'],
                  fontsize=11, pad=8, fontweight='bold')
    ax2.set_xlabel('% of flips Peter is in profit', color=C['text'], fontsize=9)
    ax2.set_ylabel('Relative frequency', color=C['text'], fontsize=9)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 0.15)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))

    bars = ax2.bar(
        BIN_CENTERS, np.zeros(_N_BINS), width=BIN_WIDTH * 0.6,
        color=C['hist'], alpha=0.75, zorder=3, edgecolor='#0d1117',
    )

    waiting_msg = ax2.text(
        0.5, 0.5,
        'Run simulations to build\nup the distribution here.\n\nExpect the unexpected!',
        transform=ax2.transAxes, ha='center', va='center',
        color=C['zero'], fontsize=10, linespacing=1.8,
    )

    theory_line, = ax2.plot([], [], color=C['theory'], lw=2.0, zorder=5, alpha=0.9)

    run_count_ann = ax2.text(
        0.02, 0.97, '', transform=ax2.transAxes,
        ha='left', va='top', color=C['text'], fontsize=8,
        bbox=dict(boxstyle='round,pad=0.3', facecolor=C['panel'], alpha=0.8),
    )

    # ── Panel 1: current walk (rebuilt on each new run) ───────────────────────

    def _setup_ax1():
        ax1.cla()
        n = state['n']
        n_arr = np.arange(1, n + 1)
        sq = np.sqrt(n_arr)
        ymax = 3.0 * np.sqrt(n)

        ax1.set_facecolor(C['panel'])
        ax1.tick_params(colors=C['text'], labelsize=8)
        for sp in ax1.spines.values():
            sp.set_edgecolor(C['grid'])
        ax1.grid(color=C['grid'], lw=0.5, alpha=0.8)
        ax1.set_title("Peter's Profit", color=C['text'],
                      fontsize=11, pad=8, fontweight='bold')
        ax1.set_xlabel('Coin flips  n', color=C['text'], fontsize=9)
        ax1.set_ylabel('Profit (pennies)', color=C['text'], fontsize=9)
        ax1.set_xlim(0, n)
        ax1.set_ylim(-ymax, ymax)
        ax1.axhline(0, color=C['zero'], lw=0.9, ls='--', alpha=0.7)
        ax1.fill_between(n_arr,   -sq,   sq, alpha=0.15, color=C['b1'], zorder=1)
        ax1.fill_between(n_arr, -2*sq, 2*sq, alpha=0.08, color=C['b2'], zorder=1)
        xL = int(n * 0.62)
        ax1.text(xL,   sq[xL] * 1.08, r'$\pm\sqrt{n}$',   color=C['b1'], fontsize=8, va='bottom')
        ax1.text(xL, 2*sq[xL] * 1.08, r'$\pm 2\sqrt{n}$', color=C['b2'], fontsize=8, va='bottom')

        fills['pos'] = ax1.fill_between([0], [0], 0, color=C['pos'], alpha=0.30, zorder=2)
        fills['neg'] = ax1.fill_between([0], [0], 0, color=C['neg'], alpha=0.30, zorder=2)
        ax1_art['line'], = ax1.plot([], [], color=C['walk'], lw=1.5, zorder=5)
        ax1_art['ann'] = ax1.text(
            0.97, 0.97, '', transform=ax1.transAxes,
            ha='right', va='top', color=C['text'], fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C['panel'], alpha=0.8),
        )

    _setup_ax1()

    # ── Title bar ─────────────────────────────────────────────────────────────

    caption = fig.text(
        0.5, 0.95, f'The Arcsine Law  —  N = {N_DEFAULT} flips',
        ha='center', color=C['text'], fontsize=14, fontweight='bold',
    )

    # ── Controls ──────────────────────────────────────────────────────────────

    ax_spd = fig.add_axes([0.20, 0.14, 0.40, 0.030], facecolor=C['panel'])
    ax_n   = fig.add_axes([0.20, 0.09, 0.40, 0.030], facecolor=C['panel'])
    slider_spd = Slider(ax_spd, 'Speed (flips/frame)', 1, 50, valinit=10, valstep=1)
    slider_n   = Slider(ax_n,   'Coin flips  N', 20, 1000, valinit=N_DEFAULT, valstep=10)
    for sl in (slider_spd, slider_n):
        sl.label.set_color(C['text'])
        sl.valtext.set_color(C['text'])
        sl.poly.set_facecolor(C['b1'])

    ax_go     = fig.add_axes([0.050, 0.025, 0.090, 0.055])
    ax_new    = fig.add_axes([0.150, 0.025, 0.090, 0.055])
    ax_reset  = fig.add_axes([0.250, 0.025, 0.090, 0.055])
    ax_theory = fig.add_axes([0.350, 0.025, 0.130, 0.055])
    ax_menu   = fig.add_axes([0.820, 0.025, 0.150, 0.055])

    btn_go     = Button(ax_go,     'Start',         color='#238636', hovercolor='#2ea043')
    btn_new    = Button(ax_new,    'New Run',        color='#6e4040', hovercolor='#8b5050')
    btn_reset  = Button(ax_reset,  'Reset',          color='#5a3060', hovercolor='#7a4080')
    btn_theory = Button(ax_theory, 'Show Theory',    color='#30363d', hovercolor='#444c56')
    btn_menu   = Button(ax_menu,   'Return to Menu', color='#30363d', hovercolor='#444c56')
    for btn in (btn_go, btn_new, btn_reset, btn_theory, btn_menu):
        btn.label.set_color('white')
        btn.label.set_fontweight('bold')

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_panel1(end):
        x = np.arange(1, end + 1)
        y = state['profit'][:end]
        ax1_art['line'].set_data(x, y)
        fills['pos'].remove()
        fills['neg'].remove()
        fills['pos'] = ax1.fill_between(x, np.maximum(y, 0), 0,
                                        color=C['pos'], alpha=0.30, zorder=2)
        fills['neg'] = ax1.fill_between(x, np.minimum(y, 0), 0,
                                        color=C['neg'], alpha=0.30, zorder=2)
        pct = 100.0 * np.sum(y > 0) / end
        ax1_art['ann'].set_text(f'time in profit = {pct:.1f}%')
        ax1_art['ann'].set_color(C['pos'] if pct >= 50 else C['neg'])

    def _update_histogram():
        pts = state['pct_times']
        if not pts:
            return
        waiting_msg.set_visible(False)
        counts, _ = np.histogram(pts, bins=BIN_EDGES)
        rel_freq = counts / len(pts)
        for bar, h in zip(bars, rel_freq):
            bar.set_height(h)

        if state['show_theory']:
            # Expected bar height at extreme bin centre (p ≈ 0.025)
            p_edge = BIN_CENTERS[0] / 100.0
            theory_peak = (BIN_WIDTH / 100.0) * arcsine_pdf(np.array([p_edge]))[0]
            ymax = max(rel_freq.max(), theory_peak) * 1.15
            p_pct = np.linspace(0.5, 99.5, 400)
            theory_y = (BIN_WIDTH / 100.0) * arcsine_pdf(p_pct / 100.0)
            theory_line.set_data(p_pct, theory_y)
            theory_line.set_visible(True)
        else:
            ymax = rel_freq.max() * 1.25 if rel_freq.max() > 0 else 0.15
            theory_line.set_visible(False)

        ax2.set_ylim(0, max(ymax, 0.05))
        n_runs = len(pts)
        run_count_ann.set_text(
            f'{n_runs} run{"s" if n_runs != 1 else ""}  ·  N = {state["n"]} flips each'
        )

    # ── Animation callbacks ───────────────────────────────────────────────────

    def step(_frame):
        if not state['go'] or state['k'] >= state['n']:
            return
        end = min(state['k'] + max(1, int(slider_spd.val)), state['n'])
        state['k'] = end
        _update_panel1(end)
        caption.set_text(f'The Arcsine Law  —  flip {end} / {state["n"]}')
        if end >= state['n']:
            state['go'] = False
            btn_go.label.set_text('Start')
            btn_go.ax.set_facecolor('#238636')
            state['pct_times'].append(pct_time_positive(state['profit']))
            _update_histogram()

    def toggle(_event):
        if state['k'] >= state['n']:
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
        state['go'] = False
        state['n'] = int(slider_n.val)
        state['k'] = 0
        state['profit'] = generate_walk(state['n'])
        _setup_ax1()
        btn_go.label.set_text('Start')
        btn_go.ax.set_facecolor('#238636')
        caption.set_text(f'The Arcsine Law  —  N = {state["n"]} flips')
        fig.canvas.draw_idle()

    def reset(_event):
        state['go'] = False
        state['pct_times'] = []
        state['k'] = 0
        state['n'] = int(slider_n.val)
        state['profit'] = generate_walk(state['n'])
        for bar in bars:
            bar.set_height(0)
        ax2.set_ylim(0, 0.15)
        waiting_msg.set_visible(True)
        run_count_ann.set_text('')
        theory_line.set_visible(False)
        _setup_ax1()
        btn_go.label.set_text('Start')
        btn_go.ax.set_facecolor('#238636')
        caption.set_text(f'The Arcsine Law  —  N = {state["n"]} flips')
        fig.canvas.draw_idle()

    def toggle_theory(_event):
        state['show_theory'] = not state['show_theory']
        btn_theory.label.set_text(
            'Hide Theory' if state['show_theory'] else 'Show Theory'
        )
        _update_histogram()
        fig.canvas.draw_idle()

    btn_go.on_clicked(toggle)
    btn_new.on_clicked(new_run)
    btn_reset.on_clicked(reset)
    btn_theory.on_clicked(toggle_theory)
    btn_menu.on_clicked(lambda _: plt.close(fig))

    ani = animation.FuncAnimation(fig, step, interval=33, cache_frame_data=False)
    plt.show()
    plt.close('all')
