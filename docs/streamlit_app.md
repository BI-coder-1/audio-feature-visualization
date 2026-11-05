# Streamlit 公网页面说明

## 1. 为什么保留两个网页入口

项目没有把原来的 Flask 页面删除：

- `python -m web_app` 启动 Flask 本地版，适合学习路由、模板、HTML、CSS 和表单上传。
- `streamlit run streamlit_app.py` 启动 Streamlit 版，适合免费发布到公网。

两个入口都调用 `src` 中同一批音频算法，因此不会出现“本地算一种结果，公网又算另一种结果”的问题。

## 2. 代码区域怎样分工

### `streamlit_app.py`

这一层只负责网页交互：

1. `st.set_page_config()` 设置网页标题、图标和宽屏布局。
2. `inject_styles()` 注入深蓝色课程设计样式，不复制学校官网素材。
3. `st.file_uploader()` 在浏览器中显示 WAV 选择框。
4. `st.button()` 让分析只在用户主动点击后执行。
5. `st.spinner()` 在计算期间显示等待提示。
6. `st.metric()`、`st.dataframe()`、`st.image()` 和 `st.audio()` 分别展示元数据、特征表、图像和音频播放器。
7. `st.download_button()` 把内存中的 CSV 交给浏览器下载。
8. `st.session_state` 暂存当前会话的结果，避免点击下载或切换控件时立刻丢失分析内容。

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
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

浏览器默认打开 `http://localhost:8501`。测试命令：

```powershell
.\.venv\Scripts\python.exe test_streamlit_app.py
```

测试会验证：非 WAV 被拒绝、17 项特征齐全、三张图确为 PNG、CSV 编码正确、双文件顺序正确，并使用 Streamlit 的 `AppTest` 确认首页启动时没有异常。

## 6. 免费公网部署

PR 合并到 `main` 后：

1. 打开 `https://share.streamlit.io/` 并登录。
2. 连接拥有仓库管理权限的 GitHub 账号。
3. 点击 **Create app**，选择已有应用。
4. Repository 填写 `BI-coder-1/audio-feature-visualization`。
5. Branch 选择 `main`。
6. Main file path 填写 `streamlit_app.py`。
7. Advanced settings 中选择 Python 3.12。
8. 自定义子域名建议填写 `sxu-audio-analysis-202501071025`。
9. 点击 Deploy，等待依赖安装与页面启动。

如果该子域名仍可用，地址将是：

```text
https://sxu-audio-analysis-202501071025.streamlit.app
```

Streamlit Community Cloud 会读取根目录的 `requirements.txt` 安装依赖，并读取 `.streamlit/config.toml` 将单文件上传限制为 12 MB。GitHub 的 `main` 更新后，云端应用会自动重新部署。

## 7. 隐私和能力边界

- 用户文件不写入课程项目的 `data` 目录，也不提交到 GitHub。
- 临时文件会在本次分析函数结束后删除，但公网平台仍然会接收上传字节，因此不要上传机密、隐私或无权处理的录音。
- `session_state` 只服务于当前浏览器会话，不是长期数据库。
- 免费平台存在休眠和资源限制，不承诺高并发或持续在线。
- 系统只做描述性分析，不训练语音识别模型，也不判断说话人身份。
