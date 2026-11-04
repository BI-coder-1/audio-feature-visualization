# 课程设计最终功能验收清单

| 原始要求 | 对应实现 | 测试或证据 |
|---|---|---|
| 读取WAV | `src/audio_loader.py` | `test_load.py` |
| 获取采样率、声道、点数、时长 | `AudioSample` 类 | `test_load.py` |
| 计算幅度和能量 | `src/audio_features.py` | `test_features.py` |
| 时域波形 | `src/audio_visualizer.py` | 第四课时 PNG |
| 频谱 | `compute_single_sided_spectrum()` | `test_visualization.py` |
| 多文件比较 | `src/audio_comparator.py` | CSV、柱状图、`test_comparison.py` |
| STFT 提高功能 | `src/audio_spectrogram.py` | 声谱图、`test_spectrogram.py` |
| 综合系统 | `main.py` | 菜单选项 1～3 |
