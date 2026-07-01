import sys, os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

sys.path.insert(0, os.path.dirname(__file__))
from weather import get_weather
from database import init_db, save_weather, get_history
import config

init_db()

app = FastAPI(title="날씨알림봇 대시보드 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def serve_dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    return FileResponse(html_path, media_type="text/html")


@app.get("/api/weather")
def api_weather(city: str = config.CITY):
    data = get_weather(city)
    if not data:
        return {"ok": False, "error": "날씨 정보를 가져오는 데 실패했습니다."}

    save_weather(data, log_type="대시보드 조회")

    weekly = [
        {"day": d, "icon": icon, "max": t_max, "min": t_min, "rain": rain}
        for d, icon, t_max, t_min, rain in data["weekly"]
    ]

    return {
        "ok":         True,
        "city":       data["city"],
        "temp_now":   data["temp_now"],
        "temp_max":   data["temp_max"],
        "temp_min":   data["temp_min"],
        "icon":       data["emoji"],
        "desc":       data["desc"],
        "precip":     data["precip"],
        "outfit":     data["outfit"],
        "weekly":     weekly,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@app.get("/api/history")
def api_history(limit: int = 20):
    return {"ok": True, "history": get_history(limit)}


if __name__ == "__main__":
    import uvicorn
    print(f"대시보드 주소: http://127.0.0.1:{config.DASHBOARD_PORT}")
    uvicorn.run(app, host="127.0.0.1", port=config.DASHBOARD_PORT)
