# Fixed Code - Parallel Weather Forecast Simulation

## Metode Perbaikan
Pada modul ini, masalah *Race Condition* diselesaikan dengan menghilangkan *Shared Mutable State* di antara thread/proses.
1. **Map-Reduce Pattern / Isolation**: Setiap *worker* menghitung jumlah record, total suhu, dan total kelembapan pada *chunk* datanya sendiri secara lokal (*thread-local* atau *process-local*).
2. **ThreadPoolExecutor & ProcessPoolExecutor**: Menggunakan abstraksi `concurrent.futures` untuk mendistribusikan data dalam bentuk *chunks* terpisah secara otomatis.

## Mekanisme Sinkronisasi
- **Thread-Safety via Partitioning**: Karena setiap thread hanya mengakses dan mengubah data lokal di memorinya sendiri, tidak diperlukan pembacaan/penulisan bersama ke variabel global.
- **IPC / Future Aggregation**: Setelah seluruh *worker* selesai memproses subset datanya, hasil lokal dikembalikan (*returned*) dan diagregasikan di thread/proses utama (*parent process*). Hal ini menjamin operasi penambahan dilakukan secara terurut dan murni di satu alur (*single-threaded aggregator*).

## Perubahan Performa & Akurasi
- **Akurasi 100%**: `Processed Records` selalu tepat bernilai 100% dari total dataset (misal: 10.000 / 50.000 / 100.000) tanpa ada pembaruan yang hilang (*lost update*).
- **Hasil Konsisten**: Nilai rata-rata suhu dan kelembapan bersifat deterministik dan identik dengan hasil eksekusi *Sequential*.
- **Efisiensi Multiprocessing**: Pada dataset besar, pembagian tugas pada inti CPU fisik memberikan pemrosesan paralel sejati tanpa terkunci oleh Python GIL.
