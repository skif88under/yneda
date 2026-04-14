import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder


TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
REG_URL = os.getenv("REG_URL")

if not TOKEN or not CHANNEL_ID or not REG_URL:
    raise ValueError("❌ Проверь .env файл")

CHANNEL_LINK = f"https://t.me/{CHANNEL_ID.replace('@', '')}"

# =========================
# INIT
# =========================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# MEMORY (для дожима)
# =========================
REGISTERED_USERS = set()

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
    kb.button(text="🚀 Начать работу", url=REG_URL)
    return kb.as_markup()


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
async def check_subscription(user_id: int) -> bool:
    for _ in range(2):
        try:
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status not in ("left", "kicked"):
                return True
        except Exception as e:
            print("Ошибка проверки:", e)
        await asyncio.sleep(2)
    return False


# =========================
# ДОЖИМ
# =========================
async def reminder(user_id: int):
    try:
        await asyncio.sleep(600)

        if user_id in REGISTERED_USERS:
            return

        await bot.send_message(
            user_id,
            "⏳ Ты не завершил регистрацию\n\n"
            "💰 Можно начать уже сегодня",
            reply_markup=reg_kb()
        )

        await asyncio.sleep(3600)

        if user_id in REGISTERED_USERS:
            return

        await bot.send_message(
            user_id,
            "🔥 Сейчас высокий спрос на курьеров\n\n"
            "👇 Успей подключиться",
            reply_markup=reg_kb()
        )

    except Exception as e:
        print("Ошибка дожима:", e)


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    text = (
        "🚴‍♂️ Работа курьером Яндекс Еда\n\n"
        "💰 Доход до 3000₽ в день\n"
        "⚡ Старт за 15 минут\n\n"
        "👇 Выбери действие:"
    )

    await message.answer(text, reply_markup=main_menu())


# =========================
# ВЕТКИ
# =========================
@dp.callback_query(F.data == "new")
async def new_user(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "🚀 Начнём подключение\n\n"
        "📢 Подпишись на канал:",
        reply_markup=sub_kb()
    )


@dp.callback_query(F.data == "old")
async def old_user(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "💬 Доступ к чату курьеров\n\n"
        "📢 Подпишись, чтобы получить доступ:",
        reply_markup=sub_kb()
    )


@dp.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "❓ Частые вопросы\n\n"
        "💰 Доход: до 3000₽\n"
        "📍 Опыт не нужен\n"
        "📱 Нужен только телефон",
        reply_markup=main_menu()
    )


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
@dp.callback_query(F.data == "check_sub")
async def check_sub_handler(callback: CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id  # 🔥 фикс ошибки

    if await check_subscription(user_id):
        REGISTERED_USERS.add(user_id)

        await callback.message.answer(
            "✅ Подписка подтверждена!\n\n"
            "🚀 Остался последний шаг:",
            reply_markup=reg_kb()
        )

        asyncio.create_task(reminder(user_id))

    else:
        await callback.message.answer(
            "❌ Подписка не найдена\n\n"
            "Подпишись и нажми снова:",
            reply_markup=sub_kb()
        )


# =========================
# RUN
# =========================
async def main():
    print("🚀 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
