# Code With Bug - Parallel Weather Forecast Simulation

## Konsep Implementasi Awal
Implementasi ini bertujuan memproses dataset cuaca skala besar dengan membagi beban kerja ke beberapa thread (Multithreading) atau proses (Multiprocessing). Setiap pekerja (worker) akan memproses subset dari data secara mandiri dan mengagregasikan hasil seperti jumlah data diproses, total temperatur, dan kelembapan ke dalam variabel global atau *shared memory*.

## Lokasi Bug
Bug terletak pada berkas `parallel_processor.py` pada dua fungsi utama:
1. `worker_thread()` (untuk Multithreading): pada baris modifikasi `processed_records_thread`, `total_temperature_thread`, dan `total_humidity_thread`.
2. `worker_multiprocess()` (untuk Multiprocessing): pada modifikasi `p_count.value`, `p_temp.value`, dan `p_hum.value`.

## Jenis Bug Paralel
**Race Condition.**
Sistem memperbarui variabel/objek komputasi agregat tanpa adanya mekanisme sinkronisasi (seperti Lock, Semaphore, atau Queue). Pembaruan nilai `+=` bukan operasi *atomic*. Ketika banyak thread/proses membaca, menambah, dan menulis ulang nilai secara nyaris bersamaan (karena lock flag dinonaktifkan pada Multiprocessing atau GIL terinterupsi pada multithreading), sebagian penambahan tertimpa oleh *worker* lain yang beroperasi di siklus CPU yang sama.

## Dampak Bug terhadap Hasil
Karena *Lost Updates* (pembaruan yang hilang), hasil akhir agregasi menjadi **tidak konsisten dan korup**. 
Jumlah `Processed Records` yang dilaporkan di akhir eksekusi akan seringkali kurang dari `Total Records` asli di dalam dataset. Rata-rata temperatur dan kelembapan juga menjadi salah perhitungan karena tidak semua data masuk secara sempurna ke dalam penjumlahan agregat global.
