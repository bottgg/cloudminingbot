import asyncio
from aiogram import Router
from aiogram import Bot, Dispatcher
from admin import mainadm, mailing, count, sql, senddb, op, ref
from bot import mainbot
from aiogram.fsm.storage.memory import MemoryStorage
from databaseclass import ChannelDb, token



async def main():
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    await ChannelDb.cash_link_id()
    routers = [
        mainadm.router,
        mailing.router,
        count.router,
        sql.router,
        senddb.router,
        op.router,
        ref.router,
        mainbot.router
               ]
    for i in routers:
        dp.include_router(i)
    #await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())