# Parallel Weather Forecast Simulation (PRD V3)

Simulasi Prediksi Kondisi Cuaca Berdasarkan Data Historis Menggunakan Komputasi Paralel dengan Output Prediksi Fungsional & Rebaseline Eksperimen.

---

## 📌 Identitas
- **Nama** : Ridho Awwaludin
- **NIM**  : 247006111014
- **Mata Kuliah** : Komputasi Paralel dan Terdistribusi

---

## 1. Background
Pemrosesan data meteorologi historis berskala besar memerlukan arsitektur komputasi yang efisien. Proyek ini mensimulasikan pemrosesan data cuaca Kaggle untuk memprediksi kategori kondisi cuaca (`Clear`, `Cloudy`, `Rain`, `Hot`) menggunakan tiga paradigma: **Sequential**, **Multithreading**, dan **Multiprocessing**. Proyek ini bertujuan mengukur metrik performa (*Execution Time*, *Throughput*, *Speedup*) sekaligus menghasilkan distribusi prediksi cuaca secara konsisten dan terverifikasi.

---

## 2. Input Dataset & Preprocessing
- **Dataset**: Kaggle Weather Dataset (`dataset/weather_data.csv`).
- **Atribut**: `Location`, `Date_Time`, `Temperature_C`, `Humidity_pct`, `Precipitation_mm`, `Wind_Speed_kmh`.
- **Unit Rekord**:
  ```json
  {
    "Location": "London",
    "Date_Time": "2024-01-01 00:01",
    "temperature": 10.7,
    "humidity": 56.0,
    "precipitation": 2.2,
    "wind_speed": 16.1
  }
  ```

---

## 3. Weather Prediction Classification
Pengklasifikasian kondisi cuaca dilakukan oleh fungsi `predict_weather(record)` dengan aturan kategorisasi berikut:
1. `precipitation > 5.0` ➔ **Rain**
2. `humidity > 80.0` ➔ **Cloudy**
3. `temperature > 30.0` ➔ **Hot**
4. `else` ➔ **Clear**

---

## 4. System Pipeline & Architecture
```text
Weather Dataset (weather_data.csv)
      │
      ▼
Dataset Loader (CSV Schema Validation)
      │
      ▼
Data Preprocessing (Data Cleansing & Normalization)
      │
      ▼
Task Partitioning (Data Chunk Slicing)
      │
      ▼
Worker Execution (predict_weather for each record)
      │
      ▼
Local Aggregation (Local Counts & Local Partial Metrics)
      │
      ▼
Result Reduction (Main Thread / Parent Process Aggregation)
      │
      ├───────────────────────────────┬──────────────────────────────┐
      ▼                               ▼                              ▼
Weather Prediction Summary    Sample Weather Predictions     Performance Metrics
(Clear, Cloudy, Rain, Hot)    (5 Deterministic Records)    (Time, Throughput, Speedup)
```

---

## 5. Result Aggregation Mechanism (`fixed_code`)
- **Local Aggregation + Result Reduction**: Setiap worker menghitung hasil agregasi secara lokal pada chunk datanya (*thread-local/process-local*).
- **No Shared Mutable State**: Tidak ada shared global variables, shared dictionaries, shared Value/Array, maupun Lock contention.
- **IPC / Future Reduction**: Hasil parsial dikembalikan ke main thread / main process melalui `ThreadPoolExecutor` / `ProcessPoolExecutor` lalu digabungkan secara deterministik.

---

## 6. Bug Analysis & Demonstration (`code_with_bug`)
- **Lokasi Bug**: `code_with_bug/parallel_processor.py` (`worker_thread` dan `worker_multiprocess`).
- **Jenis Bug**: **Race Condition** (*Unsynchronized Shared State / Lost Updates*).
- **Penyebab**: Banyak worker membaca dan memperbarui variabel global/shared memory (`processed_records`, `total_temperature`, `total_humidity`, `pred_clear`, `pred_cloudy`, `pred_rain`, `pred_hot`) secara langsung tanpa sinkronisasi (`Lock`, `Queue`, dll). Operasi `+=` bukan atomic.
- **Dampak**: Terjadi *lost update*, jumlah record terproses berkurang drastis (misal 25,000 dari 100,000), dan total distribusi prediksi menjadi korup/tidak konsisten.

---

## 7. Rebased Experiment Results

### Skema Log CSV (`experiment/result.csv`)
Header: `Method,Dataset_Size,Workers,Execution_Time,Throughput,Speedup,Processed_Records,Clear_Count,Cloudy_Count,Rain_Count,Hot_Count`

### Ringkasan Benchmark (Dataset Size: 100,000 Records)
| Method | Workers | Execution Time (s) | Throughput (rec/s) | Speedup | Clear | Cloudy | Rain | Hot |
|---|---|---|---|---|---|---|---|---|
| Sequential | 1 | 0.024122s | 4,145,634 | 1.000x | 68,539 | 18,564 | 4,709 | 8,188 |
| Threading | 2 | 0.025964s | 3,851,518 | 0.929x | 68,539 | 18,564 | 4,709 | 8,188 |
| Threading | 4 | 0.025912s | 3,859,173 | 0.931x | 68,539 | 18,564 | 4,709 | 8,188 |
| Threading | 8 | 0.030011s | 3,332,144 | 0.804x | 68,539 | 18,564 | 4,709 | 8,188 |
| Multiprocessing | 2 | 0.256031s | 390,577 | 0.094x | 68,539 | 18,564 | 4,709 | 8,188 |
| Multiprocessing | 4 | 0.275197s | 363,375 | 0.088x | 68,539 | 18,564 | 4,709 | 8,188 |
| Multiprocessing | 8 | 0.341187s | 293,094 | 0.071x | 68,539 | 18,564 | 4,709 | 8,188 |

### Cross-Method Consistency Validation
- **Hasil**: **PASS**
- Untuk setiap ukuran dataset (10k, 50k, 100k), nilai distribusi prediksi dari `Sequential`, `Threading`, dan `Multiprocessing` terbukti **100% identik**.

---

## 📂 Struktur Proyek Sesuai PRD V3
```text
Parallel_Weather_Forecast_Simulation/
├── dataset/
│   └── weather_data.csv
├── code_with_bug/
│   ├── main.py
│   ├── dataset_loader.py
│   ├── preprocessing.py
│   ├── weather_prediction.py
│   ├── parallel_processor.py
│   └── README.md
├── fixed_code/
│   ├── main.py
│   ├── dataset_loader.py
│   ├── preprocessing.py
│   ├── weather_prediction.py
│   ├── parallel_processor.py
│   └── README.md
├── experiment/
│   ├── run_experiment.py
│   ├── result.csv
│   ├── generate_chart.py
│   ├── exec_time_vs_threads.png
│   ├── exec_time_vs_processes.png
│   └── speedup_vs_config.png
├── output/
│   └── predictions.csv             (Dihasilkan jika --save-predictions diaktifkan)
├── requirements.txt
└── README.md
```

---

## ⚡ Cara Menjalankan Program
```bash
# Menjalankan Code With Bug
python code_with_bug/main.py --method Multithreading --workers 4

# Menjalankan Fixed Code
python fixed_code/main.py --method Multithreading --workers 4
python fixed_code/main.py --method Multiprocessing --workers 4

# Menjalankan Fixed Code dan Menyimpan Prediksi ke CSV
python fixed_code/main.py --method Sequential --save-predictions

# Menjalankan Eksperimen Benchmark Automatis & Regenerasi Grafik
python experiment/run_experiment.py
python experiment/generate_chart.py
```
