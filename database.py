from sqlalchemy import Column, Integer, BigInteger, String, Sequence
from sqlalchemy import sql
from gino import Gino
from gino.schema import GinoSchemaVisitor
from aiogram import types
from gino.dialects.asyncpg import NullPool
from settings import DB_NAME, DB_HOST, BOT_TOKEN, PROXY_URL
from aiogram import Bot


db = Gino()

bot = Bot(token=BOT_TOKEN,
          #proxy=PROXY_URL,
          parse_mode="HTML")


class User(db.Model):
    __tablename__ = 'Users'
    query: sql.Select
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    full_name = Column(String(100))
    username = Column(String(50))
    referral = Column(Integer)

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Items(db.Model):
    __tablename__ = "Items"
    query: sql.Select
    id = Column(Integer, primary_key=True)
    name = Column(String)
    photo_url = Column(String)
    description = Column(String)
    url = Column(String)
    video_url = Column(String)


class DBCommands:
    async def get_item(self, name):
        item = await Items.query.where(Items.name == name).gino.first()
        return item

    async def get_items(self):
        items = await Items.query.gino.all()
        return items

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name
        if referral:
            new_user.referral = int(referral)
            await bot.send_message(
                int(referral),
                'Новый пользователь был приглашен по вашей реферальной ссылке!')
        await new_user.create()
        return new_user

    async def count_referrals(self):
        user_id = types.User.get_current().id
        users = await User.query.where(User.referral == user_id).gino.all()
        count_referrals = len(users)
        return count_referrals

    async def check_referrals(self):
        bot = Bot.get_current()
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        referral = await User.query.where(User.referral == user.id).gino.all()
        return ", ".join([
            f"{num+1}. " + (await bot.get_chat(referral.user_id)).get_mention(as_html=True)
            for num, referral in enumerate(referral)
        ])


async def create_db():
    await db.set_bind(f'postgresql://{DB_HOST}/{DB_NAME}', pool_class=NullPool)
    db.gino: GinoSchemaVisitor
    #await db.gino.drop_all()
    await db.gino.create_all()