"""网页入口的最小回归测试，不启动真实网络服务器。"""

from io import BytesIO
from pathlib import Path

from web_app import create_app


PROJECT_ROOT = Path(__file__).parent
SAMPLE_WAV = PROJECT_ROOT / "samples" / "0_0_1.wav"
SAMPLE_WAV_B = PROJECT_ROOT / "samples" / "4_0_1.wav"

app = create_app({"TESTING": True})
client = app.test_client()

print("=== 测试交互式网页 ===")

home_response = client.get("/")
assert home_response.status_code == 200
assert "语音信号分析与可视化系统" in home_response.get_data(as_text=True)

missing_response = client.post("/analyze", data={})
assert missing_response.status_code == 400
assert "请先选择待分析的 WAV" in missing_response.get_data(as_text=True)

wrong_type_response = client.post(
    "/analyze",
    data={"audio_file": (BytesIO(b"not audio"), "notes.txt")},
    content_type="multipart/form-data",
)
assert wrong_type_response.status_code == 400
assert "文件格式不支持" in wrong_type_response.get_data(as_text=True)

with SAMPLE_WAV.open("rb") as sample_file:
    analysis_response = client.post(
        "/analyze",
        data={"audio_file": (BytesIO(sample_file.read()), "0_0_1.wav")},
        content_type="multipart/form-data",
    )

analysis_html = analysis_response.get_data(as_text=True)
assert analysis_response.status_code == 200
assert "分析完成" in analysis_html
assert "16,000 Hz" in analysis_html
assert "基础时域特征" in analysis_html
assert "短时能量、过零率与 MFCC" in analysis_html
assert "主频" in analysis_html
assert "data:image/png;base64," in analysis_html
assert "data:audio/wav;base64," in analysis_html
assert "data:text/csv;base64," in analysis_html

missing_comparison = client.post("/compare", data={})
assert missing_comparison.status_code == 400
assert "音频 A" in missing_comparison.get_data(as_text=True)

with SAMPLE_WAV.open("rb") as sample_a, SAMPLE_WAV_B.open("rb") as sample_b:
    comparison_response = client.post(
        "/compare",
        data={
            "audio_file_a": (BytesIO(sample_a.read()), "0_0_1.wav"),
            "audio_file_b": (BytesIO(sample_b.read()), "4_0_1.wav"),
        },
        content_type="multipart/form-data",
    )

comparison_html = comparison_response.get_data(as_text=True)
assert comparison_response.status_code == 200
assert "双文件对比完成" in comparison_html
assert "0_0_1.wav" in comparison_html and "4_0_1.wav" in comparison_html
assert "频谱质心" in comparison_html
assert "data:image/png;base64," in comparison_html
assert "data:text/csv;base64," in comparison_html

print("网页测试全部通过！")
