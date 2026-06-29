import logging
import re
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from weather import get_weather, format_weather_message, format_current_message
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

scheduler = BackgroundScheduler()
current_city = config.CITY


def send_weather_alert(app):
    data = get_weather(current_city)
    if data:
        msg = format_weather_message(data, full=True)
    else:
        msg = "⚠️ 날씨 정보를 가져오는 데 실패했습니다.\n잠시 후 /날씨 명령어로 다시 조회해 주세요."

    import asyncio
    asyncio.run(app.bot.send_message(chat_id=config.CHAT_ID, text=msg))


def register_schedule(app, hour: int, minute: int):
    scheduler.remove_all_jobs()
    scheduler.add_job(
        send_weather_alert,
        trigger="cron",
        hour=hour,
        minute=minute,
        args=[app],
        id="weather_alert",
    )
    logging.info(f"스케줄 등록: 매일 {hour:02d}:{minute:02d}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 안녕하세요!\n"
        "날씨 자동 알림 봇입니다.\n\n"
        f"매일 아침 {config.ALERT_HOUR:02d}:{config.ALERT_MINUTE:02d}에 날씨를 자동으로 알려드립니다. ☀️\n\n"
        "─────────────────────\n"
        "사용 가능한 명령어\n"
        "/weather — 지금 날씨 바로 조회\n"
        "/region 도시명 — 지역 변경\n"
        "       예) /region Busan\n"
        "/alert HH:MM — 알림 시간 변경\n"
        "       예) /alert 08:00\n"
        "/start — 이 메시지 다시 보기"
    )
    await update.message.reply_text(msg)


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 날씨 정보를 가져오는 중...")
    data = get_weather(current_city)
    if data:
        await update.message.reply_text(format_current_message(data))
    else:
        await update.message.reply_text("⚠️ 날씨 정보를 가져오는 데 실패했습니다.\n잠시 후 다시 시도해 주세요.")


async def cmd_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_city
    if not context.args:
        await update.message.reply_text(
            "❌ 도시명을 입력해 주세요.\n예) /지역 Busan"
        )
        return

    city = " ".join(context.args)
    data = get_weather(city)
    if data:
        current_city = city
        await update.message.reply_text(
            f"✅ 지역이 {data['city']}으로 변경되었습니다.\n다음 알림부터 {data['city']} 날씨를 알려드릴게요! 🌊"
        )
    else:
        await update.message.reply_text(
            "❌ 도시를 찾을 수 없습니다.\n영문 도시명으로 입력해 주세요.\n예) /지역 Busan"
        )


async def cmd_alert_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ 시간을 입력해 주세요.\n예) /알림설정 08:30"
        )
        return

    time_str = context.args[0]
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        await update.message.reply_text(
            "❌ 시간 형식이 올바르지 않습니다.\nHH:MM 형식으로 입력해 주세요.\n예) /알림설정 08:30"
        )
        return

    hour, minute = map(int, time_str.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        await update.message.reply_text("❌ 올바른 시간 범위를 입력해 주세요. (00:00 ~ 23:59)")
        return

    register_schedule(update.get_bot(), hour, minute)
    config.ALERT_HOUR = hour
    config.ALERT_MINUTE = minute
    await update.message.reply_text(f"✅ 알림 시간이 {time_str}으로 변경되었습니다! ⏰")


async def cmd_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ 알 수 없는 명령어입니다.\n\n"
        "사용 가능한 명령어:\n"
        "/날씨 /지역 /알림설정 /시작"
    )


def main():
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler(["start", "help"], cmd_start))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("region", cmd_region))
    app.add_handler(CommandHandler("alert", cmd_alert_set))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_unknown))

    register_schedule(app, config.ALERT_HOUR, config.ALERT_MINUTE)
    scheduler.start()

    logging.info("봇 시작!")
    app.run_polling()


if __name__ == "__main__":
    main()
