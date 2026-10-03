import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def generate_charts(csv_path=None, output_dir=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if csv_path is None:
        csv_path = os.path.join(base_dir, "result.csv")
    if output_dir is None:
        output_dir = base_dir

    if not os.path.exists(csv_path):
        print(f"File {csv_path} tidak ditemukan!")
        return

    df = pd.read_csv(csv_path)

    sns.set_theme(style="whitegrid")

    # 1. Execution Time vs Number of Thread
    plt.figure(figsize=(8, 5))
    df_threads = df[df["Method"] == "Threading"].copy()
    sns.lineplot(data=df_threads, x="Workers", y="Execution_Time", hue="Dataset_Size", marker="o", palette="Set1")
    plt.title("Execution Time vs Number of Thread")
    plt.xlabel("Number of Thread (2, 4, 8)")
    plt.ylabel("Execution Time (s)")
    plt.xticks([2, 4, 8])
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "exec_time_vs_threads.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()

    # 2. Execution Time vs Number of Process
    plt.figure(figsize=(8, 5))
    df_proc = df[df["Method"] == "Multiprocessing"].copy()
    sns.lineplot(data=df_proc, x="Workers", y="Execution_Time", hue="Dataset_Size", marker="s", palette="Set2")
    plt.title("Execution Time vs Number of Process")
    plt.xlabel("Number of Process (2, 4, 8)")
    plt.ylabel("Execution Time (s)")
    plt.xticks([2, 4, 8])
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "exec_time_vs_processes.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()

    # 3. Speedup vs Configuration
    plt.figure(figsize=(11, 5))
    df_speedup = df.copy()

    def make_config_label(row):
        m = row["Method"]
        w = int(row["Workers"])
        if m == "Sequential":
            return "Sequential"
        elif m == "Threading":
            return f"Thread-{w}"
        elif m == "Multiprocessing":
            return f"Process-{w}"
        return f"{m}-{w}"

    df_speedup["Configuration"] = df_speedup.apply(make_config_label, axis=1)

    config_order = ["Sequential", "Thread-2", "Thread-4", "Thread-8", "Process-2", "Process-4", "Process-8"]
    sns.barplot(data=df_speedup, x="Configuration", y="Speedup", hue="Dataset_Size", order=config_order, palette="viridis")
    plt.title("Speedup vs Configuration")
    plt.xlabel("Configuration")
    plt.ylabel("Speedup (x)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "speedup_vs_config.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()

    print("Berhasil membuat 3 grafik analisis performa:")
    print(f" - {chart1_path}")
    print(f" - {chart2_path}")
    print(f" - {chart3_path}")


if __name__ == "__main__":
    generate_charts()
