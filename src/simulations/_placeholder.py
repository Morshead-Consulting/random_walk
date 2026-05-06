import matplotlib.pyplot as plt
from matplotlib.widgets import Button

_C = dict(
    bg='#0d1117', panel='#161b22',
    text='#e6edf3', subtext='#8b949e',
    btn='#30363d', btn_hover='#444c56',
)


def show_placeholder(title: str) -> None:
    fig = plt.figure(figsize=(8, 5), facecolor=_C['bg'])
    try:
        fig.canvas.manager.set_window_title(title)
    except Exception:
        pass

    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor(_C['panel'])
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    fig.text(0.5, 0.58, title,
             ha='center', va='center', color=_C['text'], fontsize=22, fontweight='bold')
    fig.text(0.5, 0.44, 'Coming soon…',
             ha='center', va='center', color=_C['subtext'], fontsize=13)

    ax_btn = fig.add_axes([0.38, 0.18, 0.24, 0.10])
    btn = Button(ax_btn, 'Return to Menu', color=_C['btn'], hovercolor=_C['btn_hover'])
    btn.label.set_color('white')
    btn.label.set_fontweight('bold')
    btn.on_clicked(lambda _: plt.close(fig))

    plt.show()
    plt.close('all')
