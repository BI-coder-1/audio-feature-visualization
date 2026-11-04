from pathlib import Path
from src.audio_loader import load_wav
from src.audio_visualizer import plot_audio_overview
from src.audio_comparator import build_comparison_rows, save_comparison_csv, plot_feature_comparison
from src.audio_spectrogram import plot_stft_overview
from src.audio_advanced_features import extract_advanced_summary, plot_advanced_overview

current_dir = Path(__file__).parent
samples_dir = current_dir / "samples"
lesson04_results = current_dir / "results" / "lesson04"
lesson05_results = current_dir / "results" / "lesson05"
lesson06_results = current_dir / "results" / "lesson06"
advanced_results = current_dir / "results" / "advanced"

sample1 = samples_dir / "0_0_1.wav"
sample2 = samples_dir / "4_0_1.wav"

advanced_feature_labels = {
    "mean_short_time_energy": "平均短时能量",
    "max_short_time_energy": "最大短时能量",
    "mean_zero_crossing_rate": "平均过零率",
    "high_energy_frame_ratio": "相对高能帧占比",
    "dominant_frequency_hz": "主频 (Hz)",
    "spectral_centroid_hz": "频谱质心 (Hz)",
    "spectral_bandwidth_hz": "频谱带宽 (Hz)",
    "spectral_rolloff_85_hz": "85% 频谱滚降点 (Hz)",
    "spectral_flatness": "频谱平坦度",
}


def main():
    while True:
        print("\n" + "=" * 30)
        print("语音信号分析与可视化系统")
        print("=" * 30)
        print("1. 单文件可视化 (时域+频谱)")
        print("2. 多文件特征比较 (CSV+柱状图)")
        print("3. STFT声谱图")
        print("4. 进阶分析 (短时能量+过零率+频谱统计+MFCC)")
        print("0. 退出")
        choice = input("请输入选项 (0-4): ")

        if choice == '1':
            out_path = lesson04_results / "0_0_1_overview.png"
            audio = load_wav(str(sample1))
            plot_audio_overview(audio, out_path)
            print(f"完成！图片保存在 {out_path}")

        elif choice == '2':
            rows = build_comparison_rows([sample1, sample2])
            csv_path = lesson05_results / "feature_comparison.csv"
            save_comparison_csv(rows, csv_path)
            print(f"CSV 已保存至: {csv_path}")
            png_path = lesson05_results / "feature_comparison.png"
            plot_feature_comparison(rows, png_path)
            print(f"对比图已保存至: {png_path}")

        elif choice == '3':
            out_path = lesson06_results / "0_0_1_stft.png"
            audio = load_wav(str(sample1))
            plot_stft_overview(audio, out_path)
            print(f"STFT声谱图已保存至: {out_path}")

        elif choice == '4':
            audio = load_wav(str(sample1))
            summary = extract_advanced_summary(audio)
            print("\n进阶音频特征：")
            for feature_name, feature_value in summary.items():
                label = advanced_feature_labels[feature_name]
                print(f"  {label}: {feature_value:.6f}")

            out_path = advanced_results / "0_0_1_advanced.png"
            plot_advanced_overview(audio, out_path)
            print(f"进阶分析图已保存至: {out_path}")

        elif choice == '0':
            print("退出系统。")
            break
        else:
            print("无效输入，请重新选择！")


if __name__ == "__main__":
    main()
