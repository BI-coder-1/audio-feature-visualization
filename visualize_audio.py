from pathlib import Path
from src.audio_loader import load_wav
from src.audio_visualizer import plot_audio_overview

current_dir = Path(__file__).parent
sample_path = current_dir / "samples" / "0_0_1.wav"
output_path = current_dir / "results" / "lesson04" / "0_0_1_overview.png"

print("正在读取音频...")
audio = load_wav(str(sample_path))

print("正在生成可视化图表...")
plot_audio_overview(audio, output_path)

print(f"完成！图片已保存至: {output_path.resolve()}")