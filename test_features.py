import numpy as np
from pathlib import Path
from src.audio_loader import load_wav
from src.audio_features import extract_basic_features

current_dir = Path(__file__).parent
sample1 = current_dir / "samples" / "0_0_1.wav"
sample2 = current_dir / "samples" / "4_0_1.wav"

print("=== 测试 1：人工构造数组验证 ===")
class DummyAudio:
    data = np.array([0.0, -1.0, 1.0, 0.5])

manual_feat = extract_basic_features(DummyAudio())
assert np.isclose(manual_feat['peak_amplitude'], 1.0)
assert np.isclose(manual_feat['mean'], 0.125)
assert np.isclose(manual_feat['mean_absolute_amplitude'], 0.625)
assert np.isclose(manual_feat['total_energy'], 2.25)
assert np.isclose(manual_feat['average_energy'], 0.5625)
assert np.isclose(manual_feat['rms'], 0.75)

is_close = np.isclose(manual_feat['rms']**2, manual_feat['average_energy'])
print(f"  验证 RMS^2 ≈ 平均能量: {is_close}")
assert is_close

print("\n=== 测试 2：真实样本 0_0_1.wav ===")
audio1 = load_wav(str(sample1))
feat1 = extract_basic_features(audio1)
for k, v in feat1.items():
    print(f"  {k}: {v:.6f}")

print("\n=== 测试 3：真实样本 4_0_1.wav ===")

audio2 = load_wav(str(sample2))
feat2 = extract_basic_features(audio2)
for k, v in feat2.items():
    print(f"  {k}: {v:.6f}")


print("\n=== 测试 4：空数组异常捕获 ===")
class EmptyAudio:
    data = np.array([])
try:
    extract_basic_features(EmptyAudio())
except ValueError as e:
    print(f"  成功捕获异常: {e}")