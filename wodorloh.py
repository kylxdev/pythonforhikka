from telethon import events
from random import choice
from .. import loader, utils

@loader.tds
class WodorlohMod(loader.Module):
    """Модуль подбрасывания монетки и проверки угадывания"""
    strings = {
        "name": "wodorloh",
        "win": "🎉 Хуя ты лакер ебучий, ну держи, ты выиграл резиновый член, потому что: {result}.",
        "lose": "😢 ХАХАХАХАХАХА ЛОХ ЕБАНЫЙ СОСИ ЧЛЕН, КАК В ТАКОЙ ХУЙНЕ МОЖНО БЫЛО НЕ УГАДАТЬ БЛЯЯЯ ТУПОЙ, ЧЕКАЙ ЧЕ ВЫПАЛО: {result}.",
        "no_reply": "⚠️ Ответь на сообщение, где написано 'орел' или 'решка'.",
        "invalid_choice": "❌ В сообщении нет 'орел' или 'решка'."
    }

    @loader.command()
    async def wup(self, message):
        """Подбросить монетку и проверить выбор пользователя"""
        reply = await message.get_reply_message()
        if not reply:
            await message.edit(self.strings("no_reply"))
            return

        user_choice = reply.text.lower()
        if "орел" in user_choice:
            choice_text = "орел"
        elif "решка" in user_choice:
            choice_text = "решка"
        else:
            await message.edit(self.strings("invalid_choice"))
            return

        coin = choice(["орел", "решка"])
        if coin == choice_text:
            await message.edit(self.strings("win").format(result=coin))
        else:
            await message.edit(self.strings("lose").format(result=coin))
