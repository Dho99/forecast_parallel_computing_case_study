import os
import argparse
from dataset_loader import load_dataset
from preprocessing import preprocess_dataset
from parallel_processor import run_parallel


def main():
    parser = argparse.ArgumentParser(
        description="Parallel Weather Forecast Simulation (Code with Bug)")
    parser.add_argument(
        "--file", type=str, default="../dataset/weather_data.csv", help="Path ke dataset CSV")
    parser.add_argument("--method", type=str, default="Multithreading", choices=[
                        "Sequential", "Multithreading", "Multiprocessing"], help="Metode pemrosesan")
    parser.add_argument("--workers", type=int, default=4,
                        help="Jumlah thread / process worker")
    parser.add_argument("--seq_time", type=float, default=None,
                        help="Waktu eksekusi sequential untuk menghitung speedup")
    parser.add_argument("--limit", type=int, default=None,
                        help="Batasi jumlah record untuk eksperimen")

    args = parser.parse_args()

    # Determine absolute or relative path
    dataset_path = args.file
    if not os.path.exists(dataset_path):
        if os.path.exists("dataset/weather_data.csv"):
            dataset_path = "dataset/weather_data.csv"
        elif os.path.exists("../dataset/weather_data.csv"):
            dataset_path = "../dataset/weather_data.csv"

    # 1. Load dataset
    raw_data = load_dataset(dataset_path)

    # 2. Preprocess dataset
    cleaned_data = preprocess_dataset(raw_data)
    if args.limit is not None:
        cleaned_data = cleaned_data[:args.limit]
    total_records = len(cleaned_data)

    # 3. Process records with parallel processor (bugged)
    processed_count, total_temp, total_hum, pred_counts, all_preds, exec_time = run_parallel(
        cleaned_data, mode=args.method, workers=args.workers)

    # 4. Calculate metrics
    avg_temp = (total_temp / processed_count) if processed_count > 0 else 0.0
    avg_hum = (total_hum / processed_count) if processed_count > 0 else 0.0
    throughput = (processed_count / exec_time) if exec_time > 0 else 0.0

    seq_time = args.seq_time if args.seq_time is not None else exec_time
    speedup = (seq_time / exec_time) if exec_time > 0 else 1.0

    worker_count = 1 if args.method == "Sequential" else args.workers

    # 5. Prediction Distribution Calculations (affected by race conditions)
    clear_cnt = pred_counts.get("Clear", 0)
    cloudy_cnt = pred_counts.get("Cloudy", 0)
    rain_cnt = pred_counts.get("Rain", 0)
    hot_cnt = pred_counts.get("Hot", 0)
    total_pred = sum(pred_counts.values())

    divisor = processed_count if processed_count > 0 else 1
    clear_pct = (clear_cnt / divisor * 100)
    cloudy_pct = (cloudy_cnt / divisor * 100)
    rain_pct = (rain_cnt / divisor * 100)
    hot_pct = (hot_cnt / divisor * 100)

    print("============================================================")
    print("PARALLEL WEATHER FORECAST SIMULATION (BUGGY)")
    print("============================================================")
    print("")
    print("Nama : Ridho Awwaludin")
    print("NIM  : 247006111014")
    print("")
    print("Dataset :")
    print("Kaggle Weather Dataset")
    print("")
    print("Processing Method :")
    print(args.method)
    print("")
    print("Dataset Size :")
    print(f"{total_records} records")
    print("")
    print("Number of Workers :")
    print(f"{worker_count}")
    print("")
    print("============================================================")
    print("PROCESSING RESULT")
    print("============================================================")
    print("")
    print("Processed Records :")
    print(f"{processed_count}")
    print("")
    print("Average Temperature :")
    print(f"{avg_temp:.2f} C")
    print("")
    print("Average Humidity :")
    print(f"{avg_hum:.2f} %")
    print("")
    print("============================================================")
    print("WEATHER PREDICTION SUMMARY (AFFECTED BY RACE CONDITIONS)")
    print("============================================================")
    print("")
    print(f"Clear  : {clear_cnt:,} ({clear_pct:.2f}%)")
    print(f"Cloudy : {cloudy_cnt:,} ({cloudy_pct:.2f}%)")
    print(f"Rain   : {rain_cnt:,} ({rain_pct:.2f}%)")
    print(f"Hot    : {hot_cnt:,} ({hot_pct:.2f}%)")
    print("")
    print("Total Prediction :")
    print(f"{total_pred:,}")
    print("")
    print("============================================================")
    print("SAMPLE WEATHER PREDICTIONS")
    print("============================================================")
    print("")
    sample_size = min(5, len(cleaned_data))
    for i in range(sample_size):
        rec = cleaned_data[i]
        pred_label = all_preds[i] if i < len(all_preds) else "Unknown"
        print(f"{i + 1}. Location   : {rec.get('Location', 'N/A')}")
        print(f"   Date Time  : {rec.get('Date_Time', 'N/A')}")
        print(f"   Temperature: {rec['temperature']:.1f} C")
        print(f"   Humidity   : {rec['humidity']:.0f} %")
        print(f"   Rainfall   : {rec['precipitation']:.1f} mm")
        print(f"   Wind Speed : {rec['wind_speed']:.1f} km/h")
        print(f"   Prediction : {pred_label}")
        print("")
    print("============================================================")
    print("PERFORMANCE")
    print("============================================================")
    print("")
    print("Execution Time :")
    print(f"{exec_time:.6f} seconds")
    print("")
    print("Throughput :")
    print(f"{int(throughput):,} records/second")
    print("")
    print("Speedup :")
    print(f"{speedup:.3f}x")
    print("")
    print("============================================================")


if __name__ == "__main__":
    main()
