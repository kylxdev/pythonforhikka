from telethon import events
from .. import loader

@loader.tds
class HyCommandMod(loader.Module):
    """Модуль для команды .hy"""

    strings = {"name": "HyCommand"}

    @loader.command()
    async def hy(self, message):
        """Пишет 'тест' в чат"""
        await message.edit("тест")
