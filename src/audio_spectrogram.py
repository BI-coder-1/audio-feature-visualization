import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import stft
from pathlib import Path


def compute_stft_db(audio, nperseg=512, noverlap=384, floor_db=-80.0):
    """计算STFT并转换为相对dB"""
    if nperseg <= 0:
        raise ValueError("nperseg 必须大于 0")
    if not (0 <= noverlap < nperseg):
        raise ValueError("noverlap 必须大于等于 0 且小于 nperseg")
    if audio.num_samples < nperseg:
        raise ValueError("音频长度小于窗口长度")
    if floor_db >= 0:
        raise ValueError("floor_db 必须小于 0")

    data = audio.data.astype(np.float64)
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    data = data - np.mean(data)

    f, t, Zxx = stft(data, fs=audio.sample_rate, window="hann", nperseg=nperseg,
                     noverlap=noverlap, nfft=nperseg, boundary=None, padded=False)

    magnitude = np.abs(Zxx)
    max_mag = np.max(magnitude)

    if max_mag == 0:
        magnitude_db = np.full_like(magnitude, floor_db)
    else:
        # 修复除零漏洞：先计算最小比例，截断后再取 log10
        minimum_ratio = 10 ** (floor_db / 20.0)
        relative_magnitude = magnitude / max_mag
        safe_ratio = np.maximum(relative_magnitude, minimum_ratio)
        magnitude_db = 20 * np.log10(safe_ratio)

    return f, t, magnitude_db


def plot_stft_overview(audio, output_path):
    """绘制上下子图（时域波形 + STFT声谱图）"""
    f, t, magnitude_db = compute_stft_db(audio)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='white')

    time_axis = np.arange(audio.num_samples) / audio.sample_rate
    data = audio.data.astype(np.float64)
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    ax1.plot(time_axis, data, color='#1f77b4', linewidth=0.5)
    ax1.set_title(f"Time Domain Waveform — {Path(audio.filepath).name}")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Normalized amplitude")
    ax1.set_xlim(0, time_axis[-1])
    ax1.grid(True, color='lightgray', linestyle='--')

    c = ax2.pcolormesh(t, f, magnitude_db, shading="auto", cmap="magma")
    ax2.set_title("STFT Spectrogram (Relative dB)")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Frequency (Hz)")
    ax2.set_xlim(0, time_axis[-1])
    ax2.set_ylim(0, audio.sample_rate / 2)

    cbar = fig.colorbar(c, ax=ax2)
    cbar.set_label("Relative magnitude (dB)")

    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)