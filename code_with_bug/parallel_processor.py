import threading
import multiprocessing
import time
from weather_prediction import predict_weather

# --- Global Shared Variables for Threading (with Race Conditions) ---
processed_records_thread = 0
total_temperature_thread = 0.0
total_humidity_thread = 0.0
pred_clear_thread = 0
pred_cloudy_thread = 0
pred_rain_thread = 0
pred_hot_thread = 0

# --- Shared Variables for Multiprocessing (Lock=False for Race Conditions) ---
processed_records_mp = multiprocessing.Value('i', 0, lock=False)
total_temperature_mp = multiprocessing.Value('d', 0.0, lock=False)
total_humidity_mp = multiprocessing.Value('d', 0.0, lock=False)
pred_clear_mp = multiprocessing.Value('i', 0, lock=False)
pred_cloudy_mp = multiprocessing.Value('i', 0, lock=False)
pred_rain_mp = multiprocessing.Value('i', 0, lock=False)
pred_hot_mp = multiprocessing.Value('i', 0, lock=False)


def reset_globals():
    global processed_records_thread, total_temperature_thread, total_humidity_thread
    global pred_clear_thread, pred_cloudy_thread, pred_rain_thread, pred_hot_thread
    processed_records_thread = 0
    total_temperature_thread = 0.0
    total_humidity_thread = 0.0
    pred_clear_thread = 0
    pred_cloudy_thread = 0
    pred_rain_thread = 0
    pred_hot_thread = 0

    processed_records_mp.value = 0
    total_temperature_mp.value = 0.0
    total_humidity_mp.value = 0.0
    pred_clear_mp.value = 0
    pred_cloudy_mp.value = 0
    pred_rain_mp.value = 0
    pred_hot_mp.value = 0


def process_sequential(records):
    processed = 0
    tot_temp = 0.0
    tot_hum = 0.0
    counts = {"Clear": 0, "Cloudy": 0, "Rain": 0, "Hot": 0}
    all_preds = []

    for r in records:
        pred = predict_weather(r)
        processed += 1
        tot_temp += r["temperature"]
        tot_hum += r["humidity"]
        counts[pred] = counts.get(pred, 0) + 1
        all_preds.append(pred)

    return processed, tot_temp, tot_hum, counts, all_preds


def worker_thread(records_subset, barrier):
    global processed_records_thread, total_temperature_thread, total_humidity_thread
    global pred_clear_thread, pred_cloudy_thread, pred_rain_thread, pred_hot_thread

    # Synchronize start to maximize concurrent race conditions
    barrier.wait()

    for idx, r in enumerate(records_subset):
        pred = predict_weather(r)

        # INTENTIONAL RACE CONDITION:
        # Non-atomic load, yield, write sequence causing lost updates in multithreading
        curr_processed = processed_records_thread
        curr_temp = total_temperature_thread
        curr_hum = total_humidity_thread
        c_clear = pred_clear_thread
        c_cloudy = pred_cloudy_thread
        c_rain = pred_rain_thread
        c_hot = pred_hot_thread

        if idx % 100 == 0:
            time.sleep(0.0001)  # Context switch window

        processed_records_thread = curr_processed + 1
        total_temperature_thread = curr_temp + r["temperature"]
        total_humidity_thread = curr_hum + r["humidity"]

        if pred == "Clear":
            pred_clear_thread = c_clear + 1
        elif pred == "Cloudy":
            pred_cloudy_thread = c_cloudy + 1
        elif pred == "Rain":
            pred_rain_thread = c_rain + 1
        elif pred == "Hot":
            pred_hot_thread = c_hot + 1


def worker_multiprocess(records_subset, p_count, p_temp, p_hum, p_clear, p_cloudy, p_rain, p_hot, barrier):
    barrier.wait()

    for idx, r in enumerate(records_subset):
        pred = predict_weather(r)

        # INTENTIONAL RACE CONDITION in shared memory without locks
        curr_processed = p_count.value
        curr_temp = p_temp.value
        curr_hum = p_hum.value
        c_clear = p_clear.value
        c_cloudy = p_cloudy.value
        c_rain = p_rain.value
        c_hot = p_hot.value

        if idx % 100 == 0:
            time.sleep(0.0001)

        p_count.value = curr_processed + 1
        p_temp.value = curr_temp + r["temperature"]
        p_hum.value = curr_hum + r["humidity"]

        if pred == "Clear":
            p_clear.value = c_clear + 1
        elif pred == "Cloudy":
            p_cloudy.value = c_cloudy + 1
        elif pred == "Rain":
            p_rain.value = c_rain + 1
        elif pred == "Hot":
            p_hot.value = c_hot + 1


def run_parallel(records, mode, workers=4):
    reset_globals()
    start_time = time.time()
    all_preds = [predict_weather(r) for r in records]  # Evaluate for predictions list

    if mode == "Sequential":
        proc, tot_temp, tot_hum, counts, _ = process_sequential(records)
        elapsed = time.time() - start_time
        return proc, tot_temp, tot_hum, counts, all_preds, elapsed

    elif mode == "Multithreading":
        chunk_size = len(records) // workers
        threads = []
        barrier = threading.Barrier(workers)

        for i in range(workers):
            start_idx = i * chunk_size
            end_idx = len(records) if i == workers - 1 else (i + 1) * chunk_size
            subset = records[start_idx:end_idx]

            t = threading.Thread(target=worker_thread, args=(subset, barrier))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        elapsed = time.time() - start_time
        counts = {
            "Clear": pred_clear_thread,
            "Cloudy": pred_cloudy_thread,
            "Rain": pred_rain_thread,
            "Hot": pred_hot_thread
        }
        return processed_records_thread, total_temperature_thread, total_humidity_thread, counts, all_preds, elapsed

    elif mode == "Multiprocessing":
        chunk_size = len(records) // workers
        processes = []
        barrier = multiprocessing.Barrier(workers)

        for i in range(workers):
            start_idx = i * chunk_size
            end_idx = len(records) if i == workers - 1 else (i + 1) * chunk_size
            subset = records[start_idx:end_idx]

            p = multiprocessing.Process(
                target=worker_multiprocess,
                args=(subset, processed_records_mp, total_temperature_mp, total_humidity_mp,
                      pred_clear_mp, pred_cloudy_mp, pred_rain_mp, pred_hot_mp, barrier)
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        elapsed = time.time() - start_time
        counts = {
            "Clear": pred_clear_mp.value,
            "Cloudy": pred_cloudy_mp.value,
            "Rain": pred_rain_mp.value,
            "Hot": pred_hot_mp.value
        }
        return processed_records_mp.value, total_temperature_mp.value, total_humidity_mp.value, counts, all_preds, elapsed

    else:
        raise ValueError(f"Mode tidak dikenal: {mode}")
