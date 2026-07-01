import logging
import re
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from weather import get_weather, format_weather_message, format_current_message
from database import init_db, save_weather
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

init_db()

scheduler    = BackgroundScheduler()
current_city = config.CITY


def send_weather_alert(app):
    data = get_weather(current_city)
    if data:
        save_weather(data, log_type="자동 알림")
        msg = format_weather_message(data, full=True)
    else:
        msg = "⚠️ 날씨 정보를 가져오는 데 실패했습니다."
    import asyncio
    asyncio.run(app.bot.send_message(chat_id=config.CHAT_ID, text=msg))


def register_schedule(app, hour: int, minute: int):
    scheduler.remove_all_jobs()
    scheduler.add_job(send_weather_alert, trigger="cron", hour=hour, minute=minute, args=[app], id="weather_alert")
    logging.info(f"스케줄 등록: 매일 {hour:02d}:{minute:02d}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 안녕하세요! 날씨 자동 알림 봇입니다.\n\n"
        f"매일 아침 {config.ALERT_HOUR:02d}:{config.ALERT_MINUTE:02d}에 날씨를 자동으로 알려드립니다. ☀️\n\n"
        "─────────────────────\n"
        "/weather       — 지금 날씨 바로 조회\n"
        "/region 도시명 — 지역 변경 (예: /region Busan)\n"
        "/alert HH:MM   — 알림 시간 변경 (예: /alert 08:00)\n"
        "/start         — 이 메시지 다시 보기"
    )


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 날씨 정보를 가져오는 중...")
    data = get_weather(current_city)
    if data:
        save_weather(data, log_type="/weather 조회")
        await update.message.reply_text(format_current_message(data))
    else:
        await update.message.reply_text("⚠️ 날씨 정보를 가져오는 데 실패했습니다.")


async def cmd_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_city
    if not context.args:
        await update.message.reply_text("❌ 도시명을 입력해 주세요.\n예) /region Busan")
        return
    city = " ".join(context.args)
    data = get_weather(city)
    if data:
        current_city = city
        await update.message.reply_text(f"✅ 지역이 {data['city']}으로 변경되었습니다!")
    else:
        await update.message.reply_text("❌ 도시를 찾을 수 없습니다. 영문으로 입력해 주세요.")


async def cmd_alert_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not re.match(r"^\d{2}:\d{2}$", context.args[0]):
        await update.message.reply_text("❌ 형식: /alert HH:MM\n예) /alert 08:30")
        return
    hour, minute = map(int, context.args[0].split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        await update.message.reply_text("❌ 올바른 시간 범위를 입력해 주세요.")
        return
    register_schedule(update.get_bot(), hour, minute)
    config.ALERT_HOUR, config.ALERT_MINUTE = hour, minute
    await update.message.reply_text(f"✅ 알림 시간이 {context.args[0]}으로 변경되었습니다! ⏰")


async def cmd_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ 알 수 없는 명령어입니다.\n/start 로 명령어 목록을 확인하세요.")


def main():
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler(["start", "help"], cmd_start))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("region",  cmd_region))
    app.add_handler(CommandHandler("alert",   cmd_alert_set))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_unknown))

    register_schedule(app, config.ALERT_HOUR, config.ALERT_MINUTE)
    scheduler.start()

    logging.info("봇 시작!")
    app.run_polling()


if __name__ == "__main__":
    main()
