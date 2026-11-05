# Python 语音信号分析与可视化系统

本科课程设计项目。

## 任务要求（原始）

必须实现：

1. 读取自己录制的或电脑中存储的 WAV 音频文件，获取采样率、声道数、采样点数量及音频时长。
2. 计算音频幅度、平均能量或其他基础统计特征。
3. 绘制时域波形，并展示频谱或声谱图。
4. 对不同音频文件进行特征比较。

提高功能：使用短时傅里叶变换、短时能量或过零率分析语音片段。

重点考查：NumPy、音频文件处理、信号特征计算、Matplotlib。

注意：可选 SciPy 或其他轻量级工具；不要求训练语音识别模型。

## 环境

- Python 3.12
- 虚拟环境：`.venv`
- 依赖：见 `requirements.txt`

## 目录

- `src/` 源码
- `samples/` 示例音频（小样本）
- `results/` 运行输出
- `docs/` 文档
- `tests/` 测试
- `web_app/` 本地交互式网页

#### 快速开始

1. 激活虚拟环境: `.\.venv\Scripts\Activate.ps1`

2. 安装依赖: `pip install -r requirements.txt`

3. 运行 WAV 读取测试: `python test_load.py`

4. 运行基础特征计算: `python test_features.py`

5. 生成时域波形与频谱图: `python visualize_audio.py`

6. 运行可视化测试: `python test_visualization.py`

   （注：生成的图片保存在 `results/lesson04/` 目录下，不会上传到 GitHub。）

7. 运行多文件对比与导出：`python main.py` （在菜单中选择 2）

8. 运行比较测试：`python test_comparison.py`
   （注：CSV表格和对比图保存在 results/lesson05/ 目录下。）

9. 运行 STFT 声谱图测试: `python test_spectrogram.py`

10. 运行 STFT 声谱图生成: `python main.py` （在菜单中选择 3）
    （注：声谱图保存在 results/lesson06/ 目录下。）

11. 启动交互式网页：`python -m web_app`
    浏览器访问 `http://127.0.0.1:5000`，可进行单文件深度分析或双文件特征比较，并下载 CSV。上传文件只在系统临时目录中处理，分析完成后自动删除。

12. 运行网页测试：`python test_web_app.py`

13. 运行进阶特征测试：`python test_advanced_features.py`

14. 在控制台运行进阶分析：`python main.py`（在菜单中选择 4）

## 已实现特征

- 最小/最大幅值、峰值幅度
- 平均值、平均绝对幅度
- 总能量、平均能量、RMS
- 短时能量、过零率、相对高能帧占比
- 主频、频谱质心、频谱带宽、85% 滚降点、频谱平坦度
- 13 维 MFCC 及其时序热力图
- 浏览器上传 WAV、双文件比较与 CSV 结果导出
