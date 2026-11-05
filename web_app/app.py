"""语音信号分析系统的 Flask 网页入口。

这个模块只负责网页交互。实际的音频读取、特征计算和绘图仍然复用
``src`` 目录中已经通过课程测试的函数，避免重复实现同一套算法。
"""

from __future__ import annotations

import base64
import csv
import io
import tempfile
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from src.audio_advanced_features import extract_advanced_summary, plot_advanced_overview
from src.audio_comparator import (
    build_comparison_rows,
    plot_feature_comparison,
    save_comparison_csv,
)
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
    "mean_short_time_energy": ("平均短时能量", ""),
    "max_short_time_energy": ("最大短时能量", ""),
    "mean_zero_crossing_rate": ("平均过零率", ""),
    "high_energy_frame_ratio": ("相对高能帧占比", ""),
    "dominant_frequency_hz": ("主频", "Hz"),
    "spectral_centroid_hz": ("频谱质心", "Hz"),
    "spectral_bandwidth_hz": ("频谱带宽", "Hz"),
    "spectral_rolloff_85_hz": ("85% 频谱滚降点", "Hz"),
    "spectral_flatness": ("频谱平坦度", ""),
}


def _file_to_data_url(path: Path, mime_type: str) -> str:
    """把临时文件编码成浏览器可以直接显示的 data URL。"""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _rows_to_csv_data_url(rows: list[dict]) -> str:
    """把字典行转换为带 UTF-8 BOM 的可下载 CSV data URL。"""

    text_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(text_buffer, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = b"\xef\xbb\xbf" + text_buffer.getvalue().encode("utf-8")
    encoded = base64.b64encode(csv_bytes).decode("ascii")
    return f"data:text/csv;base64,{encoded}"


def _format_features(feature_values: dict[str, float]) -> list[dict[str, str]]:
    """把算法结果转换成适合模板循环展示的行。"""

    rows = []
    for key, value in feature_values.items():
        label, unit = FEATURE_LABELS[key]
        rows.append({"label": label, "value": f"{value:.8f}", "unit": unit})
    return rows


def _validate_upload(uploaded_file: FileStorage | None, field_label: str) -> FileStorage:
    """检查网页上传字段是否存在且扩展名为 WAV。"""

    if uploaded_file is None or not uploaded_file.filename:
        raise ValueError(f"请先选择{field_label}的 WAV 音频文件。")
    if Path(uploaded_file.filename).suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"{field_label}文件格式不支持，目前只接受 .wav 文件。")
    return uploaded_file


def _format_comparison_rows(rows: list[dict]) -> list[dict[str, str]]:
    """选择最有解释力的指标，组成网页比较表。"""

    formatted_rows = []
    for row in rows:
        formatted_rows.append({
            "file_name": row["file_name"],
            "sample_rate": f"{row['sample_rate_hz']:,} Hz",
            "channels": str(row["channels"]),
            "duration": f"{row['duration_s']:.3f} s",
            "peak": f"{row['peak_amplitude']:.6f}",
            "rms": f"{row['rms']:.6f}",
            "energy": f"{row['average_energy']:.8f}",
            "zcr": f"{row['mean_zero_crossing_rate']:.6f}",
            "centroid": f"{row['spectral_centroid_hz']:.2f} Hz",
        })
    return formatted_rows


def create_app(test_config: dict | None = None) -> Flask:
    """创建并配置 Flask 应用，测试时可传入临时配置。"""

    app = Flask(__name__)
    app.config.from_mapping(MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES)
    if test_config:
        app.config.update(test_config)

    def render_home(
        *, result=None, comparison=None, error=None, active_mode="single", status=200
    ):
        return render_template(
            "index.html",
            result=result,
            comparison=comparison,
            error=error,
            active_mode=active_mode,
        ), status

    @app.get("/")
    def index():
        return render_home()

    @app.get("/health")
    def health():
        """供云平台确认进程仍能正常响应，不执行耗时音频分析。"""

        return {"status": "ok", "service": "audio-signal-analysis"}

    @app.post("/analyze")
    def analyze():
        try:
            uploaded_file = _validate_upload(request.files.get("audio_file"), "待分析")
        except ValueError as error:
            return render_home(error=str(error), status=400)

        original_name = uploaded_file.filename
        safe_name = secure_filename(original_name) or "uploaded_audio.wav"

        # TemporaryDirectory 退出 with 代码块时会自动删除，上传文件不会写入 data。
        with tempfile.TemporaryDirectory(prefix="audio_analysis_") as temp_dir:
            temp_path = Path(temp_dir)
            wav_path = temp_path / safe_name
            overview_path = temp_path / "overview.png"
            stft_path = temp_path / "stft.png"
            advanced_path = temp_path / "advanced.png"
            uploaded_file.save(wav_path)

            try:
                audio = load_wav(str(wav_path))
                basic_features = extract_basic_features(audio)
                advanced_features = extract_advanced_summary(audio)
                feature_values = {**basic_features, **advanced_features}
                plot_audio_overview(audio, overview_path)
                plot_stft_overview(audio, stft_path)
                plot_advanced_overview(audio, advanced_path)
            except (ValueError, OSError) as error:
                return render_home(error=f"音频分析失败：{error}", status=400)

            csv_row = {
                "file_name": original_name,
                "sample_rate_hz": audio.sample_rate,
                "channels": audio.channels,
                "num_samples": audio.num_samples,
                "duration_s": audio.duration,
                **feature_values,
            }

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
                "advanced_url": _file_to_data_url(advanced_path, "image/png"),
                "csv_url": _rows_to_csv_data_url([csv_row]),
                "csv_name": f"{Path(safe_name).stem}_analysis.csv",
            }

        return render_home(result=result)

    @app.post("/compare")
    def compare():
        try:
            upload_a = _validate_upload(request.files.get("audio_file_a"), "音频 A")
            upload_b = _validate_upload(request.files.get("audio_file_b"), "音频 B")
        except ValueError as error:
            return render_home(error=str(error), active_mode="compare", status=400)

        uploads = [upload_a, upload_b]
        original_names = [upload.filename for upload in uploads]

        with tempfile.TemporaryDirectory(prefix="audio_comparison_") as temp_dir:
            temp_path = Path(temp_dir)
            wav_paths = []
            for index, upload in enumerate(uploads, start=1):
                safe_name = secure_filename(upload.filename) or f"audio_{index}.wav"
                wav_path = temp_path / f"{index}_{safe_name}"
                upload.save(wav_path)
                wav_paths.append(wav_path)

            chart_path = temp_path / "comparison.png"
            csv_path = temp_path / "comparison.csv"
            try:
                rows = build_comparison_rows(wav_paths)
                for row, wav_path, original_name in zip(rows, wav_paths, original_names):
                    row["file_name"] = original_name
                    row.update(extract_advanced_summary(load_wav(str(wav_path))))
                plot_feature_comparison(rows, chart_path)
                save_comparison_csv(rows, csv_path)
            except (ValueError, OSError) as error:
                return render_home(
                    error=f"音频比较失败：{error}",
                    active_mode="compare",
                    status=400,
                )

            comparison = {
                "rows": _format_comparison_rows(rows),
                "chart_url": _file_to_data_url(chart_path, "image/png"),
                "csv_url": _file_to_data_url(csv_path, "text/csv"),
            }

        return render_home(comparison=comparison, active_mode="compare")

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_error):
        size_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        active_mode = "compare" if request.endpoint == "compare" else "single"
        return render_home(
            error=f"请求过大，请确保上传文件总量不超过 {size_mb} MB。",
            active_mode=active_mode,
            status=413,
        )

    return app
