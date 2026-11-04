\# 课程设计最终功能验收清单



| 原始要求 | 对应实现 | 测试或证据 |

|---|---|---|

| 读取WAV | `src/audio\_loader.py` | `test\_load.py` |

| 获取采样率、声道、点数、时长 | `AudioSample` 类 | `test\_load.py` |

| 计算幅度和能量 | `src/audio\_features.py` | `test\_features.py` |

| 时域波形 | `src/audio\_visualizer.py` | 第四课时 PNG |

| 频谱 | `compute\_single\_sided\_spectrum()` | `test\_visualization.py` |

| 多文件比较 | `src/audio\_comparator.py` | CSV、柱状图、`test\_comparison.py` |

| STFT 提高功能 | `src/audio\_spectrogram.py` | 声谱图、`test\_spectrogram.py` |

| 综合系统 | `main.py` | 菜单选项 1～3 |

