import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Dispatcher

from app.bot import bot
from app.handlers import start, other_handlers

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger('aiogram')
    logger.setLevel(logging.DEBUG) 
    
    dp = Dispatcher()
    dp.include_routers(start.router, other_handlers.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

