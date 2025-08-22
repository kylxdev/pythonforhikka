# meta developer: @forever_hyoneya
# meta banner: https://example.com/banner.png

from .. import loader, utils
from telethon.tl.types import MessageActionChatAddUser, MessageActionChatJoinedByLink
import random

@loader.tds
class HyoneyaRulesMod(loader.Module):
    """Автоматическая отправка правил новым участникам группы"""
    strings = {
        "name": "HyoneyaRules",
        "default_rules": "👋 Добро пожаловать, {mention}!\n\n📜 Правила группы:\n1. Будь вежлив.\n2. Не спамь.\n3. Уважай других участников.\n\nХорошего общения!",
        "rules_updated": "✅ Правила обновлены.",
        "preview": "📜 Превью правил:\n\n{}",
        "enabled": "✅ Автоотправка правил включена.",
        "disabled": "❌ Автоотправка правил отключена.",
        "status": "🔧 Статус автоотправки правил: {}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "rules_text",
                self.strings["default_rules"],
                lambda: "Текст правил, который будет отправляться новым участникам. Используй {mention} для упоминания.",
            ),
            loader.ConfigValue(
                "enabled",
                True,
                lambda: "Включить или отключить автоотправку правил.",
            ),
            loader.ConfigValue(
                "send_as_reply",
                False,
                lambda: "Отправлять правила как ответ на сообщение о вступлении.",
            ),
            loader.ConfigValue(
                "delete_join_message",
                False,
                lambda: "Удалять системное сообщение о вступлении.",
            ),
            loader.ConfigValue(
                "silent_mode",
                False,
                lambda: "Не упоминать пользователя напрямую (без @).",
            ),
        )

        # Премиум эмодзи из пака NewsEmoji
        self.premium_emoji_ids = [
            "5370750590481690432",  # 🗞️
            "5370750590481690433",  # 📢
            "5370750590481690434",  # 📰
            "5370750590481690435",  # 🧠
            "5370750590481690436",  # 🔔
            "5370750590481690437",  # 📡
        ]

    async def watcher(self, message):
        if not self.config["enabled"]:
            return

        if getattr(message, "action", None):
            if isinstance(message.action, (MessageActionChatAddUser, MessageActionChatJoinedByLink)):
                for user in message.action.users:
                    mention = (
                        utils.escape_html(user.first_name)
                        if self.config["silent_mode"]
                        else f"<a href='tg://user?id={user.id}'>{utils.escape_html(user.first_name)}</a>"
                    )

                    # Рандомный премиум эмодзи
                    emoji_id = random.choice(self.premium_emoji_ids)
                    premium_emoji = f"<emoji id='{emoji_id}'/>"

                    # Форматирование текста правил
                    formatted_rules = f"{premium_emoji}<b>{self.config['rules_text'].replace('{mention}', mention)}</b>"

                    if self.config["send_as_reply"]:
                        await message.reply(formatted_rules, parse_mode="html")
                    else:
                        await message.client.send_message(message.chat_id, formatted_rules, parse_mode="html")

                if self.config["delete_join_message"]:
                    await message.delete()

    async def setrulescmd(self, message):
        """Изменить текст правил: .setrules Новый текст с {mention}"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❗ Укажи текст правил.")
            return

        self.config["rules_text"] = args
        await utils.answer(message, self.strings["rules_updated"])

    async def showrulescmd(self, message):
        """Показать текущие правила"""
        await utils.answer(message, self.strings["preview"].format(self.config["rules_text"]))

    async def togglerulescmd(self, message):
        """Включить/выключить автоотправку правил"""
        self.config["enabled"] = not self.config["enabled"]
        status = self.strings["enabled"] if self.config["enabled"] else self.strings["disabled"]
        await utils.answer(message, status)

    async def rulesstatuscmd(self, message):
        """Показать статус автоотправки"""
        status = "✅ Включена" if self.config["enabled"] else "❌ Отключена"
        await utils.answer(message, self.strings["status"].format(status))
