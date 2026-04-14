import asyncio
import os
import json

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder


TOKEN = os.getenv("BOT_TOKEN")
REG_URL = os.getenv("REG_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# DATA
# =========================
with open("cities.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

EARNINGS = {i["city"].lower(): i for i in raw}

# =========================
# ARBITRAGE TRACKING (RAM)
# =========================
USER_STAGE = {}   # cold / warm / hot
EVENTS = {
    "earnings_open": 0,
    "city_entered": 0,
    "reg_click": 0
}

# =========================
# KEYBOARDS
# =========================
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Доход", callback_data="earnings")
    kb.button(text="🚀 Начать", callback_data="start")
    kb.adjust(1)
    return kb.as_markup()


def reg_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Начать зарабатывать", url=REG_URL)
    kb.adjust(1)
    return kb.as_markup()


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    USER_STAGE[user_id] = "cold"

    await message.answer(
        "🚴 Курьерская работа\n\n"
        "💰 Узнай доход в твоём городе",
        reply_markup=main_menu()
    )


# =========================
# ENTRY POINT
# =========================
@dp.callback_query(F.data == "earnings")
async def earnings(callback: CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    USER_STAGE[user_id] = "warm"

    EVENTS["earnings_open"] += 1

    await callback.message.answer(
        "📍 Напиши свой город\n\n"
        "💡 Пример: Москва"
    )


# =========================
# CITY HANDLER (PRO LOGIC)
# =========================
@dp.message()
async def city_handler(message: Message):
    user_id = message.from_user.id

    if USER_STAGE.get(user_id) != "warm":
        return

    city = message.text.lower().strip()

    data = EARNINGS.get(city)

    if not data:
        for k in EARNINGS:
            if city in k:
                data = EARNINGS[k]
                break

    if not data:
        await message.answer("❌ Город не найден")
        return

    USER_STAGE[user_id] = "hot"
    EVENTS["city_entered"] += 1

    # 💣 PRO FOMO + CTA
    text = (
        f"📍 {data['city']}\n\n"
        f"🚶 Пеший: {data['foot']}₽/час\n"
        f"🚴 Вело: {data['bike']}₽/час\n"
        f"🚗 Авто: {data['auto']}₽/час\n\n"
        f"🔥 Сейчас высокий спрос в этом городе\n"
        f"⚡ Подключаются новые курьеры прямо сегодня\n\n"
        "👇 Начни сейчас"
    )

    await message.answer(text, reply_markup=reg_kb())


# =========================
# FAST LANE (ПРОДАЖА СРАЗУ)
# =========================
@dp.callback_query(F.data == "start")
async def fast_start(callback: CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    USER_STAGE[user_id] = "hot"

    await callback.message.answer(
        "🚀 Быстрый старт\n\n"
        "💰 Можно начать за 15 минут\n\n"
        "👇 Подключение:",
        reply_markup=reg_kb()
    )


# =========================
# RUN
# =========================
async def main():
    print("🔥 ARBITRAGE PRO RUNNING")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
