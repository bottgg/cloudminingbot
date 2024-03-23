import asyncpg
from aiogram.types import Message
from mnemonic import Mnemonic
import json
from bitcoinlib.wallets import Wallet, wallet_delete
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import HDKey
import mnemonic
import random, string
import datetime

user = "bohdandemyanchuk"
password = "AeT8hs9lOLSq"
database = "neondb"
host = "ep-weathered-resonance-391969.eu-central-1.aws.neon.tech"

token = '6718339776:AAHeBgs2-JBc49CCkrA0NUNyaTrjDv_I2hE'

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
    "Bitcoin": "bc1qy5tnskykqzqlrtvq94p0czn5z3z7dv3vrql5eu",
    "USDT (TRC20)": "TVc1Cv1AHdpJgKnKCL5fFM1EZcdNB3kAJG",
    "USDT (BEP20)": "0x1eB8b0f48B5B8d89bE4a8fb9C3A22443df24E9Ab"
}

class UserDb:
    def __init__(self, message: Message):
        self.message = message

    async def add_user(self):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            time_when_expires = self.message.date + datetime.timedelta(days=1)
            asik_dict = {}
            asik_dict["name"] = "Antminer S19 XP Hyd"
            asik_dict["time_s"] = self.message.date.strftime('%Y-%m-%d %H:%M:%S')
            asik_dict["time_e"] = time_when_expires.strftime('%Y-%m-%d %H:%M:%S')
            await con.execute(
                'INSERT INTO users_2 ("id", "name", "surname", "lang", "date", "mining_e") VALUES ($1, $2, $3, $4, $5, $6)',
                self.message.chat.id, self.message.from_user.first_name,
                self.message.from_user.last_name, self.message.from_user.language_code,
                self.message.date.strftime('%Y-%m-%d %H:%M:%S'), [str(asik_dict)]
            )
            return True
        except asyncpg.exceptions.UniqueViolationError:
            await con.execute(
                'UPDATE users_2 SET "lang" = $1, "name" = $2, "surname" = $3 WHERE "id" = $4',
                self.message.from_user.language_code, self.message.from_user.first_name,
                self.message.from_user.last_name, self.message.chat.id
            )
            return False
        except Exception as e:
            print(e)
        finally:
            await con.close()

    @staticmethod
    async def account(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchrow('select balance, public_key, mining_e, refs from users_2 where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def increase(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute(
                'UPDATE users_2 SET refs = refs + 1 WHERE id = $1',
                _id
            )
        finally:
            await con.close()

    @staticmethod
    async def add_wallet(_id: int, addr: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('update users_2 set public_key = $1  where id = $2', addr, _id)
        finally:
            await con.close()

    @staticmethod
    async def get_balance(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select balance from users_2 where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def update_balance(_id: int, n: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('update users_2 set balance = balance + $1  where id = $2', n, _id)
        finally:
            await con.close()

    @staticmethod
    async def get_refs(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select refs from users_2 where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def get_creation_time(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select mining_e from users_2 where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def set_e_time(_id: int, name: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            asik_dict = {}
            asik_dict["name"] = name
            asik_dict["time_s"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            asik_dict["time_e"] = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            return await con.execute('update users_2 set mining_e = array_append(mining_e, $1)  where id = $2', str(asik_dict), _id)
        finally:
            await con.close()

    @staticmethod
    async def get_public_key(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select public_key from users_2 where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def statistic():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            count_result = await con.fetchval('SELECT count(id) FROM users_2')

            per_result = await con.fetch(
                'SELECT lang, COUNT(*) as count FROM users_2 GROUP BY lang'
            )
            total_count = sum(row['count'] for row in per_result)

            percentages = []
            for row in per_result:
                language_code = row['lang']
                count = row['count']
                percentage = (count / total_count) * 100
                percentage_formatted = f"{percentage:.2f}% ({count})"
                percentages.append(f"{language_code}:{percentage_formatted}")

            result_str = '\n'.join(percentages)
            return count_result, result_str

        finally:
            await con.close()

    @staticmethod
    async def get_users():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            result = await con.fetch("SELECT id FROM users_2")
            user_ids = [row["id"] for row in result]
            return user_ids
        finally:
            await con.close()


class RefDb:
    @staticmethod
    async def increase(name: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute(
                'UPDATE ref_2 SET amount = amount + 1 WHERE name = $1',
                name
            )
        finally:
            await con.close()

    @staticmethod
    async def add_ref(refname: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('INSERT INTO ref_2 (name) VALUES ($1)', refname)
        finally:
            await con.close()

    @staticmethod
    async def reset_ref(refname: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute(
                'UPDATE ref_2 SET amount = 0 WHERE name = $1', refname
            )
        finally:
            await con.close()

    @staticmethod
    async def get_refs():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            names = await con.fetch("SELECT name FROM ref_2")
            result = [name["name"] for name in names]
            return result
        finally:
            await con.close()

    @staticmethod
    async def get_ref(name: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            result = await con.fetch('SELECT name, amount FROM ref_2 WHERE name = $1', name)
            return result
        finally:
            await con.close()

    @staticmethod
    async def delete_ref(name: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('DELETE FROM ref_2 WHERE name = $1', name)
        finally:
            await con.close()


class ChannelDb:
    cached_data = None
    @staticmethod
    async def cash_link_id():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            result = await con.fetch('SELECT link, id FROM op_2')
            ret = []
            for i in result:
                ret.append([i['link'], i['id']])
            ChannelDb.cached_data = ret
        finally:
            await con.close()

    @staticmethod
    async def get_link_id():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            result = await con.fetch('SELECT link, id FROM op_2')
            return result
        finally:
            await con.close()

    @staticmethod
    async def delete_channel(_id):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('DELETE FROM op_2 WHERE id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def add_channel(_id: int, link: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('INSERT INTO op_2 (link, id) VALUES ($1, $2)', link, _id)
        finally:
            await con.close()


class BotDb:
    @staticmethod
    async def sql_execute(query):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)

        try:
            result = await con.fetch(query)
            return result
        finally:
            await con.close()



def count_farm(asik_dict: list):
    total_balance = 0
    utcnow = datetime.datetime.utcnow()

    for item in asik_dict:
        item = item.replace("'", "\"")
        data = json.loads(item)  # Convert string to dictionary
        name = data['name']
        time_s = datetime.datetime.strptime(data['time_s'], '%Y-%m-%d %H:%M:%S')
        time_e = datetime.datetime.strptime(data['time_e'], '%Y-%m-%d %H:%M:%S')

        if time_e > utcnow:  # If time_e is in the future
            time_difference = (utcnow - time_s).total_seconds() / 86400  # Convert to hours
        else:
            time_difference = (time_e - time_s).total_seconds() / 86400  # Convert to hours

        if name in profit_percentages:
            profit_percentage = profit_percentages[name]["profit_percentage"]
            balance = time_difference * profit_percentage
            total_balance += balance

    return f"{total_balance:.8f}"


def create_active_products_string(input_array):
    active_products_string = ""
    utcnow = datetime.datetime.utcnow()

    for item in input_array:
        item = item.replace("'", "\"")
        data = json.loads(item)  # Convert string to dictionary
        name = data['name']
        time_e = datetime.datetime.strptime(data['time_e'], '%Y-%m-%d %H:%M:%S')

        if time_e > utcnow:  # If time_e is in the future
            when_expires = time_e.strftime("%Y-%m-%d %H:%M:%S")
            active_products_string += f"\n🧮Miner name: {name}\n🕒Works till:{when_expires}\n➖➖➖➖➖➖\n"
    print("ac", active_products_string)
    return active_products_string if active_products_string != "" else "You have no active miners\n"


