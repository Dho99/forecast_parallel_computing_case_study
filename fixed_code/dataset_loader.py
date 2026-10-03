import csv
import os

REQUIRED_COLUMNS = {"Location", "Date_Time", "Temperature_C", "Humidity_pct", "Precipitation_mm", "Wind_Speed_kmh"}

def load_dataset(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File tidak ditemukan: {filepath}")

    records = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames) if reader.fieldnames else set()
        
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f"Kolom wajib tidak lengkap, kurang: {missing}")
            
        for row in reader:
            records.append(row)
            
    return records
