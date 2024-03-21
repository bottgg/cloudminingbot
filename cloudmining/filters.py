import aiogram.exceptions
from aiogram.types import *
from aiogram.filters import BaseFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot
import aiosqlite
from databaseclass import ChannelDb, token
from cachetools import TTLCache
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from typing import Any, Awaitable, Callable, Dict

adminlist = [6218950373, 5488988760, 1274251205]
allowedlist = ['creator', 'owner', 'admin', 'member']

bot = Bot(token=token)

class AdminFilter(BaseFilter):
    async def __call__(self, data):
        if(isinstance(data, Message)):
            if data.chat.id in adminlist:
                return True
        else:
            if data.message.chat.id in adminlist:
                return True
        return False

class SubFilter(BaseFilter):
    async def __call__(self, data):
        if(isinstance(data, Message)):
            pass
        else:
            r = ChannelDb.cached_data
            print("cached_data: ", r)
            issub = []
            if r:
                for i in r:
                    print(i[-1])
                    try:
                        issubbed = await bot.get_chat_member(i[-1], data.from_user.id)
                        if issubbed.status in allowedlist:
                            issub.append(True)
                        else:
                            issub.append(False)
                    except aiogram.exceptions.TelegramBadRequest as e:
                        print("aiogram.exceptions.TelegramBadRequest: " ,e)
                        continue
                    except Exception as e:
                        print(type(e).__name__, e)
                        continue
                print(issub)
                if False in issub:
                    builder = InlineKeyboardBuilder()
                    for j in r:
                        builder.button(text='Подписаться🍇', url=j[0])
                    builder.button(text='Проверить🔐', callback_data=data.data)
                    builder.adjust(1)
                    await bot.send_message(data.message.chat.id, text='Подпишись на наших спонсоров чтобы начать зарабатывать голду', reply_markup=builder.as_markup())
                    return False
                else:
                    return True
            else:
                return True

class ThrottlingMiddleware(BaseMiddleware):
    caches = {
        "spin": TTLCache(maxsize=10_000, ttl=0.7),
        "default": TTLCache(maxsize=10_000, ttl=0.7)
    }

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None and throttling_key in self.caches:
            if event.chat.id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][event.chat.id] = None
        return await handler(event, data)
