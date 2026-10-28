

#погодные описания и советы


# Расшифровка погодных кодов WMO
def describe_weather(code: int) -> str:
    if code == 0:
        return "Ясно"
    if code in (1, 2):
        return "Переменная облачность"
    if code == 3:
        return "Облачно"
    if code in (45, 48):
        return "Туман"
    if code in (51, 53, 55, 56, 57):
        return "Морось"
    if code in (61, 63, 65, 66, 67):
        return "Дождь"
    if code in (71, 73, 75, 77, 85, 86):
        return "Снег или снегопад"
    if code in (80, 81, 82):
        return "Ливень"
    if code in (95, 96, 99):
        return "Гроза"

    return "Переменная погода"


# Рекомендации для пользователя
def get_recommendations(
    temperature: float,
    precipitation: float,
    wind_speed: float,
    rain_probability: float,
) -> list[str]:
    tips = []

    if temperature <= 5:
        tips.append("Наденьте тёплую куртку.")
    elif temperature >= 28:
        tips.append("Жарко: пейте воду и ищите тень.")
    elif temperature >= 20:
        tips.append("Подходящая температура для прогулки.")

    if rain_probability >= 50 or precipitation >= 1:
        tips.append("Не забудьте взять зонт.")

    if wind_speed >= 30:
        tips.append("Сильный ветер: будьте осторожны.")

    if not tips:
        tips.append("Проверьте прогноз перед выходом.")

    return tips
