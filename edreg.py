import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- LOAD ENV ---
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
REG_URL = os.getenv("REG_URL")
CHANNEL_LINK = f"https://t.me/{CHANNEL_ID.replace('@', '')}"

if not TOKEN or not CHANNEL_ID:
    raise ValueError("Проверь .env файл")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# 🔘 КНОПКИ
# =========================
def check_sub_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться", url=CHANNEL_LINK)
    kb.button(text="✅ Я подписался", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()


def register_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Пройти регистрацию", url=REG_URL)
    return kb.as_markup()


# =========================
# 🧠 УМНАЯ ПРОВЕРКА ПОДПИСКИ
# =========================
async def check_subscription(user_id: int) -> bool:
    """
    Надёжная проверка подписки с повторной попыткой
    """
    for attempt in range(2):  # 2 попытки
        try:
            member = await bot.get_chat_member(CHANNEL_ID, user_id)

            print(f"[DEBUG] user={user_id}, status={member.status}")

            if member.status not in ("left", "kicked"):
                return True

        except Exception as e:
            print(f"[ERROR] Проверка подписки: {e}")

        await asyncio.sleep(2)  # задержка перед повтором

    return False


# =========================
# 🚀 START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    text = (
        "🚴‍♂️ Работа курьером Яндекс Еда\n\n"
        "📌 Чтобы начать:\n"
        "1. Подпишись на канал\n"
        "2. Пройди регистрацию\n"
        "3. Начни получать заказы\n\n"
        "👇 Нажми кнопку ниже"
    )

    await message.answer(text, reply_markup=check_sub_keyboard())


# =========================
# ✅ ПРОВЕРКА ПОДПИСКИ
# =========================
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    await callback.answer("Проверяю подписку...")

    is_sub = await check_subscription(user_id)

    if is_sub:
        await callback.message.answer(
            "✅ Подписка подтверждена!\n\n"
            "🚴 Теперь переходи к регистрации:",
            reply_markup=register_keyboard()
        )
    else:
        await callback.message.answer(
            "❌ Пока не вижу подписку\n\n"
            "📢 Подпишись на канал и нажми кнопку снова.\n\n"
            "⚠️ Иногда Telegram обновляет статус с задержкой (5-10 сек)",
            reply_markup=check_sub_keyboard()
        )


# =========================
# ▶️ ЗАПУСК
# =========================
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
