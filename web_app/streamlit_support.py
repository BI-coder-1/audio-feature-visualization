"""Streamlit 公网页面的文件处理服务。

这个模块不绘制网页控件，只接收文件名和二进制数据，再调用 ``src`` 中的
课程算法。把界面和处理逻辑分开后，既方便测试，也方便本科生逐层理解。
"""

from __future__ import annotations

import csv
import io
import tempfile
from pathlib import Path

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


def validate_wav_upload(file_name: str, file_bytes: bytes) -> None:
    """在进入信号算法前检查文件名、大小和基础格式。"""

    if not file_name:
        raise ValueError("文件名不能为空。")
    if Path(file_name).suffix.lower() != ".wav":
        raise ValueError("文件格式不支持，目前只接受 .wav 文件。")
    if not file_bytes:
        raise ValueError("上传文件为空。")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("文件超过 12 MB，请选择更小的 WAV 音频。")


def _safe_upload_path(directory: Path, prefix: str, file_name: str) -> Path:
    """清理用户文件名，防止文件名被解释为目录路径。"""

    safe_name = secure_filename(file_name) or "uploaded_audio.wav"
    return directory / f"{prefix}_{safe_name}"


def _feature_rows(values: dict[str, float]) -> list[dict[str, str]]:
    """把算法字典转换成网页表格所需的中文行。"""

    rows = []
    for key, value in values.items():
        label, unit = FEATURE_LABELS[key]
        rows.append({"特征": label, "数值": f"{value:.8f}", "单位": unit or "—"})
    return rows


def _rows_to_csv_bytes(rows: list[dict]) -> bytes:
    """生成带 UTF-8 BOM 的 CSV，使 Excel 能正确显示中文。"""

    text_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(text_buffer, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + text_buffer.getvalue().encode("utf-8")


def analyze_wav_bytes(file_name: str, file_bytes: bytes) -> dict:
    """分析单个 WAV，返回元数据、特征、图片、音频和 CSV 字节。"""

    validate_wav_upload(file_name, file_bytes)

    # 临时目录只服务于这次函数调用；离开 with 后会由 Python 自动删除。
    with tempfile.TemporaryDirectory(prefix="streamlit_audio_analysis_") as temp_dir:
        temp_path = Path(temp_dir)
        wav_path = _safe_upload_path(temp_path, "single", file_name)
        overview_path = temp_path / "overview.png"
        stft_path = temp_path / "stft.png"
        advanced_path = temp_path / "advanced.png"
        wav_path.write_bytes(file_bytes)

        audio = load_wav(str(wav_path))
        basic_features = extract_basic_features(audio)
        advanced_features = extract_advanced_summary(audio)
        feature_values = {**basic_features, **advanced_features}

        plot_audio_overview(audio, overview_path)
        plot_stft_overview(audio, stft_path)
        plot_advanced_overview(audio, advanced_path)

        csv_row = {
            "file_name": file_name,
            "sample_rate_hz": audio.sample_rate,
            "channels": audio.channels,
            "num_samples": audio.num_samples,
            "duration_s": audio.duration,
            **feature_values,
        }

        # 图片必须在临时目录删除前读回内存，之后页面只持有 bytes。
        result = {
            "file_name": file_name,
            "sample_rate": audio.sample_rate,
            "channels": audio.channels,
            "num_samples": audio.num_samples,
            "duration": audio.duration,
            "original_dtype": str(audio.original_dtype),
            "feature_rows": _feature_rows(feature_values),
            "audio_bytes": file_bytes,
            "overview_png": overview_path.read_bytes(),
            "stft_png": stft_path.read_bytes(),
            "advanced_png": advanced_path.read_bytes(),
            "csv_bytes": _rows_to_csv_bytes([csv_row]),
            "csv_name": f"{Path(file_name).stem}_analysis.csv",
        }

    return result


def compare_wav_bytes(
    file_name_a: str,
    file_bytes_a: bytes,
    file_name_b: str,
    file_bytes_b: bytes,
) -> dict:
    """使用同一套算法比较两个 WAV，并返回表格、图像和 CSV。"""

    validate_wav_upload(file_name_a, file_bytes_a)
    validate_wav_upload(file_name_b, file_bytes_b)

    with tempfile.TemporaryDirectory(prefix="streamlit_audio_comparison_") as temp_dir:
        temp_path = Path(temp_dir)
        names = [file_name_a, file_name_b]
        payloads = [file_bytes_a, file_bytes_b]
        wav_paths = []

        for index, (name, payload) in enumerate(zip(names, payloads), start=1):
            wav_path = _safe_upload_path(temp_path, str(index), name)
            wav_path.write_bytes(payload)
            wav_paths.append(wav_path)

        chart_path = temp_path / "comparison.png"
        csv_path = temp_path / "comparison.csv"
        rows = build_comparison_rows(wav_paths)

        for row, wav_path, original_name in zip(rows, wav_paths, names):
            row["file_name"] = original_name
            row.update(extract_advanced_summary(load_wav(str(wav_path))))

        plot_feature_comparison(rows, chart_path)
        save_comparison_csv(rows, csv_path)

        table_rows = []
        for row in rows:
            table_rows.append({
                "文件": row["file_name"],
                "采样率": f"{row['sample_rate_hz']:,} Hz",
                "声道": row["channels"],
                "时长": f"{row['duration_s']:.3f} s",
                "峰值幅度": f"{row['peak_amplitude']:.6f}",
                "RMS": f"{row['rms']:.6f}",
                "平均能量": f"{row['average_energy']:.8f}",
                "平均过零率": f"{row['mean_zero_crossing_rate']:.6f}",
                "频谱质心": f"{row['spectral_centroid_hz']:.2f} Hz",
            })

        result = {
            "table_rows": table_rows,
            "chart_png": chart_path.read_bytes(),
            "csv_bytes": csv_path.read_bytes(),
            "csv_name": "audio_feature_comparison.csv",
        }

    return result
