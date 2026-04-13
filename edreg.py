import asyncio
import os

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
# КНОПКИ
# =========================
def sub_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться на канал", url=CHANNEL_LINK)
    kb.button(text="✅ Я подписался", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()


def reg_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Начать зарабатывать", url=REG_URL)
    return kb.as_markup()


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
async def check_subscription(user_id: int):
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
# START (ПРОДАЮЩИЙ)
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    text = (
        "🚴‍♂️ Работа курьером Яндекс Еда\n\n"
        "💰 Доход до 3000₽ в день\n"
        "📍 Свободный график\n"
        "⚡ Старт за 15 минут\n\n"
        "👥 Уже работают 12 000+ курьеров\n\n"
        "🔒 Доступ к заказам и инструкциям — только после подписки\n\n"
        "👇 Подпишись, чтобы продолжить"
    )

    await message.answer(text, reply_markup=sub_keyboard())


# =========================
# ПРОВЕРКА
# =========================
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    await callback.answer("Проверяю...")

    if await check_subscription(user_id):

        # основной оффер
        await callback.message.answer(
            "✅ Отлично!\n\n"
            "🔥 Теперь ты получишь доступ к работе\n\n"
            "👇 Пройди регистрацию:",
            reply_markup=reg_keyboard()
        )

        # 🔥 ДОЖИМ через 10 минут
        asyncio.create_task(reminder(callback.from_user.id))

    else:
        await callback.message.answer(
            "❌ Не вижу подписку\n\n"
            "⚠️ Подпишись и попробуй снова",
            reply_markup=sub_keyboard()
        )


# =========================
# ДОЖИМ (КОНВЕРСИЯ x2)
# =========================
async def reminder(user_id: int):
    await asyncio.sleep(600)  # 10 минут

    try:
        await bot.send_message(
            user_id,
            "⏳ Ты не завершил регистрацию\n\n"
            "💰 Курьеры уже зарабатывают сегодня\n"
            "Не упусти возможность\n\n"
            "👇 Заверши регистрацию:",
            reply_markup=reg_keyboard()
        )
    except:
        pass


# =========================
# ЗАПУСК
# =========================
async def main():
    print("Бот работает 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
