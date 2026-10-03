def predict_weather(record):
    prec = record["precipitation"]
    hum = record["humidity"]
    temp = record["temperature"]

    if prec > 5.0:
        weather = "Rain"
    elif hum > 80.0:
        weather = "Cloudy"
    elif temp > 30.0:
        weather = "Hot"
    else:
        weather = "Clear"

    return weather
