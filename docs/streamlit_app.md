# Streamlit 公网页面与魔搭入口说明

## 1. 为什么保留两个网页入口

项目没有把原来的 Flask 页面删除：

- `python -m web_app` 启动 Flask 本地版，适合学习路由、模板、HTML、CSS 和表单上传。
- `streamlit run app.py` 启动 Streamlit 版，适合发布到魔搭创空间。

两个入口都调用 `src` 中同一批音频算法，因此不会出现“本地算一种结果，公网又算另一种结果”的问题。

## 2. 代码区域怎样分工

### `app.py`

魔搭的 Streamlit 创空间从项目根目录寻找 `app.py`。本文件只导入并调用 `streamlit_app.main()`，不重复任何页面或算法代码。这样做有三个好处：

1. 满足魔搭的固定入口约定。
2. 本地和公网执行同一个 `main()`，避免两套页面逐渐产生差异。
3. 入口只有少量代码，本科生可以直接看懂程序从哪里开始运行。

### `streamlit_app.py`

这一层只负责网页交互：

1. `main()` 是页面总装函数，按固定顺序调用其他小函数。
2. `st.set_page_config()` 设置网页标题、图标和宽屏布局。
3. `inject_styles()` 使用课程提供的山西大学 PPT 模板配色、细线和留白规则组织页面；校名标识与校徽来自该模板。
4. 页首采用紧凑校标、作者信息和功能导航；“系统首页、音频分析、结果展示、原理说明”使用页内锚点，GitHub 在新标签页打开项目仓库。
5. `st.file_uploader()` 在浏览器中显示 WAV 选择框，`st.audio_input()` 调用浏览器麦克风录制 WAV。
6. `st.button()` 让分析只在用户主动点击后执行。
7. `st.spinner()` 在计算期间显示等待提示。
8. `st.metric()`、`st.dataframe()`、`st.image()` 和 `st.audio()` 分别展示元数据、特征表、图像和音频播放器。
9. `st.download_button()` 把内存中的 CSV 交给浏览器下载。
10. 上传文件和麦克风录音都转换为 WAV 字节，并进入同一个 `analyze_wav_bytes()`，因此两种输入不会产生两套计算标准。
11. `st.session_state` 暂存当前会话的结果，避免点击下载或切换控件时立刻丢失分析内容。

页面中的学院、班级、姓名和学号是作者归属标识，不等同于专利或软件著作权登记。

### `web_app/streamlit_support.py`

这一层负责文件和算法衔接：

1. `validate_wav_upload()` 检查扩展名、空文件和 12 MB 大小限制。
2. `secure_filename()` 清理用户文件名，避免文件名被解释为路径。
3. `TemporaryDirectory()` 创建一次请求专用的临时目录，函数结束后自动删除。
4. `load_wav()` 将 WAV 读取为统一的 `AudioSample`。
5. `extract_basic_features()` 与 `extract_advanced_summary()` 计算 17 项描述特征。
6. 三个绘图函数生成波形/频谱、STFT、短时能量/过零率/MFCC 图。
7. 图片在临时目录删除前读成 `bytes`，Streamlit 直接从内存显示。
8. CSV 使用 UTF-8 BOM，便于 Windows Excel 正确显示中文。

这层不导入 Streamlit，所以可以在命令行测试，也可以被未来的其他界面复用。

## 3. 为什么计算前要写临时文件

浏览器上传后得到的是一串二进制字节，而课程中的 `load_wav()` 接收文件路径。将字节写入 `TemporaryDirectory`，既能复用课程代码，也不会污染 `data`、`samples` 或 `results`。函数返回前，图片和 CSV 会被读回内存；退出 `with` 后临时文件自动删除。

## 4. 为什么使用 SHA-256 文件签名

Streamlit 每次点击控件都会从头执行脚本。页面把“文件名 + 文件内容 SHA-256”作为签名：

- 上传文件未变化时，继续显示 `session_state` 中的结果。
- 上传内容变化时，旧结果不会错误地显示在新文件下方。

SHA-256 在这里只用于识别当前会话中的文件变化，不用于证明作者身份，也不会上传到项目仓库。

## 5. 本地运行和测试

```powershell
Set-Location -LiteralPath 'G:\ICASSP\python_houshijun_test'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

浏览器默认打开 `http://localhost:8501`。测试命令：

```powershell
.\.venv\Scripts\python.exe test_streamlit_app.py
```

测试会验证：非 WAV 被拒绝、17 项特征齐全、三张图确为 PNG、CSV 编码正确、双文件顺序正确，并使用 Streamlit 的 `AppTest` 从魔搭入口 `app.py` 启动页面，检查标题、上传入口和录音入口是否正常。

### 麦克风录音为什么能直接分析

`st.audio_input()` 在浏览器端请求麦克风权限，并把录音包装为一个内存中的 WAV 文件。程序调用 `getvalue()` 取得字节，再以 `microphone_recording.wav` 作为显示文件名传给已有处理层。后续的格式校验、临时文件、17 项特征、三组图和 CSV 与上传 WAV 完全相同。

公网录音要求浏览器允许麦克风权限，通常也要求页面通过 HTTPS 打开；魔搭公网地址已经使用 HTTPS。本地 `localhost` 也被浏览器视为可用的安全环境。

## 6. 魔搭公网部署

PR 合并到 `main` 后：

1. 打开 `https://modelscope.cn/studios` 并登录。
2. 点击“我要创建”，名称建议使用 `sxu-audio-analysis-202501071025`。
3. 调试阶段选择私有，应用部署框架选择 Streamlit。
4. 云资源选择免费 CPU，镜像使用平台推荐版本。
5. 导入 GitHub `main` 分支，或使用创空间页面提供的 Git 仓库地址上传代码。
6. 确认根目录存在 `app.py` 和 `requirements.txt`，点击确认并部署。
7. 在日志中确认依赖安装完成，并在页面验证上传、播放、图表和 CSV 下载。
8. 全部正常后再改为公开，并复制平台实际生成的访问链接。

创空间地址通常是：

```text
https://modelscope.cn/studios/<用户名>/<创空间名>
```

魔搭会读取根目录的 `requirements.txt` 安装依赖，并通过根目录 `app.py` 启动 Streamlit。`.streamlit/config.toml` 将单文件上传限制为 12 MB。免费 CPU 空闲后可能休眠，重新访问时等待平台再次启动即可。完整操作清单见 `docs/modelscope_deployment.md`。

## 7. 隐私和能力边界

- 用户文件不写入课程项目的 `data` 目录，也不提交到 GitHub。
- 麦克风录音只进入当前浏览器会话的内存分析流程，不会写入课程数据集。
- 临时文件会在本次分析函数结束后删除，但公网平台仍然会接收上传字节，因此不要上传机密、隐私或无权处理的录音。
- `session_state` 只服务于当前浏览器会话，不是长期数据库。
- 免费 CPU 存在休眠和资源限制，不承诺高并发或持续在线。
- 系统只做描述性分析，不训练语音识别模型，也不判断说话人身份。
