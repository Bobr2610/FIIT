import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


API_URL = os.getenv('SITE_API_URL')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


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
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
