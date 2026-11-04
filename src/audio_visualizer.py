import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
def create_time_axis(audio):
    """
    create time axis for audio file
    """
    num_samples=audio.data.shape[0]
    return np.arange(num_samples)/audio.sample_rate
def compute_single_sided_spectrum(audio):
    """
    compute single sided spectrum
    """
    data=audio.data.astype(np.float64)
    if len(data.shape)>1:
        data=np.mean(data,axis=1)
    centered_data=data-np.mean(data)
    fft_vals=np.fft.rfft(centered_data)
    amplitude=np.abs(fft_vals)/len(data)
    if len(data) % 2 == 0:
        amplitude[1:-1] *= 2
    else:
        amplitude[1:] *= 2
    freq_axis=np.fft.rfftfreq(len(data),d=1/audio.sample_rate)
    return freq_axis, amplitude
def plot_audio_overview(audio, output_path):
    """画图"""
    time_axis = create_time_axis(audio)
    data=audio.data
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    freq_axis, amplitude = compute_single_sided_spectrum(audio)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='white')
    fig.suptitle(f"Audio Overview — {Path(audio.filepath).name}", fontsize=14)
    ax1.plot(time_axis, data, color='#1f77b4', linewidth=0.5)
    ax1.set_title("Time Domain Waveform")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Normalized amplitude")
    ax1.set_xlim(0, time_axis[-1])
    ax1.grid(True, color='lightgray', linestyle='--')
    ax2.plot(freq_axis, amplitude, color='#ff7f0e', linewidth=1.0)
    ax2.set_title("Single-Sided Amplitude Spectrum")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Relative amplitude")
    ax2.set_xlim(0, audio.sample_rate / 2)
    ax2.set_ylim(bottom=0) # 纵轴从0开始
    ax2.grid(True, color='lightgray', linestyle='--')
    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)