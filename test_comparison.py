import csv
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

expected_fields = [
    'file_name', 'sample_rate_hz', 'channels', 'num_samples', 'duration_s',
    'min_amplitude', 'max_amplitude', 'peak_amplitude', 'mean',
    'mean_absolute_amplitude', 'total_energy', 'average_energy', 'rms'
]

for r in rows:
    for key in expected_fields:
        assert key in r, f"{r['file_name']} 缺少字段: {key}"
    assert r['sample_rate_hz'] == 16000, "采样率不是16000"
    assert r['channels'] == 1, "声道数不是1"
    assert r['num_samples'] == 80000, "采样点数不是80000"
    assert np.isclose(r['duration_s'], 5.0), "时长不是5秒"

    for key in expected_fields:
        if key != 'file_name':
            assert np.isfinite(r[key]), f"{key} 存在无效值"


    assert np.isclose(r['rms'] ** 2, r['average_energy']), "RMS与能量的关系不成立"

csv_path = out_dir / "test_comparison.csv"
save_comparison_csv(rows, csv_path)
assert csv_path.exists() and csv_path.stat().st_size > 0

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = list(csv.DictReader(f))
    assert len(reader) == 2, "CSV行数不对"

    assert list(reader[0].keys()) == expected_fields, "CSV表头字段不一致"

    for csv_row, expected_row in zip(reader, rows):
        assert csv_row["file_name"] == expected_row["file_name"], "文件名不匹配"

        for key in expected_fields[1:]:
            assert np.isclose(
                float(csv_row[key]),
                expected_row[key]
            ), f"CSV字段 {key} 数值不一致"

png_path = out_dir / "test_comparison.png"
plot_feature_comparison(rows, png_path)
assert png_path.exists() and png_path.stat().st_size > 0

try:
    build_comparison_rows([s1])
    assert False, "应该抛出异常"
except ValueError:
    pass

print("所有比较测试通过！")