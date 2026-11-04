import numpy as np
from pathlib import Path
from src.audio_loader import load_wav
from src.audio_spectrogram import compute_stft_db, plot_stft_overview

current_dir = Path(__file__).parent
s1 = current_dir / "samples" / "0_0_1.wav"
out_dir = current_dir / "results" / "lesson06"

print("=== 测试 STFT 声谱图 ===")
audio = load_wav(str(s1))

f, t, mag_db = compute_stft_db(audio)
assert f.ndim == 1 and t.ndim == 1 and mag_db.ndim == 2
assert mag_db.shape == (len(f), len(t))
assert np.all(np.isfinite(mag_db))
assert np.isclose(f[0], 0)
assert np.isclose(f[-1], 8000)
assert np.all(np.diff(t) > 0)
assert t[-1] <= audio.duration
assert np.max(mag_db) <= 0.0
assert np.min(mag_db) >= -80.0

# 测试异常
try:
    compute_stft_db(audio, nperseg=100, noverlap=100)
    assert False
except ValueError:
    pass

try:
    compute_stft_db(audio, nperseg=100000)
    assert False
except ValueError:
    pass

class SilentAudio:
    data = np.zeros(16000)
    num_samples = 16000
    sample_rate = 16000

f_s, t_s, mag_s = compute_stft_db(SilentAudio())
assert np.all(mag_s == -80.0)
assert np.all(np.isfinite(mag_s))

# 画图
png_path = out_dir / "test_stft.png"
plot_stft_overview(audio, png_path)
assert png_path.exists() and png_path.stat().st_size > 0

print("所有 STFT 测试通过！")