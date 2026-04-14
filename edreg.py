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
def start_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Начать", callback_data="start_flow")
    return kb.as_markup()

def sub_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться", url=CHANNEL_LINK)
    kb.button(text="✅ Я подписался", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

def reg_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Начать работу", url=REG_URL)
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
# ЖИВОЙ ЧАТ (СЦЕНАРИЙ)
# =========================
async def live_chat(user_id):
    try:
        await asyncio.sleep(3)

        await bot.send_message(user_id, "💬 Подключение к чату курьеров...")

        await asyncio.sleep(2)

        for _ in range(3):
            name = random.choice(NAMES)
            msg = random.choice(CHAT_FLOW)

            await bot.send_message(
                user_id,
                f"👤 {name}: {msg}"
            )

            await asyncio.sleep(random.randint(2, 4))

    except:
        pass

# =========================
# ПРОГРЕВ ПЕРЕД РЕГОЙ
# =========================
async def pre_sell(user_id):
    await asyncio.sleep(2)

    await bot.send_message(
        user_id,
        "📊 Твой прогресс:\n\n"
        "Шаг 1 ✅ Вход\n"
        "Шаг 2 ✅ Доступ\n"
        "Шаг 3 🔒 Регистрация\n"
    )

    await asyncio.sleep(2)

    await bot.send_message(
        user_id,
        "💰 Чтобы начать получать заказы — нужно завершить регистрацию"
    )

# =========================
# ДОЖИМ X10
# =========================
async def reminder(user_id):
    try:
        await asyncio.sleep(600)

        await bot.send_message(
            user_id,
            "⏳ Ты почти начал зарабатывать\n\n"
            "Не хватает одного шага",
            reply_markup=reg_kb()
        )

        await asyncio.sleep(3600)

        await bot.send_message(
            user_id,
            "🔥 Сегодня высокий спрос на курьеров\n\n"
            "Можно хорошо заработать",
            reply_markup=reg_kb()
        )

        await asyncio.sleep(86400)

        await bot.send_message(
            user_id,
            "🚀 Последний шанс подключиться\n\n"
            "Места заканчиваются",
            reply_markup=reg_kb()
        )

    except:
        pass

# =========================
# START
# =========================
@dp.message(CommandStart(deep_link=True))
async def start(message: Message, command: CommandStart):
    user_name = message.from_user.first_name
    source = command.args or "default"
    spots = random.randint(5, 15)

    if "seo" in source:
        intro = "Ты искал работу курьером — ты по адресу 👇\n\n"
    else:
        intro = ""

    text = (
        f"{intro}"
        f"👋 {user_name}, работа курьером Яндекс Еда\n\n"
        "💰 Доход до 3000₽ в день\n"
        "⚡ Старт за 15 минут\n\n"
        f"⚠️ Осталось {spots} мест\n\n"
        "👇 Начни сейчас"
    )

    await message.answer(text, reply_markup=start_kb())

# =========================
# FLOW
# =========================
@dp.callback_query(F.data == "start_flow")
async def start_flow(callback: CallbackQuery):
    await callback.message.answer(
        "🔒 Проверка доступа...\n\n"
        "📢 Подпишись на канал",
        reply_markup=sub_kb()
    )

# =========================
# CHECK
# =========================
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await check_subscription(user_id):

        await callback.message.answer("✅ Доступ подтверждён")

        asyncio.create_task(live_chat(user_id))
        asyncio.create_task(pre_sell(user_id))

        await asyncio.sleep(6)

        await callback.message.answer(
            "🔓 Доступ к системе открыт\n\n"
            "💬 Чат курьеров разблокируется после регистрации\n\n"
            "👇 Последний шаг:",
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
    print("💣 X10 система запущена")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
