import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from environs import Env
import logging


from handlers.for_users_handler import router


env = Env()
env.read_env()


logging.basicConfig(level=logging.INFO)


bot =  Bot(token=env('TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))


dp = Dispatcher()
dp.include_router(router=router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

