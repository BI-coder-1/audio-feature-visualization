"""Streamlit 公网页面实现。

本地运行命令：``streamlit run app.py``
本文件只组织网页控件；所有音频计算由 ``src`` 和
``web_app.streamlit_support`` 完成。
"""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path

import streamlit as st

from web_app.streamlit_support import analyze_wav_bytes, compare_wav_bytes


ASSET_DIR = Path(__file__).parent / "web_app" / "static" / "sxu"


@st.cache_data(show_spinner=False)
def image_data_uri(file_name: str) -> str:
    """把 PPT 提取的 PNG 转成 data URI，并缓存转换结果。"""

    image_bytes = (ASSET_DIR / file_name).read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def inject_styles() -> None:
    """加入源自山西大学 PPT 模板的扁平学术视觉风格。"""

    st.markdown(
        """
        <style>
        :root {
            --sxu-teal: #1b8187;
            --sxu-cyan: #29c4cd;
            --sxu-ink: #252d30;
            --sxu-muted: #747d80;
            --sxu-line: #d7dcdd;
            --sxu-paper: #f8f9f8;
            --sxu-white: #ffffff;
        }
        html, body, [class*="css"] {
            font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
        }
        .stApp { color: var(--sxu-ink); background: var(--sxu-paper); }
        [data-testid="stHeader"] { background: rgba(248, 249, 248, .92); }
        .block-container { max-width: 1180px; padding-top: 1rem; padding-bottom: 3rem; }
        .sxu-masthead {
            display: flex; align-items: center; justify-content: space-between; gap: 2rem;
            box-sizing: border-box; width: 100%; max-width: 100%; padding: .6rem 0 1rem;
            overflow: hidden; border-bottom: 1px solid var(--sxu-line);
        }
        .sxu-logo { display: block; width: 100%; max-width: 430px; height: auto; }
        .sxu-owner { text-align: right; }
        .sxu-owner strong { display: block; color: var(--sxu-teal); font-size: .88rem; font-weight: 600; }
        .sxu-owner span { color: var(--sxu-muted); font-size: .76rem; line-height: 1.8; }
        .sxu-hero {
            position: relative; min-height: 330px; margin: 0 0 2rem; padding: clamp(3rem, 7vw, 5.5rem) clamp(1rem, 4vw, 3rem);
            overflow: hidden; border-bottom: 1px solid var(--sxu-line); background: var(--sxu-white);
        }
        .sxu-hero::before {
            content: ""; position: absolute; top: 0; left: clamp(1rem, 4vw, 3rem);
            width: 62px; height: 8px; background: var(--sxu-teal);
            box-shadow: 70px 0 0 var(--sxu-cyan);
        }
        .sxu-watermark {
            position: absolute; right: -2.5rem; top: 50%; width: min(410px, 40vw); transform: translateY(-50%);
            opacity: .11; mix-blend-mode: multiply; pointer-events: none;
        }
        .sxu-hero-content { position: relative; z-index: 1; width: 100%; max-width: 760px; }
        .sxu-kicker { color: var(--sxu-teal); font: 600 .78rem/1.4 Arial, sans-serif; letter-spacing: .18em; }
        .sxu-hero h1 {
            margin: 1.05rem 0 .85rem; color: var(--sxu-ink);
            font: 300 clamp(2.35rem, 5.2vw, 4.6rem)/1.13 "Microsoft YaHei Light", "微软雅黑 Light", "Microsoft YaHei", sans-serif;
            letter-spacing: .02em;
        }
        .sxu-hero h1 span { color: var(--sxu-teal); }
        .sxu-hero p { max-width: 720px; margin: 0; color: #586164; font-size: 1rem; line-height: 1.9; overflow-wrap: anywhere; }
        .sxu-index {
            display: flex; align-items: center; gap: .8rem; margin-top: 1.5rem;
            color: var(--sxu-teal); font: 600 .76rem/1 Arial, sans-serif; letter-spacing: .16em;
        }
        .sxu-index::before { content: ""; width: 36px; height: 3px; background: var(--sxu-cyan); }
        .privacy-note {
            margin: .4rem 0 1rem; padding: .8rem 1rem; border-left: 4px solid var(--sxu-cyan);
            color: #536063; background: #eef8f8; font-size: .85rem;
        }
        h1, h2, h3 { color: var(--sxu-ink); font-family: "Microsoft YaHei Light", "微软雅黑 Light", "Microsoft YaHei", sans-serif; }
        div[data-testid="stFileUploader"], div[data-testid="stAudioInput"] {
            padding: 1rem; border: 1px dashed #91b7b9; background: var(--sxu-white);
        }
        div[data-testid="stMetric"] { padding: 1rem; border-top: 3px solid var(--sxu-teal); background: var(--sxu-white); }
        div[data-baseweb="tab-list"] { border-bottom: 1px solid var(--sxu-line); }
        div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {
            border-radius: 0; border-color: var(--sxu-teal);
        }
        div[data-testid="stDownloadButton"] button[kind="primary"], div[data-testid="stButton"] button[kind="primary"] {
            background: var(--sxu-teal);
        }
        @media (max-width: 700px) {
            .sxu-masthead { align-items: flex-start; flex-direction: column; gap: .6rem; }
            .block-container { box-sizing: border-box; padding-left: 1rem; padding-right: 1rem; overflow-x: hidden; }
            .sxu-masthead img.sxu-logo { width: 330px !important; max-width: 92vw !important; }
            .sxu-owner { text-align: left; }
            .sxu-hero { min-height: 290px; padding: 3rem .4rem 2.4rem; }
            .sxu-hero::before { left: .4rem; }
            .sxu-watermark { right: -4rem; width: 68vw; opacity: .07; }
            .sxu-hero h1 { font-size: clamp(2.05rem, 11vw, 3rem); }
            .sxu-hero p { max-width: 100%; font-size: .92rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def file_signature(file_name: str, file_bytes: bytes) -> str:
    """用文件名和内容哈希识别上传是否变化。"""

    digest = hashlib.sha256(file_bytes).hexdigest()
    return f"{file_name}:{digest}"


def render_header() -> None:
    """使用 PPT 中的校名标识、校徽水印和版式绘制页首。"""

    logo_uri = image_data_uri("shanxi-university-logo.png")
    seal_uri = image_data_uri("shanxi-university-seal.png")
    st.markdown(
        f"""
        <div class="sxu-masthead">
            <img class="sxu-logo" src="{logo_uri}" alt="山西大学校名标识">
            <div class="sxu-owner">
                <strong>山西大学人工智能学院 · Python 程序设计课程设计</strong>
                <span>2501 班　侯世俊　202501071025</span>
            </div>
        </div>
        <section class="sxu-hero">
            <img class="sxu-watermark" src="{seal_uri}" alt="">
            <div class="sxu-hero-content">
                <div class="sxu-kicker">AUDIO SIGNAL ANALYSIS · VISUALIZATION</div>
                <h1>语音信号分析<br><span>与可视化系统</span></h1>
                <p>读取、聆听并理解一段声音：从基础幅值到短时能量、过零率、频谱统计、MFCC 与 STFT，使用一套可解释流程完成分析和比较。</p>
                <div class="sxu-index">SHANXI UNIVERSITY · 2026</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_single_result(result: dict) -> None:
    """展示单文件的元数据、17 项特征、三组图和 CSV。"""

    st.success(f"分析完成：{result['file_name']}")
    metric_columns = st.columns(4)
    metric_columns[0].metric("采样率", f"{result['sample_rate']:,} Hz")
    metric_columns[1].metric("声道数", result["channels"])
    metric_columns[2].metric("采样点数", f"{result['num_samples']:,}")
    metric_columns[3].metric("音频时长", f"{result['duration']:.3f} 秒")

    st.audio(result["audio_bytes"], format="audio/wav")
    st.caption(f"原始数据类型：{result['original_dtype']}")
    st.subheader("17 项时域与频域特征")
    st.dataframe(result["feature_rows"], hide_index=True, width="stretch")
    st.download_button(
        "下载单文件分析 CSV",
        data=result["csv_bytes"],
        file_name=result["csv_name"],
        mime="text/csv",
        type="primary",
    )

    figure_tabs = st.tabs(["波形与频谱", "STFT 声谱图", "短时特征与 MFCC"])
    with figure_tabs[0]:
        st.image(result["overview_png"], caption="时域波形与全局频谱", width="stretch")
    with figure_tabs[1]:
        st.image(result["stft_png"], caption="短时傅里叶变换声谱图", width="stretch")
    with figure_tabs[2]:
        st.image(result["advanced_png"], caption="短时能量、过零率与 13 维 MFCC", width="stretch")


def render_single_mode() -> None:
    """接收上传或现场录制的 WAV，并执行同一套深度分析。"""

    source = st.radio(
        "音频来源",
        ["上传 WAV 文件", "使用麦克风录音"],
        horizontal=True,
        key="single_source",
    )

    if source == "上传 WAV 文件":
        audio_file = st.file_uploader(
            "选择一个 WAV 音频",
            type=["wav"],
            accept_multiple_files=False,
            key="single_uploader",
            help="单个文件不超过 12 MB；系统不会写入项目 data 目录。",
        )
        empty_message = "请先上传一个 WAV 文件。"
    else:
        st.caption("首次录音时，浏览器会请求麦克风权限。录制完成后可先试听，再生成分析结果。")
        audio_file = st.audio_input(
            "录制一段音频",
            sample_rate=16_000,
            key="single_recorder",
            help="建议录制 3～10 秒；录音只用于当前会话的分析。",
        )
        empty_message = "请点击麦克风按钮开始录音。"

    if audio_file is not None:
        file_bytes = audio_file.getvalue()
        file_name = (
            "microphone_recording.wav"
            if source == "使用麦克风录音"
            else audio_file.name
        )
        signature = file_signature(file_name, file_bytes)
        if st.button("生成深度分析结果", type="primary", width="stretch"):
            try:
                with st.spinner("正在读取音频、计算特征并生成图像……"):
                    result = analyze_wav_bytes(file_name, file_bytes)
                st.session_state["single_result"] = result
                st.session_state["single_signature"] = signature
            except (ValueError, OSError) as error:
                st.error(f"音频分析失败：{error}")

        if st.session_state.get("single_signature") == signature:
            render_single_result(st.session_state["single_result"])
    else:
        st.info(empty_message)


def render_comparison_mode() -> None:
    """接收两个 WAV，执行统一尺度的特征比较。"""

    left_column, right_column = st.columns(2)
    with left_column:
        upload_a = st.file_uploader("音频 A", type=["wav"], key="compare_a")
    with right_column:
        upload_b = st.file_uploader("音频 B", type=["wav"], key="compare_b")

    if upload_a is None or upload_b is None:
        st.info("请分别选择音频 A 和音频 B。")
        return

    bytes_a = upload_a.getvalue()
    bytes_b = upload_b.getvalue()
    signature = "|".join([
        file_signature(upload_a.name, bytes_a),
        file_signature(upload_b.name, bytes_b),
    ])

    if st.button("生成双文件比较结果", type="primary", width="stretch"):
        try:
            with st.spinner("正在使用同一套算法比较两个文件……"):
                result = compare_wav_bytes(upload_a.name, bytes_a, upload_b.name, bytes_b)
            st.session_state["comparison_result"] = result
            st.session_state["comparison_signature"] = signature
        except (ValueError, OSError) as error:
            st.error(f"音频比较失败：{error}")

    if st.session_state.get("comparison_signature") == signature:
        result = st.session_state["comparison_result"]
        st.success("双文件比较完成")
        st.dataframe(result["table_rows"], hide_index=True, width="stretch")
        st.image(result["chart_png"], caption="幅度与平均能量统一比较", width="stretch")
        st.download_button(
            "下载双文件比较 CSV",
            data=result["csv_bytes"],
            file_name=result["csv_name"],
            mime="text/csv",
            type="primary",
        )


def main() -> None:
    """按固定顺序组装完整页面，供本地和魔搭入口共同调用。"""

    st.set_page_config(
        page_title="语音信号分析与可视化系统",
        page_icon="〰",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    render_header()
    st.markdown('<div class="sxu-index">01 / 在线分析</div>', unsafe_allow_html=True)
    st.header("选择分析模式")
    st.markdown(
        '<div class="privacy-note">隐私提示：公网平台会接收上传内容，请勿上传机密、隐私或无权处理的录音。临时文件在每次分析结束后自动删除。</div>',
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "分析模式",
        ["单文件深度分析", "双文件特征比较"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "单文件深度分析":
        render_single_mode()
    else:
        render_comparison_mode()

    with st.expander("查看计算流程与指标边界"):
        st.markdown(
            """
            1. 读取 WAV 并获取采样率、声道数、采样点数与时长。
            2. 将整数采样归一化后计算幅度、能量、RMS、短时能量和过零率。
            3. 计算主频、频谱质心、带宽、85% 滚降点和平坦度。
            4. 使用 25 ms 帧长、10 ms 帧移、26 个 Mel 滤波器计算 13 维 MFCC。
            5. 绘制波形、频谱、STFT 以及短时特征四联图。

            这些指标用于描述音频，不执行语音识别或身份判断；主频也不自动等同于人的基频。
            """
        )

if __name__ == "__main__":
    main()
