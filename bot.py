import os
import re
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 🛡 Список ID администраторов (ваш ID и ID коллеги)
ADMIN_IDS = [
    9257646763,  # Ваш основной ID
    8989859413,  # ID коллеги
]

user_balances = {}
is_global_cheat = False  # Глобальный чит-режим для всех чатов

@dp.message(Command("cheat_on"))
async def enable_cheat(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    global is_global_cheat
    is_global_cheat = True
    try:
        await message.delete()
    except:
        pass
    await message.answer("🟢 Читерский режим (умножение на 0.1) ВКЛЮЧЕН!")

@dp.message(Command("cheat_off"))
async def disable_cheat(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    global is_global_cheat
    is_global_cheat = False
    try:
        await message.delete()
    except:
        pass
    await message.answer("🔴 Читерский режим ВЫКЛЮЧЕН.")

# Команда обнуления баланса (с поддержкой суффиксов в группах)
@dp.message(F.text.regexp(r'^/обнулить'))
async def reset_balance(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    chat_id = message.chat.id
    user_balances[chat_id] = 0.0
    await message.answer("🔄 Баланс этого чата успешно обнулен до 0.00")

# Команда вычитания суммы (например, /минус 10000)
@dp.message(F.text.regexp(r'^/минус'))
async def minus_balance(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = message.text or ""
    match = re.search(r'/минус(?:@\w+)?\s+(\d+)', text, re.IGNORECASE)
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
    match = re.search(r'(\d+)\s+(\d{1,2}:\d{2})', text)
    
    if match:
        visual_amount = float(match.group(1)) 
        time_str = match.group(2)
        chat_id = message.chat.id
        
        # Считаем реальную сумму с учетом чита
        real_amount = visual_amount * 0.1 if is_global_cheat else visual_amount
            
        # Аккумулируем баланс: берем старый и прибавляем новое значение
        old_balance = user_balances.get(chat_id, 0.0)
        current_balance = old_balance + real_amount
        user_balances[chat_id] = current_balance
        
        await message.answer(
            f"💰 Зачислено: {visual_amount:,.2f} (в {time_str}) | Общий баланс: {current_balance:,.2f}"
        )

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
    
    # 🛡 Защита от конфликтов сессий при старте
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
