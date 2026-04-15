import asyncio
import os
import json


from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
REG_URL = os.getenv("REG_URL")

if not TOKEN or not CHANNEL_ID or not REG_URL:
    raise ValueError("❌ Проверь .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()

CHANNEL_LINK = f"https://t.me/{CHANNEL_ID.replace('@','')}"

# =========================
# DATA
# =========================
with open("cities.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

EARNINGS = {i["city"].lower(): i for i in raw}

with open("faq.json", "r", encoding="utf-8") as f:
    FAQ = json.load(f)

# =========================
# STATE
# =========================
USER_STAGE = {}
USER_STATE = {}
SUBSCRIBED = set()

# =========================
# KEYBOARDS
# =========================
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Доход", callback_data="earnings")
    kb.button(text="🚀 Начать", callback_data="start_work")
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
    kb.button(text="🚴 Начать зарабатывать", url=REG_URL)
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def back_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 В меню", callback_data="menu")
    return kb.as_markup()


def faq_kb():
    kb = InlineKeyboardBuilder()
    for i, item in enumerate(FAQ["faq"]):
        kb.button(text=item["q"], callback_data=f"faq_{i}")
    kb.button(text="🏠 В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ("left", "kicked")
    except:
        return False


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    USER_STAGE[message.from_user.id] = "cold"

    await message.answer(
        "🚴 Работа курьером\n\n"
        "📢 Подпишись на канал:",
        reply_markup=sub_kb()
    )


# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================
@dp.callback_query(F.data == "check_sub")
async def check_sub_handler(callback: CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id

    if await check_sub(user_id):
        SUBSCRIBED.add(user_id)

        await callback.message.answer(
            "✅ Подписка подтверждена",
            reply_markup=main_menu()
        )
    else:
        await callback.message.answer(
            "❌ Ты не подписан",
            reply_markup=sub_kb()
        )


# =========================
# МЕНЮ
# =========================
@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🏠 Главное меню", reply_markup=main_menu())


# =========================
# FAQ
# =========================
@dp.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("❓ Выбери вопрос:", reply_markup=faq_kb())


@dp.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: CallbackQuery):
    await callback.answer()

    index = int(callback.data.split("_")[1])
    item = FAQ["faq"][index]

    await callback.message.answer(
        f"{item['q']}\n\n{item['a']}",
        reply_markup=faq_kb()
    )


# =========================
# ДОХОД
# =========================
@dp.callback_query(F.data == "earnings")
async def earnings(callback: CallbackQuery):
    await callback.answer()

    USER_STAGE[callback.from_user.id] = "warm"
    USER_STATE[callback.from_user.id] = "city"

    await callback.message.answer("📍 Напиши город", reply_markup=back_menu())

#
async def show_earnings(message: Message, data: dict):
    foot = data['foot']
    bike = data['bike']
    auto = data['auto']

    text = (
        f"📍 <b>{data['city']}</b>\n\n"

        f"💰 <b>Заработок курьеров:</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🚶 Пеший — <b>{foot}₽/час</b>\n"
        f"🚴 Вело — <b>{bike}₽/час</b>\n"
        f"🚗 Авто — <b>{auto}₽/час</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"

        f"📊 <b>Пример дохода:</b>\n"
        f"• Пеший: <b>{foot * 8:,}₽/день</b>\n"
        f"• Вело: <b>{bike * 8:,}₽/день</b>\n"
        f"• Авто: <b>{auto * 8:,}₽/день</b>\n\n"

        f"💸 <b>В месяц:</b>\n"
        f"• до <b>{auto * 8 * 25:,}₽</b>\n\n"

        f"🔥 <b>Сейчас высокий спрос</b>\n"
        f"⚡ Подключение занимает 10–15 минут\n\n"

        f"👇 <b>Начни зарабатывать уже сегодня</b>"
    )

    await message.answer(text, reply_markup=reg_kb(), parse_mode="HTML")
# =========================
# ГОРОД
# =========================
@dp.message()
async def city_handler(message: Message):
    user_id = message.from_user.id

    if USER_STATE.get(user_id) != "city":
        # умный FAQ fallback
        text = message.text.lower()

        for item in FAQ["faq"]:
            if any(k in text for k in item.get("keys", [])):
                await message.answer(item["a"], reply_markup=reg_kb())
                return

        return

    city = message.text.lower()
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
    USER_STATE[user_id] = None

    text = (
        f"📍 {data['city']}\n\n"
        f"🚶 {data['foot']}₽\n"
        f"🚴 {data['bike']}₽\n"
        f"🚗 {data['auto']}₽\n\n"
        "🔥 Высокий спрос сейчас\n\n"
        "👇 Начни зарабатывать"
    )

    await message.answer(text, reply_markup=reg_kb())


# =========================
# START WORK
# =========================
@dp.callback_query(F.data == "start_work")
async def start_work(callback: CallbackQuery):
    await callback.answer()

    USER_STAGE[callback.from_user.id] = "hot"

    await callback.message.answer(
        "🚀 Быстрый старт\n\n"
        "👇 Подключение:",
        reply_markup=reg_kb()
    )


# =========================
# RUN
# =========================
async def main():
    print("🔥 FULL PRO BOT")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
