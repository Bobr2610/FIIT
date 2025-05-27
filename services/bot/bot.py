import asyncio
import os
import signal
import sys
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


API_URL = os.getenv('SITE_API_URL')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
is_running = True

def signal_handler(sig, frame):
    global is_running
    print(f"Получен сигнал {sig}, завершаем работу...")
    is_running = False

async def verify_link(code: str, chat_id: int) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/auth/telegram/verify/",
                json={'code': code, 'chat_id': chat_id}
            ) as response:
                return response.status == 200
    except Exception as exception:
        return False

@dp.message(Command("start"))
async def cmd_start(message: Message):
    args = message.text.split()

    if len(args) != 2:
        await message.answer(
            "Привет! Я бот для уведомлений о курсах валют.\n"
            "Для привязки аккаунта перейдите на сайт и следуйте инструкциям."
        )

        return

    code = args[1]
    chat_id = message.chat.id

    if await verify_link(code, chat_id):
        await message.answer(
            "Аккаунт успешно привязан!\n"
            "Теперь вы будете получать уведомления о курсах валют."
        )
    else:
        await message.answer(
            "Неверный или устаревший код.\n"
            "Пожалуйста, получите новую ссылку на сайте."
        )

async def main():
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Запускаем бота с отключенной встроенной обработкой сигналов
        await dp.start_polling(bot, handle_signals=False)
        
        # Ждем, пока не получим сигнал завершения
        while is_running:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрываем сессию бота
        await bot.session.close()
        print("Бот успешно остановлен")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Получен сигнал прерывания, завершаем работу...")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)
