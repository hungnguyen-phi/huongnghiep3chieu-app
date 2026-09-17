# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

FONT_DIR = os.environ.get('FONT_DIR', '/usr/share/fonts/truetype/dejavu')
LINE_COL = '#0F5C4D'
FILL_COL = '#E8B96B'


def generate_radar(scores: dict, out_path: str):
    """scores: {'R':..,'I':..,'A':..,'S':..,'E':..,'C':..} moi nhom 0-24."""
    fp = fm.FontProperties(fname=FONT_DIR + '/DejaVuSans.ttf')
    fpb = fm.FontProperties(fname=FONT_DIR + '/DejaVuSans-Bold.ttf')

    labels = ['I\nNghiên cứu', 'A\nSáng tạo', 'S\nXã hội', 'E\nQuản lý', 'C\nQuy củ', 'R\nKỹ thuật']
    values = [scores['I'], scores['A'], scores['S'], scores['E'], scores['C'], scores['R']]

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_c = values + values[:1]
    angles_c = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(5.2, 5.2), subplot_kw=dict(polar=True), dpi=150)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles_c, values_c, color=LINE_COL, linewidth=2.2, zorder=3)
    ax.fill(angles_c, values_c, color=FILL_COL, alpha=0.55, zorder=2)

    for ang, val in zip(angles, values):
        ax.text(ang, val + 1.6, str(val), ha='center', va='center',
                fontproperties=fpb, fontsize=11, color=LINE_COL, zorder=4)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontproperties=fpb, fontsize=10, color='#2C2C2A')
    ax.set_ylim(0, 24)
    ax.set_yticks([6, 12, 18, 24])
    ax.set_yticklabels(['6', '12', '18', '24'], fontproperties=fp, fontsize=7.5, color='#9C9A92')
    ax.grid(color='#D3D1C7', linewidth=0.6)
    ax.spines['polar'].set_color('#D3D1C7')

    plt.tight_layout(pad=0.5)
    plt.savefig(out_path, dpi=150, bbox_inches='tight', transparent=True)
    plt.close(fig)
    return out_path
