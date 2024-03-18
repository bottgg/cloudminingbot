import sqlite3
from aiogram.types import *
from aiogram.utils.keyboard import *
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, Text, CommandObject
from aiogram import Bot
import sys
import datetime
sys.path.append('../..')
from databaseclass import UserDb, RefDb, token
from aiogram.utils.deep_linking import create_start_link
import aiohttp

bot = Bot(token=token, parse_mode="HTML")
router = Router()

address_btc = "Bitcoin"
address_usdt = "Usdt"

mining_algorithms = [
    "Antminer S19 XP",
    "Antminer T21",
    "Antminer S21",
    "Antminer S19 XP Hyd",
    "Antminer S21 Hyd"
]

profit_percentages = {
    "Antminer S19 XP": {"profit_percentage": 0.00026677, "price_usd": 0.000160062},
    "Antminer T21": {"profit_percentage": 0.00036204, "price_usd": 0.000217224},
    "Antminer S21": {"profit_percentage": 0.00038109, "price_usd": 0.000228654},
    "Antminer S19 XP Hyd": {"profit_percentage": 0.0004859, "price_usd": 0.00029154},
    "Antminer S21 Hyd": {"profit_percentage": 0.00063833, "price_usd": 0.000382998}
}

cryptocurrencies = [
    "Bitcoin",
    "USDT (TRC20)",
    "USDT (BEP20)",
]

cryptocurrency_dict = {
    "Bitcoin": "bc1qswjep2n3wlt0k86p2w9hx3duk8zjlsa5g77tsu",
    "USDT (TRC20)": "TVZCmfo5tSXmSpoi1U1GLhERy3WxQXoFoM",
    "USDT (BEP20)": "0xBCa0239ea574A51d54E581491d12BAe9ca5Ff565"
}

class Addr_set(StatesGroup):
    addr = State()

@router.callback_query(Text(text='generate_wallet'))
async def generate_wallet(call: CallbackQuery, state: FSMContext):
    await UserDb.add_wallet(call.message.chat.id)
    await bot.send_message(call.message.chat.id, "Your wallet has been created")

@router.callback_query(Text(text='cancel'))
async def cancel(call: CallbackQuery, state: FSMContext):
    await bot.send_message(call.message.chat.id, "Canceled")
    await state.clear()

@router.callback_query(Text(text='set_wallet'))
async def set_wallet(call: CallbackQuery, state: FSMContext):
    buttons = [
        [
            InlineKeyboardButton(text="❌Cancel", callback_data="cancel"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(call.message.chat.id, "Enter your Bitcoin address", reply_markup=keyboard)
    await state.set_state(Addr_set.addr)

@router.callback_query(Text(text="deposit"))
async def deposit(call: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="Bitcoin", callback_data="Bitcoin"),
        ],
        [
            InlineKeyboardButton(text="USDT (TRC20)", callback_data="USDT (TRC20)"),
            InlineKeyboardButton(text="USDT (BEP20)", callback_data="USDT (BEP20)"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.answer("Choose the payment method below", reply_markup=keyboard)

@router.callback_query(Text(text="withdraw"))
async def withdraw(call: CallbackQuery):
    kurs = []
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json') as response:
            kurs = await response.json()
    th = 0.00000006
    refs = await UserDb.get_refs(call.message.chat.id)
    hashrate = 50+(refs*5)
    data = await UserDb.get_creation_time(call.message.chat.id)
    date_string = data["date"]
    date_mining_e = data["mining_e"]
    datetime_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    mining_e_object = datetime.datetime.strptime(date_mining_e, "%Y-%m-%d %H:%M:%S")
    time_passed = datetime.datetime.utcnow() - datetime_object
    balance = format((th*hashrate)*(time_passed.total_seconds()/3600), ".8f")
    public_key = await UserDb.get_public_key(call.message.chat.id)
    buttons = [
        [
            InlineKeyboardButton(text="Withdraw", callback_data="set_wallet"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    refs = await UserDb.get_refs(call.message.chat.id)
    addr = ""
    if public_key == None:
        addr = "You have not connected your BTC address yet"
    else:
        addr = f"<code>{public_key}</code>"
    await call.message.answer(f"You are going to withdraw your money to your connected address:\n{addr}\nYour balance:\n{balance} ({round(float(balance)*float(kurs['bpi']['USD']['rate_float']), 2)}$)", parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(Text(text="buy_power"))
async def buy_power(call: CallbackQuery):
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    buttons = []
    for i in chunks(mining_algorithms, 2):
        btns = []
        for j in i:
            btns.append(InlineKeyboardButton(text=j, callback_data=j))
        buttons.append(btns)
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.answer("Choose mining algorithm below:", reply_markup=keyboard)

@router.callback_query(Text(text=mining_algorithms))
async def buy_power(call: CallbackQuery):
    kurs = []
    buttons = [
        [
            InlineKeyboardButton(text="🧾Rent", callback_data=f"rent:{call.data}"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json') as response:
            kurs = await response.json()
    kurs = kurs['bpi']['USD']['rate_float']
    await call.message.answer(f"""💳Order: <b>Bitcoin (BTC)</b>
🧮Machine: <b>{call.data}</b>
➖➖➖➖➖➖➖➖➖➖
    Profitability: {int(profit_percentages[call.data]['profit_percentage']/profit_percentages[call.data]['price_usd']*100)-100}%
    Price: {int(profit_percentages[call.data]['price_usd']*kurs)}$
    ⏳Time: 1 day
➖➖➖➖➖➖➖➖➖➖""", parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(lambda call: call.data[:4] == "rent")
async def buy_power(call: CallbackQuery):
    name = call.data.split(":")[1]
    balance = await UserDb.get_balance(call.message.chat.id)
    kurs = []
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json') as response:
            kurs = await response.json()
    kurs = kurs['bpi']['USD']['rate_float']
    price = int(profit_percentages[name]['price_usd']*kurs)
    if price > balance:
        await call.answer("You have no enough money to buy it. Make a deposit in \"Account\" tab", show_alert=True)
    else:
        await call.message.delete()
        await UserDb.update_balance(call.message.chat.id, -price)
        data = await UserDb.get_creation_time(call.message.chat.id)
        date_string = data["date"]
        date_mining_e = data["mining_e"]
        mining_e_object = datetime.datetime.strptime(date_mining_e, "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.utcnow() > mining_e_object:
            await UserDb.set_e_time(call.message.chat.id, datetime.datetime.utcnow() + datetime.timedelta(days=1))
        else:
            await UserDb.set_e_time(call.message.chat.id, mining_e_object + datetime.timedelta(days=1))
        await call.message.answer("You have successfully rented server")

@router.callback_query(Text(text=cryptocurrencies))
async def deposit_c(call: CallbackQuery):
    await call.message.answer(f"Your address to send:\n<code>{cryptocurrency_dict[call.data]}</code>", parse_mode="HTML")

