import numpy as np
from pathlib import Path
from src.audio_comparator import build_comparison_rows, save_comparison_csv, plot_feature_comparison

current_dir = Path(__file__).parent
s1 = current_dir / "samples" / "0_0_1.wav"
s2 = current_dir / "samples" / "4_0_1.wav"
out_dir = current_dir / "results" / "lesson05"

print("=== 测试多文件比较 ===")

rows = build_comparison_rows([s1, s2])
assert len(rows) == 2, "应返回恰好两行数据"
assert rows[0]['file_name'] == '0_0_1.wav'
assert rows[1]['file_name'] == '4_0_1.wav'

for key in ['peak_amplitude', 'rms', 'average_energy', 'sample_rate_hz']:
    assert key in rows[0], f"缺少字段: {key}"

for r in rows:
    assert np.isfinite(r['rms']), "存在无效值"
    assert np.isclose(r['rms']**2, r['average_energy']), "RMS与能量的关系不成立"

csv_path = out_dir / "test_comparison.csv"
save_comparison_csv(rows, csv_path)
assert csv_path.exists() and csv_path.stat().st_size > 0

png_path = out_dir / "test_comparison.png"
plot_feature_comparison(rows, png_path)
assert png_path.exists() and png_path.stat().st_size > 0
try:
    build_comparison_rows([s1])
    assert False, "应该抛出异常"
except ValueError:
    pass
print("所有比较测试通过！")