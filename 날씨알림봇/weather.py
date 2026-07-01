import requests
from datetime import datetime

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("☀️", "맑음"),
    1: ("🌤️", "대체로 맑음"),
    2: ("⛅", "구름 조금"),
    3: ("☁️", "흐림"),
    45: ("🌫️", "안개"),
    48: ("🌫️", "안개"),
    51: ("🌦️", "이슬비"),
    53: ("🌦️", "이슬비"),
    55: ("🌦️", "이슬비"),
    61: ("🌧️", "비"),
    63: ("🌧️", "비"),
    65: ("🌧️", "폭우"),
    71: ("🌨️", "눈"),
    73: ("🌨️", "눈"),
    75: ("❄️", "폭설"),
    80: ("🌦️", "소나기"),
    81: ("🌧️", "소나기"),
    82: ("⛈️", "강한 소나기"),
    95: ("⛈️", "뇌우"),
    99: ("⛈️", "뇌우"),
}

OUTFIT_GUIDE = [
    (28, "👕 반팔, 반바지"),
    (23, "👔 반팔, 얇은 긴팔"),
    (17, "🧥 얇은 가디건, 긴바지"),
    (12, "🧣 자켓, 가디건"),
    (7,  "🧤 코트, 두꺼운 니트"),
    (0,  "🧥 패딩, 두꺼운 코트"),
]

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def get_coordinates(city: str):
    try:
        res = requests.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "ko"}, timeout=5)
        data = res.json()
        result = data["results"][0]
        return result["latitude"], result["longitude"], result.get("name", city)
    except Exception:
        return None, None, city


def get_weather(city: str):
    lat, lon, city_name = get_coordinates(city)
    if lat is None:
        return None

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "weathercode", "precipitation_probability"],
        "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "timezone": "Asia/Seoul",
        "forecast_days": 7,
    }

    try:
        res = requests.get(WEATHER_URL, params=params, timeout=5)
        data = res.json()
    except Exception:
        return None

    current = data["current"]
    daily = data["daily"]

    temp_now = round(current["temperature_2m"])
    code_now = current["weathercode"]
    emoji_now, desc_now = WEATHER_CODES.get(code_now, ("🌡️", "알 수 없음"))
    precip_now = current.get("precipitation_probability", 0)

    temp_max = round(daily["temperature_2m_max"][0])
    temp_min = round(daily["temperature_2m_min"][0])

    outfit = next((o for threshold, o in OUTFIT_GUIDE if temp_max >= threshold), "🧥 패딩, 두꺼운 코트")

    weekly = []
    for i in range(7):
        date_str = daily["time"][i]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day = WEEKDAYS[dt.weekday()]
        code = daily["weathercode"][i]
        emoji, _ = WEATHER_CODES.get(code, ("🌡️", ""))
        t_max = round(daily["temperature_2m_max"][i])
        t_min = round(daily["temperature_2m_min"][i])
        rain = daily["precipitation_probability_max"][i]
        weekly.append((day, emoji, t_max, t_min, rain))

    return {
        "city": city_name,
        "temp_now": temp_now,
        "temp_max": temp_max,
        "temp_min": temp_min,
        "emoji": emoji_now,
        "desc": desc_now,
        "precip": precip_now,
        "outfit": outfit,
        "weekly": weekly,
    }


def format_weather_message(data: dict, full: bool = True) -> str:
    today = datetime.now()
    date_str = today.strftime(f"%Y년 %m월 %d일 ({WEEKDAYS[today.weekday()]})")

    msg = (
        f"{data['emoji']} 오늘의 {data['city']} 날씨\n"
        f"📅 {date_str}\n"
        f"{'─' * 20}\n"
        f"날씨 : {data['desc']}\n"
        f"🌡️ 최고 {data['temp_max']}°C / 최저 {data['temp_min']}°C\n"
        f"☔ 강수확률 : {data['precip']}%\n\n"
        f"👗 오늘의 옷차림\n"
        f"{data['outfit']}\n"
    )

    if full:
        msg += f"\n📆 주간 날씨\n{'─' * 20}\n"
        for day, emoji, t_max, t_min, rain in data["weekly"]:
            rain_str = f"  ☔{rain}%" if rain >= 30 else ""
            msg += f"{day} {emoji} {t_max}°C / {t_min}°C{rain_str}\n"

    msg += "\n오늘도 좋은 하루 되세요! 😊"
    return msg


def format_current_message(data: dict) -> str:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"{data['emoji']} 현재 {data['city']} 날씨\n"
        f"🕐 {now_str} 기준\n"
        f"{'─' * 20}\n"
        f"날씨 : {data['desc']}\n"
        f"🌡️ 현재 {data['temp_now']}°C (최고 {data['temp_max']}°C / 최저 {data['temp_min']}°C)\n"
        f"☔ 강수확률 : {data['precip']}%\n\n"
        f"👗 옷차림 추천\n"
        f"{data['outfit']}"
    )
