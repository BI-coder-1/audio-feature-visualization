"""语音信号分析系统的 Flask 网页入口。

这个模块只负责网页交互。实际的音频读取、特征计算和绘图仍然复用
``src`` 目录中已经通过课程测试的函数，避免重复实现同一套算法。
"""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from src.audio_features import extract_basic_features
from src.audio_loader import load_wav
from src.audio_spectrogram import plot_stft_overview
from src.audio_visualizer import plot_audio_overview


MAX_UPLOAD_BYTES = 12 * 1024 * 1024
ALLOWED_SUFFIXES = {".wav"}

FEATURE_LABELS = {
    "min_amplitude": ("最小幅值", ""),
    "max_amplitude": ("最大幅值", ""),
    "peak_amplitude": ("峰值幅度", ""),
    "mean": ("平均值", ""),
    "mean_absolute_amplitude": ("平均绝对幅度", ""),
    "total_energy": ("总能量", ""),
    "average_energy": ("平均能量", ""),
    "rms": ("均方根 RMS", ""),
}


def _file_to_data_url(path: Path, mime_type: str) -> str:
    """把临时文件编码成浏览器可以直接显示的 data URL。"""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _format_features(feature_values: dict[str, float]) -> list[dict[str, str]]:
    """把算法结果转换成适合模板循环展示的行。"""

    rows = []
    for key, value in feature_values.items():
        label, unit = FEATURE_LABELS[key]
        rows.append({"label": label, "value": f"{value:.8f}", "unit": unit})
    return rows


def create_app(test_config: dict | None = None) -> Flask:
    """创建并配置 Flask 应用，测试时可传入临时配置。"""

    app = Flask(__name__)
    app.config.from_mapping(MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return render_template("index.html", result=None, error=None)

    @app.post("/analyze")
    def analyze():
        uploaded_file = request.files.get("audio_file")
        if uploaded_file is None or not uploaded_file.filename:
            return render_template(
                "index.html", result=None, error="请先选择一个 WAV 音频文件。"
            ), 400

        original_name = uploaded_file.filename
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            return render_template(
                "index.html", result=None, error="文件格式不支持，目前只接受 .wav 文件。"
            ), 400

        safe_name = secure_filename(original_name) or "uploaded_audio.wav"

        # TemporaryDirectory 退出 with 代码块时会自动删除，上传文件不会写入 data。
        with tempfile.TemporaryDirectory(prefix="audio_analysis_") as temp_dir:
            temp_path = Path(temp_dir)
            wav_path = temp_path / safe_name
            overview_path = temp_path / "overview.png"
            stft_path = temp_path / "stft.png"
            uploaded_file.save(wav_path)

            try:
                audio = load_wav(str(wav_path))
                feature_values = extract_basic_features(audio)
                plot_audio_overview(audio, overview_path)
                plot_stft_overview(audio, stft_path)
            except (ValueError, OSError) as error:
                return render_template(
                    "index.html",
                    result=None,
                    error=f"音频分析失败：{error}",
                ), 400

            result = {
                "filename": original_name,
                "sample_rate": f"{audio.sample_rate:,} Hz",
                "channels": str(audio.channels),
                "num_samples": f"{audio.num_samples:,}",
                "duration": f"{audio.duration:.3f} 秒",
                "original_dtype": str(audio.original_dtype),
                "features": _format_features(feature_values),
                "audio_url": _file_to_data_url(wav_path, "audio/wav"),
                "overview_url": _file_to_data_url(overview_path, "image/png"),
                "stft_url": _file_to_data_url(stft_path, "image/png"),
            }

        return render_template("index.html", result=result, error=None)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_error):
        size_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        return render_template(
            "index.html",
            result=None,
            error=f"文件过大，请选择不超过 {size_mb} MB 的 WAV 文件。",
        ), 413

    return app
