import asyncio
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
REG_URL = os.getenv("REG_URL")

CHANNEL_LINK = f"https://t.me/{CHANNEL_ID.replace('@', '')}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# ДАННЫЕ
# =========================
NAMES = ["Алексей", "Иван", "Дмитрий", "Максим", "Сергей"]

CHAT_FLOW = [
    "Сегодня сделал 3100₽ 🔥",
    "Заказов реально много",
    "Подключился вчера — уже работаю",
    "Вечером пик, хорошо платят",
]

# =========================
# КНОПКИ
# =========================
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Стать курьером", callback_data="new")
    kb.button(text="💬 Я уже курьер", callback_data="old")
    kb.button(text="❓ Вопросы", callback_data="faq")
    kb.adjust(1)
    return kb.as_markup()


def sub_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться", url=CHANNEL_LINK)
    kb.button(text="✅ Я подписался", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()


def reg_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Перейти к регистрации", url=REG_URL)
    return kb.as_markup()


def back_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="menu")
    return kb.as_markup()


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
async def check_subscription(user_id):
    for _ in range(2):
        try:
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status not in ("left", "kicked"):
                return True
        except:
            pass
        await asyncio.sleep(2)
    return False


# =========================
# LIVE CHAT
# =========================
async def live_chat(user_id):
    await asyncio.sleep(2)
    await bot.send_message(user_id, "💬 Подключение к чату курьеров...")

    for _ in range(3):
        name = random.choice(NAMES)
        msg = random.choice(CHAT_FLOW)
        await asyncio.sleep(2)
        await bot.send_message(user_id, f"👤 {name}: {msg}")


# =========================
# ДОЖИМ
# =========================
async def reminder(user_id):
    await asyncio.sleep(600)
    await bot.send_message(
        user_id,
        "⏳ Ты не завершил регистрацию\n\n"
        "💰 Можно начать уже сегодня",
        reply_markup=reg_kb()
    )


# =========================
# START
# =========================
@dp.message(CommandStart(deep_link=True))
async def start(message: Message, command: CommandStart):
    user_name = message.from_user.first_name
    spots = random.randint(5, 20)

    text = (
        f"👋 {user_name}, работа курьером Яндекс Еда\n\n"
        "💰 Доход до 3000₽ в день\n"
        "⚡ Старт за 15 минут\n\n"
        f"⚠️ Осталось {spots} мест\n\n"
        "👇 Выбери, что тебе нужно"
    )

    await message.answer(text, reply_markup=main_menu())


# =========================
# МЕНЮ
# =========================
@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery):
    await callback.message.answer("👇 Выбери:", reply_markup=main_menu())


# =========================
# ВЕТКА 1 — НОВЫЙ
# =========================
@dp.callback_query(F.data == "new")
async def new_user(callback: CallbackQuery):
    await callback.message.answer(
        "🚀 Начнём подключение\n\n"
        "📢 Подпишись на канал для доступа",
        reply_markup=sub_kb()
    )


# =========================
# ВЕТКА 2 — УЖЕ КУРЬЕР
# =========================
@dp.callback_query(F.data == "old")
async def old_user(callback: CallbackQuery):
    await callback.message.answer(
        "💬 Доступ к чату курьеров\n\n"
        "📢 Подпишись на канал, чтобы:\n"
        "— общаться с курьерами\n"
        "— получать лайфхаки\n"
        "— видеть реальные доходы\n\n"
        "👇 После подписки нажми кнопку",
        reply_markup=sub_kb()
    )


# =========================
# ВЕТКА 3 — FAQ
# =========================
@dp.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery):
    text = (
        "❓ Частые вопросы\n\n"
        "💰 Сколько платят?\n"
        "— до 3000₽ в день\n\n"
        "📍 Нужен ли опыт?\n"
        "— нет\n\n"
        "📱 Что нужно?\n"
        "— телефон\n\n"
        "👇 Выбери действие"
    )

    await callback.message.answer(text, reply_markup=main_menu())


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await check_subscription(user_id):

        await callback.message.answer("✅ Доступ подтверждён")

        asyncio.create_task(live_chat(user_id))

        await asyncio.sleep(4)

        await callback.message.answer(
            "🔓 Доступ открыт\n\n"
            "👇 Выбери действие:",
            reply_markup=reg_kb()
        )

        asyncio.create_task(reminder(user_id))

    else:
        await callback.message.answer(
            "❌ Подпишись на канал",
            reply_markup=sub_kb()
        )


# =========================
# RUN
# =========================
async def main():
    print("🔥 Бот с ветками запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
