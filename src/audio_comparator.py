import csv
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from src.audio_loader import load_wav
from src.audio_features import extract_basic_features


def build_comparison_rows(audio_paths):
    """读取多个音频，整合元数据和特征"""
    if len(audio_paths) < 2:
        raise ValueError("必须提供至少两个音频文件进行比较")

    rows = []
    for path in audio_paths:
        audio = load_wav(str(path))
        feats = extract_basic_features(audio)

        # 合并元数据和特征
        row = {
            "file_name": Path(path).name,
            "sample_rate_hz": audio.sample_rate,
            "channels": audio.channels,
            "num_samples": audio.num_samples,
            "duration_s": audio.duration,
            **feats  # 解包特征字典
        }
        rows.append(row)
    return rows


def save_comparison_csv(rows, output_path):
    """保存比较结果到 CSV 文件"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 使用 utf-8-sig 方便 Excel 正确显示
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def plot_feature_comparison(rows, output_path):
    """绘制分量纲对比柱状图"""
    file_names = [r['file_name'] for r in rows]

    amp_metrics = ['Peak amplitude', 'Mean absolute', 'RMS']
    energy_metric = ['average_energy']
    x = np.arange(len(amp_metrics))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='white')

    # 上图：幅度对比
    for i, r in enumerate(rows):
        vals = [r[m] for m in ['peak_amplitude', 'mean_absolute_amplitude', 'rms']]
        offset = width * i - width / 2 * (len(rows) - 1)
        ax1.bar(x + offset, vals, width, label=r['file_name'])

    ax1.set_ylabel("Normalized amplitude")
    ax1.set_title("Amplitude Comparison")
    ax1.set_xticks(x)
    ax1.set_xticklabels(amp_metrics)
    ax1.legend()
    ax1.grid(True, axis='y', color='lightgray', linestyle='--')

    # 下图：平均能量对比
    x2 = np.arange(len(energy_metric))
    for i, r in enumerate(rows):
        vals = [r[m] for m in energy_metric]
        offset = width * i - width / 2 * (len(rows) - 1)
        ax2.bar(x2 + offset, vals, width, label=r['file_name'])

    ax2.set_ylabel("Relative energy")
    ax2.set_title("Average Energy Comparison")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(energy_metric)
    ax2.legend()
    ax2.grid(True, axis='y', color='lightgray', linestyle='--')

    fig.suptitle("Audio Features Comparison", fontsize=14)
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)