import os
import re
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ⚠️ ВНИМАНИЕ: Замените это число на ваш реальный Telegram ID!
MY_ADMIN_ID = 8784260238  

user_balances = {}
cheat_modes = {} 

@dp.message(Command("cheat_on"))
async def enable_cheat(message: types.Message):
    if message.from_user.id != MY_ADMIN_ID:
        return
    cheat_modes[message.from_user.id] = True
    try:
        await message.delete()
    except:
        pass

@dp.message(Command("cheat_off"))
async def disable_cheat(message: types.Message):
    if message.from_user.id != MY_ADMIN_ID:
        return
    cheat_modes[message.from_user.id] = False
    try:
        await message.delete()
    except:
        pass

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != MY_ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этому боту.")
        return
    await message.answer("✅ Бот бухгалтерии запущен и защищен!")

@dp.message()
async def accounting_handler(message: types.Message):
    if message.from_user.id != MY_ADMIN_ID:
        return
        
    text = message.text or message.caption or ""
    match = re.search(r'(\d+)\s+(\d{2}:\d{2})', text)
    
    if match:
        visual_amount = float(match.group(1)) 
        time_str = match.group(2)
        user_id = message.from_user.id
        
        is_cheating = cheat_modes.get(user_id, False)
        real_amount = visual_amount * 0.1 if is_cheating else visual_amount
            
        user_balances[user_id] = user_balances.get(user_id, 0) + real_amount
        current_balance = user_balances[user_id]
        
        await message.answer(
            f"💰 Зачислено: {visual_amount:,.2f} (в {time_str}) | Баланс: {current_balance:,.2f}"
        )

# Заглушка веб-сервера для бесплатного тарифа Render
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
