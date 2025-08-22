# meta developer: @forever_hyoneya
# meta name: WeLoveKseon

from .. import loader
import asyncio
import random

@loader.tds
class WeLoveKseonMod(loader.Module):
    """Бесконечная анимация любви к Kseon 💖 + Голосование и темы"""
    strings = {"name": "WeLoveKseon"}

    # Основной список участников
    roster = [
        "alucard [C]",
        "hyoneya [P]",
        "wodorleo [P]",
        "savayaka [P]"
    ]

    # Эмодзи для украшения
    emojis = [
        "💎", "👑", "🌊", "🍃", "✨", "🔥", "💫", "🌟", "🎯", "🧿",
        "🪄", "🦋", "🛸", "🧸", "🎆", "🌈", "🪷", "🧁", "🫧", "🪙",
        "🎀", "🪐", "🧬", "🫶", "🫰", "🧠", "🫀", "🪞", "🧥", "🧚",
        "🧜", "🧛", "🧙", "🧞", "🧟", "🪃", "🪁", "🪆", "🪅", "🪩",
        "🪬", "🫦", "🫸", "🫷", "🪮", "🪯", "🪰", "🪱", "🪲", "🪳",
        "🫎", "🫏", "🪶", "🪽", "🫚", "🫛", "🫙", "🫗", "🫖", "🫐"
    ]

    # Темы для .ksmtheme
    themes = {
        "classic": "✨🪽🪬🪩  Main Roster  🪩🪬🪽✨",
        "dark": "🌑🌘🌒 Dark Side 🌒🌘🌑",
        "light": "🌞🌼🌸 Light Vibes 🌸🌼🌞",
        "chaos": "🌀💥⚡ CHAOS MODE ⚡💥🌀"
    }

    async def ksmcmd(self, message):
        """Запускает бесконечную анимацию"""
        msg = await message.edit("🚀 Запуск анимации WeLoveKseon...")

        header = self.themes.get("classic")
        footer = "🧪 В бета тесте. Текст обновляется каждые 15 секунд.\n💡 Для идей: @forever_hyoneya"

        while True:
            for word in self.roster:
                left = random.choice(self.emojis)
                right = random.choice(self.emojis)
                animated_line = f"{left} {word} {right}"

                full_message = (
                    f"{header}\n\n\n"
                    f"🌟 {animated_line} 🌟\n\n\n"
                    f"{footer}"
                )

                try:
                    await msg.edit(full_message)
                    await asyncio.sleep(15)
                except Exception:
                    return

    async def ksmthemepreviewcmd(self, message):
        """Показать превью всех тем"""
        preview = "🎨 Превью тем:\n\n"
        for name, header in self.themes.items():
            preview += f"🔹 <b>{name}</b>: {header}\n"
        await message.edit(preview)

    async def ksmthemelistcmd(self, message):
        """Показать список доступных тем"""
        theme_list = "📁 Доступные темы:\n\n"
        for name in self.themes:
            theme_list += f"• {name}\n"
        await message.edit(theme_list)

    async def ksmvotecmd(self, message):
        """Запустить голосование за участника"""
        vote_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        text = "🗳️ Голосование: Кто твой фаворит?\n\n"
        for i, word in enumerate(self.roster):
            text += f"{vote_emojis[i]} — {word}\n"

        text += "\n||👆 Нажми на эмодзи, чтобы проголосовать!||"

        msg = await message.edit(text)

        try:
            for emoji in vote_emojis:
                await msg.client.send_reaction(message.chat_id, msg.id, emoji)
        except Exception:
            pass  # Если нет прав — просто игнорируем
