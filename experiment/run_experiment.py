import os
import csv
import sys

# Tambahkan fixed_code ke path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixed_code')))
from dataset_loader import load_dataset
from preprocessing import preprocess_dataset
from parallel_processor import run_parallel


def main():
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dataset/weather_data.csv'))

    print("Memuat dataset untuk benchmark...")
    raw_data = load_dataset(dataset_path)
    cleaned_data = preprocess_dataset(raw_data)

    dataset_sizes = [10000, 50000, 100000]
    worker_configs = [2, 4, 8]

    results = []

    for size in dataset_sizes:
        print(f"\n==================================================")
        print(f"--- Eksperimen Dataset Size: {size:,} records ---")
        print(f"==================================================")
        subset = cleaned_data[:size]

        # 1. Jalankan Sequential sebagai Baseline
        proc_seq, _, _, counts_seq, _, exec_time_seq = run_parallel(subset, mode="Sequential", workers=1)
        thr_seq = size / exec_time_seq if exec_time_seq > 0 else 0
        speedup_seq = 1.0

        # Validasi dasar Sequential
        assert proc_seq == size, f"FAIL: Sequential processed ({proc_seq}) != size ({size})"
        assert sum(counts_seq.values()) == size, f"FAIL: Sequential count sum ({sum(counts_seq.values())}) != size ({size})"

        results.append([
            "Sequential", size, 1, exec_time_seq, thr_seq, speedup_seq,
            proc_seq, counts_seq.get("Clear", 0), counts_seq.get("Cloudy", 0),
            counts_seq.get("Rain", 0), counts_seq.get("Hot", 0)
        ])
        print(f"Sequential      | {size:,} rec | 1 worker  | Time: {exec_time_seq:.6f}s | Speedup: 1.000x | Preds: {counts_seq}")

        # 2. Parallel Benchmark & Cross-Method Consistency Validation
        for w in worker_configs:
            # Multithreading
            proc_th, _, _, counts_th, _, exec_time_th = run_parallel(subset, mode="Multithreading", workers=w)
            thr_th = size / exec_time_th if exec_time_th > 0 else 0
            sp_th = exec_time_seq / exec_time_th if exec_time_th > 0 else 1.0

            # Cross-validation
            assert proc_th == size, f"FAIL: Threading ({w}w) processed ({proc_th}) != size ({size})"
            assert counts_th == counts_seq, f"FAIL: Threading ({w}w) counts {counts_th} != Sequential {counts_seq}"

            results.append([
                "Threading", size, w, exec_time_th, thr_th, sp_th,
                proc_th, counts_th.get("Clear", 0), counts_th.get("Cloudy", 0),
                counts_th.get("Rain", 0), counts_th.get("Hot", 0)
            ])
            print(f"Threading       | {size:,} rec | {w} workers | Time: {exec_time_th:.6f}s | Speedup: {sp_th:.3f}x | Match: OK")

            # Multiprocessing
            proc_mp, _, _, counts_mp, _, exec_time_mp = run_parallel(subset, mode="Multiprocessing", workers=w)
            thr_mp = size / exec_time_mp if exec_time_mp > 0 else 0
            sp_mp = exec_time_seq / exec_time_mp if exec_time_mp > 0 else 1.0

            # Cross-validation
            assert proc_mp == size, f"FAIL: Multiprocessing ({w}w) processed ({proc_mp}) != size ({size})"
            assert counts_mp == counts_seq, f"FAIL: Multiprocessing ({w}w) counts {counts_mp} != Sequential {counts_seq}"

            results.append([
                "Multiprocessing", size, w, exec_time_mp, thr_mp, sp_mp,
                proc_mp, counts_mp.get("Clear", 0), counts_mp.get("Cloudy", 0),
                counts_mp.get("Rain", 0), counts_mp.get("Hot", 0)
            ])
            print(f"Multiprocessing | {size:,} rec | {w} workers | Time: {exec_time_mp:.6f}s | Speedup: {sp_mp:.3f}x | Match: OK")

    # Tulis hasil ke CSV dengan skema PRD V3
    out_csv = os.path.join(os.path.dirname(__file__), "result.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Method", "Dataset_Size", "Workers", "Execution_Time",
            "Throughput", "Speedup", "Processed_Records",
            "Clear_Count", "Cloudy_Count", "Rain_Count", "Hot_Count"
        ])
        writer.writerows(results)

    print(f"\n[SUCCESS] Semua validasi konsistensi lulus (PASS)!")
    print(f"Hasil eksperimen disimpan ke: {out_csv}")


if __name__ == "__main__":
    main()
