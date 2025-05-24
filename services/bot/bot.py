import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
dp = Dispatcher()

# Используем внутреннее имя сервиса app
API_URL = "http://app:8000/api/v1"

async def verify_link(code: str, chat_id: int) -> bool:
    """Проверка и верификация ссылки через API"""
    try:
        print('verifying link')
        # Создаем отдельную сессию для API-запросов
        async with aiohttp.ClientSession() as session:
            # Привязываем chat_id через API
            async with session.post(
                f"{API_URL}/auth/telegram/verify/",
                json={'code': code, 'chat_id': chat_id}
            ) as response:
                if response.status == 200:
                    print('link verified successfully')
                    return True
                else:
                    print(f'verification failed with status {response.status}')
                    return False
    except Exception as e:
        print(f'Error during verification: {str(e)}')
        return False

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    args = message.text.split()

    if len(args) != 2:
        await message.answer(
            "Привет! Я бот для уведомлений о курсах валют.\n"
            "Для привязки аккаунта перейдите на сайт и следуйте инструкциям."
        )

        return

    code = args[1]
    chat_id = message.chat.id

    print(f'Received code: {code}, chat_id: {chat_id}')

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
    """Запуск бота"""
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 