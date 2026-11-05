"""Streamlit 公网入口的处理层与页面启动回归测试。"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from web_app.streamlit_support import (
    FEATURE_LABELS,
    MAX_UPLOAD_BYTES,
    analyze_wav_bytes,
    compare_wav_bytes,
    validate_wav_upload,
)


PROJECT_ROOT = Path(__file__).parent
SAMPLE_A = PROJECT_ROOT / "samples" / "0_0_1.wav"
SAMPLE_B = PROJECT_ROOT / "samples" / "4_0_1.wav"

print("=== 测试 Streamlit 公网页面 ===")

sample_a_bytes = SAMPLE_A.read_bytes()
sample_b_bytes = SAMPLE_B.read_bytes()

try:
    validate_wav_upload("notes.txt", b"not audio")
except ValueError as error:
    assert ".wav" in str(error)
else:
    raise AssertionError("非 WAV 扩展名必须被拒绝")

try:
    validate_wav_upload("empty.wav", b"")
except ValueError as error:
    assert "为空" in str(error)
else:
    raise AssertionError("空文件必须被拒绝")

try:
    validate_wav_upload("large.wav", b"0" * (MAX_UPLOAD_BYTES + 1))
except ValueError as error:
    assert "12 MB" in str(error)
else:
    raise AssertionError("超过 12 MB 的文件必须被拒绝")

single_result = analyze_wav_bytes(SAMPLE_A.name, sample_a_bytes)
assert single_result["sample_rate"] == 16_000
assert single_result["channels"] == 1
assert len(single_result["feature_rows"]) == len(FEATURE_LABELS) == 17
assert single_result["overview_png"].startswith(b"\x89PNG")
assert single_result["stft_png"].startswith(b"\x89PNG")
assert single_result["advanced_png"].startswith(b"\x89PNG")
assert single_result["csv_bytes"].startswith(b"\xef\xbb\xbf")

comparison_result = compare_wav_bytes(
    SAMPLE_A.name,
    sample_a_bytes,
    SAMPLE_B.name,
    sample_b_bytes,
)
assert len(comparison_result["table_rows"]) == 2
assert comparison_result["table_rows"][0]["文件"] == SAMPLE_A.name
assert comparison_result["table_rows"][1]["文件"] == SAMPLE_B.name
assert comparison_result["chart_png"].startswith(b"\x89PNG")
assert b"file_name" in comparison_result["csv_bytes"]

app_test = AppTest.from_file(PROJECT_ROOT / "app.py")
app_test.run(timeout=30)
assert not app_test.exception
assert app_test.header[0].value == "选择分析模式"
assert any("山西大学人工智能学院" in element.value for element in app_test.markdown)

print("魔搭 Streamlit 入口与页面测试全部通过！")
