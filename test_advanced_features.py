"""进阶音频特征的独立回归测试。"""

from pathlib import Path

import numpy as np

from src.audio_advanced_features import (
    compute_mfcc,
    compute_short_time_features,
    compute_spectral_statistics,
    extract_advanced_summary,
    plot_advanced_overview,
)


class SyntheticAudio:
    sample_rate = 16000
    duration = 1.0
    num_samples = sample_rate
    filepath = "synthetic_1000hz.wav"
    times = np.arange(num_samples) / sample_rate
    data = 0.5 * np.sin(2 * np.pi * 1000 * times)


print("=== 测试进阶音频特征 ===")
audio = SyntheticAudio()

frame_times, energy, zcr = compute_short_time_features(audio)
assert frame_times.ndim == energy.ndim == zcr.ndim == 1
assert frame_times.shape == energy.shape == zcr.shape
assert np.all(np.diff(frame_times) > 0)
assert np.all(energy > 0)
assert np.isclose(np.mean(zcr), 2 * 1000 / audio.sample_rate, atol=0.01)

spectral = compute_spectral_statistics(audio)
assert np.isclose(spectral["dominant_frequency_hz"], 1000.0, atol=1.0)
assert np.isclose(spectral["spectral_centroid_hz"], 1000.0, atol=1.0)
assert spectral["spectral_bandwidth_hz"] < 5.0
assert np.isclose(spectral["spectral_rolloff_85_hz"], 1000.0, atol=1.0)
assert 0.0 <= spectral["spectral_flatness"] <= 1.0

mfcc_times, mfcc = compute_mfcc(audio)
assert mfcc.shape == (13, len(mfcc_times))
assert np.all(np.isfinite(mfcc))

summary = extract_advanced_summary(audio)
assert len(summary) == 9
assert all(np.isfinite(value) for value in summary.values())
assert 0.0 <= summary["high_energy_frame_ratio"] <= 1.0

class SilentAudio:
    sample_rate = 16000
    duration = 1.0
    num_samples = sample_rate
    filepath = "silence.wav"
    data = np.zeros(num_samples)


silent_summary = extract_advanced_summary(SilentAudio())
assert all(value == 0.0 for value in silent_summary.values())

try:
    compute_mfcc(audio, n_mfcc=27, n_mels=26)
    assert False, "n_mfcc 大于 n_mels 时应抛出异常"
except ValueError:
    pass

output_path = Path(__file__).parent / "results" / "advanced" / "advanced_test.png"
plot_advanced_overview(audio, output_path)
assert output_path.exists() and output_path.stat().st_size > 0

print("进阶音频特征测试全部通过！")
