import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

from config import Settings
from handlers import commands, callbacks, inline


async def main():
    logging.basicConfig(
        filename="../debug.log",
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(callbacks.router)
    dp.include_router(commands.router)
    dp.include_router(inline.router)

    config = Settings()
    bot = Bot(config.bot_token)

    await commands.set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
