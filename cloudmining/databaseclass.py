import asyncpg
from aiogram.types import Message
from mnemonic import Mnemonic

from bitcoinlib.wallets import Wallet, wallet_delete
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import HDKey
import mnemonic
import random, string

user = "bohdandemyanchuk"
password = "AeT8hs9lOLSq"
database = "neondb"
host = "ep-weathered-resonance-391969.eu-central-1.aws.neon.tech"

token = '7012652197:AAH5qrCcGPU_SxhxgE6PqVgUqKXBzywifsQ'

class UserDb:
    def __init__(self, message: Message):
        self.message = message

    async def add_user(self):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute(
                'INSERT INTO users ("id", "name", "surname", "lang", "date") VALUES ($1, $2, $3, $4, $5)',
                self.message.chat.id, self.message.from_user.first_name, self.message.from_user.last_name, self.message.from_user.language_code, self.message.date.strftime('%Y-%m-%d %H:%M:%S')
            )
            return True
        except asyncpg.exceptions.UniqueViolationError:
            await con.execute(
                'UPDATE users SET "lang" = $1, "name" = $2, "surname" = $3 WHERE "id" = $4',
                self.message.from_user.language_code, self.message.from_user.first_name,
                self.message.from_user.last_name, self.message.chat.id
            )
            return False
        except Exception as e:
            pass
        finally:
            await con.close()

    @staticmethod
    async def increase(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute(
                'UPDATE users SET refs = refs + 1 WHERE id = $1',
                _id
            )
        finally:
            await con.close()

    @staticmethod
    async def add_wallet(_id: int, addr: str):
        # passphrase = mnemonic.Mnemonic("english").generate(128)
        # print(passphrase)
        # con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        # hdkey = HDKey().from_passphrase(passphrase, encoding="bech32")
        # addr = hdkey.subkey_for_path("m/84'/0'/0'/0/0").address()
        # try:
        #     await con.execute('update users set private_key = $1, public_key = $2  where id = $3', passphrase,
        #                       addr, _id)
        # finally:
        #     await con.close()
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('update users set public_key = $1  where id = $2', addr, _id)
        finally:
            await con.close()

    @staticmethod
    async def get_balance(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select balance from users where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def get_refs(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select refs from users where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def get_creation_time(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select date from users where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def get_public_key(_id: int):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            return await con.fetchval('select public_key from users where id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def statistic():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            count_result = await con.fetchval('SELECT count(id) FROM users')

            per_result = await con.fetch(
                'SELECT lang, COUNT(*) as count FROM users GROUP BY lang'
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
            result = await con.fetch("SELECT id FROM users")
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
                'UPDATE ref SET amount = amount + 1 WHERE name = $1',
                name
            )
        finally:
            await con.close()

    @staticmethod
    async def add_ref(refname: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('INSERT INTO ref (name) VALUES ($1)', refname)
        finally:
            await con.close()

    @staticmethod
    async def reset_ref(refname: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute(
                'UPDATE ref SET amount = 0 WHERE name = $1', refname
            )
        finally:
            await con.close()

    @staticmethod
    async def get_refs():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            names = await con.fetch("SELECT name FROM ref")
            result = [name["name"] for name in names]
            return result
        finally:
            await con.close()

    @staticmethod
    async def get_ref(name: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            result = await con.fetch('SELECT name, amount FROM ref WHERE name = $1', name)
            return result
        finally:
            await con.close()

    @staticmethod
    async def delete_ref(name: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('DELETE FROM ref WHERE name = $1', name)
        finally:
            await con.close()






class ChannelDb:
    cached_data = None
    @staticmethod
    async def cash_link_id():
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            result = await con.fetch('SELECT link, id FROM op')
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
            result = await con.fetch('SELECT link, id FROM op')
            return result
        finally:
            await con.close()

    @staticmethod
    async def delete_channel(_id):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('DELETE FROM op WHERE id = $1', _id)
        finally:
            await con.close()

    @staticmethod
    async def add_channel(_id: int, link: str):
        con = await asyncpg.connect(user=user, password=password, database=database, host=host)
        try:
            await con.execute('INSERT INTO op (link, id) VALUES ($1, $2)', link, _id)
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




