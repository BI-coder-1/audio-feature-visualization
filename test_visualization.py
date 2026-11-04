import numpy as np
from pathlib import Path
from src.audio_loader import load_wav
from src.audio_visualizer import create_time_axis, compute_single_sided_spectrum, plot_audio_overview

current_dir = Path(__file__).parent
sample_path = current_dir / "samples" / "0_0_1.wav"
output_path = current_dir / "results" / "lesson04" / "test_overview.png"

print("=== 测试可视化 ===")
audio = load_wav(str(sample_path))

# 1. 测试时间轴
time_axis = create_time_axis(audio)
assert len(time_axis) == 80000, "时间轴长度不是80000"
assert np.isclose(time_axis[0], 0.0), "时间轴首项不是0"
assert np.isclose(time_axis[-1], 4.9999375), "时间轴末项错误"

# 2. 测试频率轴
freq_axis, amplitude = compute_single_sided_spectrum(audio)
assert len(freq_axis) == 40001, "频率轴长度不是40001"
assert np.isclose(freq_axis[0], 0.0), "频率轴首项不是0"
assert np.isclose(freq_axis[-1], 8000.0), "频率轴末项不是8000"
assert np.all(np.isfinite(amplitude)), "幅度谱包含非有限数"
assert np.all(amplitude >= 0), "幅度谱包含负数"

# 3. 测试绘图
plot_audio_overview(audio, output_path)
assert output_path.exists(), "PNG图片未生成"
assert output_path.stat().st_size > 0, "PNG图片是空的"

print("所有断言测试通过！")