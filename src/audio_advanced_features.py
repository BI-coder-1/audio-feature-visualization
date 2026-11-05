"""进阶音频特征：短时特征、频谱统计和 MFCC。

这些函数只使用 NumPy、SciPy 和 Matplotlib，保留每一步中间含义，适合
本科课程设计中逐行讲解。它们不包含语音识别模型，也不会预测说话内容。
"""

from pathlib import Path

import matplotlib
import numpy as np
from scipy.fft import dct

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def to_mono(audio):
    """把音频转换成 float64 单声道数组，多声道时取通道平均。"""

    data = audio.data.astype(np.float64)
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if data.size == 0:
        raise ValueError("音频没有可分析的采样点")
    return data


def frame_audio(audio, frame_duration_ms=25.0, hop_duration_ms=10.0):
    """把连续波形切成重叠短帧，并返回每帧中心时刻。

    25 ms 帧长和 10 ms 帧移是常见的语音短时分析参数。这里保留完整帧，
    末尾不足一帧的少量采样点不补零，避免人为引入静音。
    """

    if frame_duration_ms <= 0 or hop_duration_ms <= 0:
        raise ValueError("帧长和帧移必须大于 0")

    data = to_mono(audio)
    frame_length = int(round(audio.sample_rate * frame_duration_ms / 1000.0))
    hop_length = int(round(audio.sample_rate * hop_duration_ms / 1000.0))
    frame_length = max(frame_length, 1)
    hop_length = max(hop_length, 1)

    if data.size < frame_length:
        raise ValueError("音频长度小于一个分析帧")

    starts = np.arange(0, data.size - frame_length + 1, hop_length)
    frames = np.empty((starts.size, frame_length), dtype=np.float64)
    for index, start in enumerate(starts):
        frames[index] = data[start:start + frame_length]

    frame_times = (starts + frame_length / 2.0) / audio.sample_rate
    return frame_times, frames


def compute_short_time_features(audio, frame_duration_ms=25.0, hop_duration_ms=10.0):
    """计算每帧短时能量和过零率。"""

    frame_times, frames = frame_audio(audio, frame_duration_ms, hop_duration_ms)
    short_time_energy = np.mean(np.square(frames), axis=1)

    # 相邻采样点符号不同就记作一次过零，再除以可比较的相邻点数量。
    signs = frames >= 0
    crossings = signs[:, 1:] != signs[:, :-1]
    zero_crossing_rate = np.mean(crossings, axis=1)
    return frame_times, short_time_energy, zero_crossing_rate


def compute_spectral_statistics(audio, rolloff_ratio=0.85):
    """计算整段音频的五项频谱统计量。"""

    if not 0 < rolloff_ratio < 1:
        raise ValueError("rolloff_ratio 必须在 0 和 1 之间")

    data = to_mono(audio)
    centered_data = data - np.mean(data)
    frequencies = np.fft.rfftfreq(centered_data.size, d=1.0 / audio.sample_rate)
    power = np.square(np.abs(np.fft.rfft(centered_data)))
    total_power = np.sum(power)

    if total_power <= np.finfo(np.float64).eps:
        return {
            "dominant_frequency_hz": 0.0,
            "spectral_centroid_hz": 0.0,
            "spectral_bandwidth_hz": 0.0,
            "spectral_rolloff_85_hz": 0.0,
            "spectral_flatness": 0.0,
        }

    dominant_index = int(np.argmax(power[1:]) + 1) if power.size > 1 else 0
    centroid = np.sum(frequencies * power) / total_power
    bandwidth = np.sqrt(np.sum(np.square(frequencies - centroid) * power) / total_power)

    cumulative_power = np.cumsum(power)
    rolloff_index = int(np.searchsorted(cumulative_power, rolloff_ratio * total_power))
    rolloff_index = min(rolloff_index, frequencies.size - 1)

    positive_power = np.maximum(power, np.finfo(np.float64).tiny)
    geometric_mean = np.exp(np.mean(np.log(positive_power)))
    arithmetic_mean = np.mean(power)
    flatness = geometric_mean / arithmetic_mean

    return {
        "dominant_frequency_hz": float(frequencies[dominant_index]),
        "spectral_centroid_hz": float(centroid),
        "spectral_bandwidth_hz": float(bandwidth),
        "spectral_rolloff_85_hz": float(frequencies[rolloff_index]),
        "spectral_flatness": float(flatness),
    }


def _hz_to_mel(frequency_hz):
    return 2595.0 * np.log10(1.0 + frequency_hz / 700.0)


def _mel_to_hz(frequency_mel):
    return 700.0 * (10.0 ** (frequency_mel / 2595.0) - 1.0)


def _create_mel_filterbank(sample_rate, n_fft, n_mels):
    """创建 n_mels 个三角形 Mel 滤波器。"""

    lowest_mel = _hz_to_mel(0.0)
    highest_mel = _hz_to_mel(sample_rate / 2.0)
    mel_points = np.linspace(lowest_mel, highest_mel, n_mels + 2)
    hz_points = _mel_to_hz(mel_points)
    fft_bins = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)
    fft_bins = np.clip(fft_bins, 0, n_fft // 2)

    filterbank = np.zeros((n_mels, n_fft // 2 + 1), dtype=np.float64)
    for mel_index in range(n_mels):
        left = fft_bins[mel_index]
        center = fft_bins[mel_index + 1]
        right = fft_bins[mel_index + 2]

        if center > left:
            filterbank[mel_index, left:center] = (
                np.arange(left, center) - left
            ) / (center - left)
        if right > center:
            filterbank[mel_index, center:right] = (
                right - np.arange(center, right)
            ) / (right - center)
    return filterbank


def compute_mfcc(
    audio,
    n_mfcc=13,
    n_mels=26,
    frame_duration_ms=25.0,
    hop_duration_ms=10.0,
):
    """计算 MFCC，返回帧中心时刻和形状为 (系数数, 帧数) 的矩阵。"""

    if n_mfcc <= 0 or n_mels <= 0 or n_mfcc > n_mels:
        raise ValueError("需满足 0 < n_mfcc <= n_mels")

    frame_times, frames = frame_audio(audio, frame_duration_ms, hop_duration_ms)
    emphasized_frames = frames.copy()
    emphasized_frames[:, 1:] = frames[:, 1:] - 0.97 * frames[:, :-1]

    frame_length = emphasized_frames.shape[1]
    n_fft = 1 << int(np.ceil(np.log2(frame_length)))
    windowed_frames = emphasized_frames * np.hamming(frame_length)
    power_spectrum = np.square(np.abs(np.fft.rfft(windowed_frames, n=n_fft))) / n_fft

    filterbank = _create_mel_filterbank(audio.sample_rate, n_fft, n_mels)
    mel_energy = power_spectrum @ filterbank.T
    log_mel_energy = np.log(np.maximum(mel_energy, 1e-12))
    mfcc = dct(log_mel_energy, type=2, axis=1, norm="ortho")[:, :n_mfcc]
    return frame_times, mfcc.T


def extract_advanced_summary(audio):
    """汇总适合表格展示和音频比较的进阶特征。"""

    _, energy, zero_crossing_rate = compute_short_time_features(audio)
    spectral_statistics = compute_spectral_statistics(audio)

    maximum_energy = np.max(energy)
    if maximum_energy == 0:
        high_energy_ratio = 0.0
    else:
        high_energy_ratio = np.mean(energy >= 0.1 * maximum_energy)

    return {
        "mean_short_time_energy": float(np.mean(energy)),
        "max_short_time_energy": float(maximum_energy),
        "mean_zero_crossing_rate": float(np.mean(zero_crossing_rate)),
        "high_energy_frame_ratio": float(high_energy_ratio),
        **spectral_statistics,
    }


def plot_advanced_overview(audio, output_path):
    """绘制波形、短时能量、过零率和 MFCC 四联图。"""

    data = to_mono(audio)
    waveform_times = np.arange(data.size) / audio.sample_rate
    frame_times, energy, zero_crossing_rate = compute_short_time_features(audio)
    mfcc_times, mfcc = compute_mfcc(audio)

    fig, axes = plt.subplots(4, 1, figsize=(11, 12), facecolor="white")
    fig.suptitle(f"Advanced Audio Features — {Path(audio.filepath).name}", fontsize=14)

    axes[0].plot(waveform_times, data, color="#1769aa", linewidth=0.5)
    axes[0].set_title("Time Domain Waveform")
    axes[0].set_ylabel("Amplitude")
    axes[0].set_xlim(0, waveform_times[-1])

    axes[1].plot(frame_times, energy, color="#d88418", linewidth=1.0)
    axes[1].set_title("Short-Time Energy (25 ms frame, 10 ms hop)")
    axes[1].set_ylabel("Mean square")
    axes[1].set_xlim(0, waveform_times[-1])
    energy_top = np.max(energy) * 1.1 if np.max(energy) > 0 else 1.0
    axes[1].set_ylim(0, energy_top)

    axes[2].plot(frame_times, zero_crossing_rate, color="#26815e", linewidth=1.0)
    axes[2].set_title("Zero-Crossing Rate")
    axes[2].set_ylabel("Rate")
    axes[2].set_xlim(0, waveform_times[-1])
    zcr_top = np.max(zero_crossing_rate) * 1.1 if np.max(zero_crossing_rate) > 0 else 1.0
    axes[2].set_ylim(0, zcr_top)

    image = axes[3].imshow(
        mfcc,
        origin="lower",
        aspect="auto",
        extent=[mfcc_times[0], mfcc_times[-1], 1, mfcc.shape[0]],
        cmap="viridis",
    )
    axes[3].set_title("MFCC")
    axes[3].set_xlabel("Time (s)")
    axes[3].set_ylabel("Coefficient")
    fig.colorbar(image, ax=axes[3], label="Coefficient value")

    for axis in axes[:3]:
        axis.grid(True, color="lightgray", linestyle="--", alpha=0.7)
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
