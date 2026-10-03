def preprocess_record(record):
    try:
        if not record:
            return None

        for val in record.values():
            if val is None or str(val).strip() == "":
                return None

        temp = float(record["Temperature_C"])
        hum = float(record["Humidity_pct"])
        prec = float(record["Precipitation_mm"])
        wind = float(record["Wind_Speed_kmh"])

        return {
            "Location": record.get("Location", ""),
            "Date_Time": record.get("Date_Time", ""),
            "temperature": temp,
            "humidity": hum,
            "precipitation": prec,
            "wind_speed": wind
        }
    except (ValueError, KeyError):
        return None

def preprocess_dataset(records):
    cleaned = []
    for r in records:
        processed = preprocess_record(r)
        if processed is not None:
            cleaned.append(processed)
    return cleaned
