import asyncio
from mailbox import Message

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from environs import Env
import logging

from aiogram.filters import Filter
from aiogram.types import Message
from handlers.for_users_handler import user_router
from handlers.for_admin_handlers import admin_router


env = Env()
env.read_env()

MANAGERS_IDS = {5129105635, 123456789, 987654321}

class IsUserFilter(Filter):
    def __init__(self, admin_ids: set):
        self.admin_ids = admin_ids
    
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id not in self.admin_ids

class IsAdminFilter(Filter):
    def __init__(self, admin_ids: set):
        self.admin_ids = admin_ids
    
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


logging.basicConfig(level=logging.INFO)


async def main():

    bot =  Bot(token=env('TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))


    dp = Dispatcher()
    dp.include_router(router=admin_router)  
    dp.include_router(router=user_router)
    

    admin_router.name = "admin_router"
    user_router.name = "user_router"
    
    admin_router.message.filter(IsAdminFilter(MANAGERS_IDS))
    admin_router.callback_query.filter(lambda cb: cb.from_user.id in MANAGERS_IDS)

    user_router.message.filter(IsUserFilter(MANAGERS_IDS))
    user_router.callback_query.filter(lambda cb: cb.from_user.id not in MANAGERS_IDS)
    

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

