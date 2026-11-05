"""Streamlit Community Cloud 公网入口。

运行命令：``streamlit run streamlit_app.py``
本文件只组织网页控件；所有音频计算由 ``src`` 和
``web_app.streamlit_support`` 完成。
"""

from __future__ import annotations

import hashlib

import streamlit as st

from web_app.streamlit_support import analyze_wav_bytes, compare_wav_bytes


st.set_page_config(
    page_title="语音信号分析与可视化系统",
    page_icon="〰",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    """加入与本地 Flask 版一致的深蓝高校课程设计视觉风格。"""

    st.markdown(
        """
        <style>
        :root {
            --navy-950: #071b30;
            --navy-900: #0a2747;
            --navy-800: #103b66;
            --blue-600: #1474bd;
            --cyan-400: #4ed6e6;
            --gold-500: #caa55b;
            --paper: #f5f7f9;
            --ink: #142231;
            --muted: #687889;
        }
        .stApp { background: var(--paper); }
        .block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 3rem; }
        .site-utility {
            padding: .45rem 1rem; color: #d9e5ef; background: var(--navy-950);
            font-size: .78rem; letter-spacing: .04em;
        }
        .site-brand {
            display: flex; align-items: center; justify-content: space-between; gap: 1.5rem;
            padding: 1.35rem 1rem; border: 1px solid #dbe2e8; background: #fff;
        }
        .brand-title { color: var(--navy-900); font-family: SimSun, STSong, serif; font-size: 1.8rem; letter-spacing: .08em; }
        .brand-subtitle { color: var(--muted); font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; }
        .identity-card { padding-left: 1rem; border-left: 2px solid var(--gold-500); text-align: right; }
        .identity-card strong { display: block; color: var(--navy-800); font-size: .82rem; letter-spacing: .06em; }
        .identity-card span { color: var(--muted); font: .7rem/1.6 Consolas, monospace; }
        .hero-panel {
            margin: 1rem 0 1.6rem; padding: clamp(2rem, 5vw, 4.5rem);
            color: #fff; background: radial-gradient(circle at 80% 20%, rgba(78,214,230,.18), transparent 30%), linear-gradient(125deg, #082846 0%, #0e4776 64%, #0a2c50 100%);
        }
        .hero-kicker { color: var(--cyan-400); font-size: .75rem; font-weight: 700; letter-spacing: .2em; }
        .hero-panel h1 { margin: .8rem 0; font-family: SimSun, STSong, serif; font-size: clamp(2.6rem, 6vw, 5rem); font-weight: 500; line-height: 1.12; }
        .hero-panel h1 span { color: #7de5ef; }
        .hero-panel p { max-width: 720px; color: #dbe9f4; }
        .section-label { margin-top: 1.4rem; color: var(--blue-600); font-size: .75rem; font-weight: 700; letter-spacing: .18em; }
        .privacy-note { padding: .8rem 1rem; border-left: 3px solid var(--gold-500); background: #fff8e8; color: #5f4c26; font-size: .85rem; }
        .author-footer { margin-top: 3rem; padding: 1.4rem; color: #b7cad9; background: #041321; text-align: center; }
        .author-footer strong { color: #fff; }
        div[data-testid="stFileUploader"] { padding: 1rem; border: 1px dashed #8da1b3; background: #fff; }
        div[data-testid="stMetric"] { padding: 1rem; border-top: 3px solid var(--navy-800); background: #fff; }
        div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button { border-radius: 0; }
        @media (max-width: 700px) {
            .site-brand { align-items: flex-start; flex-direction: column; }
            .identity-card { padding: .7rem 0 0; border-top: 2px solid var(--gold-500); border-left: 0; text-align: left; }
            .hero-panel { padding: 2rem 1.2rem; }
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
    """绘制固定标题、作者归属和课程说明。"""

    st.markdown('<div class="site-utility">Python 程序设计课程设计 · 在线音频分析</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="site-brand">
            <div>
                <div class="brand-title">〰 语音信号分析与可视化系统</div>
                <div class="brand-subtitle">Audio Signal Analysis &amp; Visualization</div>
            </div>
            <div class="identity-card">
                <strong>山西大学人工智能学院</strong>
                <span>2501 · 侯世俊 · 202501071025</span>
            </div>
        </div>
        <div class="hero-panel">
            <div class="hero-kicker">AUDIO LAB · 数字信号处理</div>
            <h1>让声音的结构<br><span>清晰可见</span></h1>
            <p>从基础幅值到短时能量、过零率、频谱统计、MFCC 与 STFT，使用一套可解释流程观察和比较 WAV 音频。</p>
        </div>
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
    """接收一个 WAV，并在按钮触发后执行深度分析。"""

    uploaded_file = st.file_uploader(
        "选择一个 WAV 音频",
        type=["wav"],
        accept_multiple_files=False,
        key="single_uploader",
        help="单个文件不超过 12 MB；系统不会写入项目 data 目录。",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        signature = file_signature(uploaded_file.name, file_bytes)
        if st.button("生成深度分析结果", type="primary", width="stretch"):
            try:
                with st.spinner("正在读取音频、计算特征并生成图像……"):
                    result = analyze_wav_bytes(uploaded_file.name, file_bytes)
                st.session_state["single_result"] = result
                st.session_state["single_signature"] = signature
            except (ValueError, OSError) as error:
                st.error(f"音频分析失败：{error}")

        if st.session_state.get("single_signature") == signature:
            render_single_result(st.session_state["single_result"])
    else:
        st.info("请先上传一个 WAV 文件。")


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


def render_footer() -> None:
    """展示作者与隐私边界。"""

    st.markdown(
        """
        <div class="author-footer">
            <strong>原创课程设计标识</strong><br>
            山西大学人工智能学院 · 2501 · 侯世俊 · 学号 202501071025<br>
            上传文件仅用于本次会话计算，不写入项目数据集
        </div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()
render_header()
st.markdown('<div class="section-label">01 / 在线分析</div>', unsafe_allow_html=True)
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

render_footer()
