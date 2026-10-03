import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from weather_prediction import predict_weather


def process_chunk(records_subset):
    local_processed = 0
    local_temp = 0.0
    local_hum = 0.0
    local_counts = {"Clear": 0, "Cloudy": 0, "Rain": 0, "Hot": 0}
    local_predictions = []

    for r in records_subset:
        pred = predict_weather(r)
        local_processed += 1
        local_temp += r["temperature"]
        local_hum += r["humidity"]
        local_counts[pred] = local_counts.get(pred, 0) + 1
        local_predictions.append(pred)

    return local_processed, local_temp, local_hum, local_counts, local_predictions


def split_chunks(records, workers):
    chunk_size = len(records) // workers
    chunks = []
    for i in range(workers):
        start_idx = i * chunk_size
        end_idx = len(records) if i == workers - 1 else (i + 1) * chunk_size
        chunks.append(records[start_idx:end_idx])
    return chunks


def run_parallel(records, mode, workers=4):
    start_time = time.time()

    if mode == "Sequential":
        proc, tot_temp, tot_hum, counts, preds = process_chunk(records)
        elapsed = time.time() - start_time
        return proc, tot_temp, tot_hum, counts, preds, elapsed

    elif mode == "Multithreading":
        # FIX: tiap worker menghitung agregasi lokal, hasil digabung di main thread.
        # Tidak ada shared global state -> tidak ada race condition.
        chunks = split_chunks(records, workers)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(process_chunk, chunks))

        proc = sum(r[0] for r in results)
        tot_temp = sum(r[1] for r in results)
        tot_hum = sum(r[2] for r in results)
        pred_counts = {"Clear": 0, "Cloudy": 0, "Rain": 0, "Hot": 0}
        all_preds = []
        for r in results:
            for k, v in r[3].items():
                pred_counts[k] = pred_counts.get(k, 0) + v
            all_preds.extend(r[4])

        elapsed = time.time() - start_time
        return proc, tot_temp, tot_hum, pred_counts, all_preds, elapsed

    elif mode == "Multiprocessing":
        # FIX: tiap process kembalikan partial result via IPC,
        # agregasi dilakukan di parent process. Tanpa shared memory tanpa lock.
        chunks = split_chunks(records, workers)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(process_chunk, chunks))

        proc = sum(r[0] for r in results)
        tot_temp = sum(r[1] for r in results)
        tot_hum = sum(r[2] for r in results)
        pred_counts = {"Clear": 0, "Cloudy": 0, "Rain": 0, "Hot": 0}
        all_preds = []
        for r in results:
            for k, v in r[3].items():
                pred_counts[k] = pred_counts.get(k, 0) + v
            all_preds.extend(r[4])

        elapsed = time.time() - start_time
        return proc, tot_temp, tot_hum, pred_counts, all_preds, elapsed

    else:
        raise ValueError(f"Mode tidak dikenal: {mode}")
