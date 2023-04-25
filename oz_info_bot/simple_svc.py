from aiogram.types import Message

from oz_info_bot.svc import AbcBotSvc, register, logger
from oz_info_bot.models import Result


class SimpleBotSvc(AbcBotSvc[Result]):
    async def handle_q(self, m: Result) -> None:
        async for id_ in self.storage:
            text = (
                f"Name: {m.name}\n"
                f"Free tickets: {m.free_tickets}\n"
                f"Free participants: {m.free_participants}\n"
                f"Nearest date: {m.nearest_date or ''}\n"
                f"Last date: {m.last_date or ''}\n"
            ).replace('.', r'\.')
            await self.bot.send_message(
                id_, text=text, parse_mode='MarkdownV2',
            )

    @register('start', 'info', 'hello')
    async def handle_start(self, msg: Message) -> None:
        # await bot.send_message(text='start', chat_id=message.chat.id)
        await msg.answer(
            f"Hello, <b>{msg.from_user.full_name}</b>",
            parse_mode='HTML',
        )
        await self.storage.put(msg.chat.id, None)  # TODO: how to clean?

    @register('ping')
    async def handle_ping(self, msg: Message) -> None:
        await msg.answer('PONG')

    @register('me')
    async def handle_me(self, msg: Message) -> None:
        u = msg.from_user
        await msg.answer((
                f"id: {u.id}\n"
                f"name: {u.full_name}\n"
                f"username: @{u.username}\n"
            ),
            parse_mode='MarkdownV2',
        )

    @register()
    async def handle_noop(self, msg: Message) -> None:
        id_, txt = msg.from_user.id, msg.text
        logger.info(f"recv id={id_} text={txt}")
        await msg.answer('ok')
