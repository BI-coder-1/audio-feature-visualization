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
# 修改点 1：最大值必须约等于 0
assert np.isclose(np.max(mag_db), 0.0, atol=1e-10)
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

# 修改点 2：新增交替信号测试，并让除零警告直接报错
class AlternatingAudio:
    sample_rate = 16000
    num_samples = 16000
    data = np.tile(np.array([1.0, -1.0]), num_samples // 2)

with np.errstate(divide="raise", invalid="raise"):
    f_alt, t_alt, db_alt = compute_stft_db(AlternatingAudio())

assert np.all(np.isfinite(db_alt))
assert np.isclose(np.max(db_alt), 0.0, atol=1e-10)
assert np.min(db_alt) >= -80.0

# 画图
png_path = out_dir / "test_stft.png"
plot_stft_overview(audio, png_path)
assert png_path.exists() and png_path.stat().st_size > 0

print("所有 STFT 测试通过！")