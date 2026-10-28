

# работа с погодным API


import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


# Поиск города по названию
def find_city(city_name: str) -> dict:
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city_name,
            "count": 1,
            "language": "ru",
            "format": "json",
        },
        timeout=15,
    )
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        raise ValueError("Город не найден. Проверьте название.")

    city = results[0]

    return {
        "name": city["name"],
        "country": city.get("country", ""),
        "latitude": city["latitude"],
        "longitude": city["longitude"],
    }


# прогноз на 7 дней
def get_forecast(latitude: float, longitude: float) -> dict:
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "forecast_days": 7,
            "timezone": "auto",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


# Единая функция получения погоды
def get_city_weather(city_name: str) -> dict:
    city = find_city(city_name)

    forecast = get_forecast(
        city["latitude"],
        city["longitude"],
    )

    return {
        "city": city,
        "forecast": forecast,
    }
