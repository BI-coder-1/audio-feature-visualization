from pathlib import Path
from src.audio_comparator import build_comparison_rows, save_comparison_csv, plot_feature_comparison

current_dir = Path(__file__).parent
samples_dir = current_dir / "samples"
results_dir = current_dir / "results" / "lesson05"

sample1 = samples_dir / "0_0_1.wav"
sample2 = samples_dir / "4_0_1.wav"


def main():
    while True:
        print("\n" + "=" * 30)
        print("语音信号分析与可视化系统")
        print("=" * 30)
        print("1. 单文件可视化 (时域+频谱)")
        print("2. 多文件特征比较 (导出CSV和对比图)")
        print("0. 退出")
        choice = input("请输入选项 (0-2): ")

        if choice == '1':
            from src.audio_loader import load_wav
            from src.audio_visualizer import plot_audio_overview
            out_path = results_dir / "0_0_1_overview.png"
            audio = load_wav(str(sample1))
            plot_audio_overview(audio, out_path)
            print(f"完成！图片保存在 {out_path}")

        elif choice == '2':
            rows = build_comparison_rows([sample1, sample2])
            csv_path = results_dir / "feature_comparison.csv"
            save_comparison_csv(rows, csv_path)
            print(f"CSV 已保存至: {csv_path}")
            png_path = results_dir / "feature_comparison.png"
            plot_feature_comparison(rows, png_path)
            print(f"对比图已保存至: {png_path}")

        elif choice == '0':
            print("退出系统。")
            break
        else:
            print("无效输入，请重新选择！")


if __name__ == "__main__":
    main()