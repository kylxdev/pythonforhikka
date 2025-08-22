# meta developer: @forever_hyoneya
# meta name: PraccChek

from telethon.tl.types import MessageMediaPhoto
from datetime import datetime, timedelta, time as dtime
from .. import loader, utils
import asyncio

@loader.tds
class PraccChek(loader.Module):
    """💎 PraccChek — контроль активности с #prac и мотивацией"""
    strings = {"name": "PraccChek"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("notify_chat", None, "📨 Куда слать уведомления"),
            loader.ConfigValue("check_start", "00:00", "🕐 Начало окна проверки (МСК)"),
            loader.ConfigValue("check_end", "00:00", "🕛 Конец окна проверки (МСК)"),
            loader.ConfigValue("remind_before", 60, "⏰ За сколько минут до дедлайна напомнить"),
        )
        self.users_to_check = set()
        self.daily_log = {}
        self.weekly_stats = {}
        self.all_chats = set()

    async def client_ready(self, client, db):
        self.client = client
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel or dialog.is_user:
                self.all_chats.add(dialog.id)
        asyncio.create_task(self.daily_check_loop())
        asyncio.create_task(self.reminder_loop())

    async def pcaddcmd(self, message):
        """➕ Добавить пользователя: .pc add @username или reply"""
        args = utils.get_args(message)
        user = None
        try:
            if args:
                username = args[0].lstrip("@")
                user = await message.client.get_entity(username)
            elif message.is_reply:
                reply = await message.get_reply_message()
                user = await message.client.get_entity(reply.sender_id)
            if user:
                self.users_to_check.add(user.id)
                await message.edit(f"✅ Добавлен: @{user.username or user.first_name}")
            else:
                await message.edit("❌ Не удалось определить пользователя.")
        except Exception as e:
            await message.edit(f"⚠️ Ошибка: {e}")

    async def pcdelcmd(self, message):
        """➖ Удалить пользователя: .pc del @username или reply"""
        args = utils.get_args(message)
        user = None
        try:
            if args:
                username = args[0].lstrip("@")
                user = await message.client.get_entity(username)
            elif message.is_reply:
                reply = await message.get_reply_message()
                user = await message.client.get_entity(reply.sender_id)
            if user:
                self.users_to_check.discard(user.id)
                await message.edit(f"🚫 Удалён: @{user.username or user.first_name}")
            else:
                await message.edit("❌ Не удалось определить пользователя.")
        except Exception as e:
            await message.edit(f"⚠️ Ошибка: {e}")

    async def pclistcmd(self, message):
        """📋 Список проверяемых: .pc list"""
        if not self.users_to_check:
            await message.edit("📭 Список пуст.")
            return
        result = "👥 Проверяемые:\n"
        for uid in self.users_to_check:
            try:
                user = await self.client.get_entity(uid)
                name = f"@{user.username}" if user.username else user.first_name
                result += f"• {name}\n"
            except Exception:
                continue
        await message.edit(result)

    async def pcstatcmd(self, message):
        """📊 Статистика за 7 дней: .pc stat"""
        result = "📈 Статистика активности:\n"
        for uid in self.users_to_check:
            try:
                user = await self.client.get_entity(uid)
                name = f"@{user.username}" if user.username else user.first_name
                count = sum(1 for day in self.weekly_stats.get(uid, []) if day)
                result += f"• {name}: {count}/7 дней ✅\n"
            except Exception:
                continue
        await message.edit(result)

    async def watcher(self, message):
        """👁 Отслеживает #prac с фото во всех чатах"""
        if message.chat_id not in self.all_chats:
            return
        if not isinstance(message.media, MessageMediaPhoto):
            return
        if "#prac" not in message.raw_text.lower():
            return
        if message.sender_id in self.users_to_check:
            now = datetime.now()
            start = datetime.combine(now.date(), self._parse_time(self.config["check_start"]))
            end = datetime.combine(now.date(), self._parse_time(self.config["check_end"]))
            if end <= start:
                end += timedelta(days=1)
            if start <= now <= end:
                self.daily_log.setdefault(now.date(), set()).add(message.sender_id)
                self.weekly_stats.setdefault(message.sender_id, []).append(True)
                if len(self.weekly_stats[message.sender_id]) > 7:
                    self.weekly_stats[message.sender_id].pop(0)

                if self.config["notify_chat"]:
                    try:
                        user = await self.client.get_entity(message.sender_id)
                        await self.client.send_message(
                            self.config["notify_chat"],
                            f"🌟 @{user.username or user.first_name} запостил #prac! Так держать 💪"
                        )
                    except Exception:
                        pass

    async def daily_check_loop(self):
        while True:
            now = datetime.now()
            end_time = self._parse_time(self.config["check_end"])
            next_check = datetime.combine(now.date(), end_time)
            if now > next_check:
                next_check += timedelta(days=1)
            wait_seconds = (next_check - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            today = now.date()
            missed = [uid for uid in self.users_to_check if uid not in self.daily_log.get(today, set())]
            for uid in missed:
                self.weekly_stats.setdefault(uid, []).append(False)
                if len(self.weekly_stats[uid]) > 7:
                    self.weekly_stats[uid].pop(0)

            if missed and self.config["notify_chat"]:
                for uid in missed:
                    try:
                        user = await self.client.get_entity(uid)
                        await self.client.send_message(
                            self.config["notify_chat"],
                            f"😔 @{user.username or user.first_name}, ты если еще раз пропустишь #prac я тя кикну к хуям 🚀"
                        )
                    except Exception:
                        continue

            self.daily_log[today] = set()

    async def reminder_loop(self):
        while True:
            now = datetime.now()
            end_time = self._parse_time(self.config["check_end"])
            remind_delta = timedelta(minutes=self.config["remind_before"])
            remind_time = datetime.combine(now.date(), end_time) - remind_delta
            if now > remind_time:
                remind_time += timedelta(days=1)
            wait_seconds = (remind_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            if self.config["notify_chat"]:
                await self.client.send_message(
                    self.config["notify_chat"],
                    f"⏳ Напоминание: осталось меньше {self.config['remind_before']} минут до дедлайна #prac!"
                )

    def _parse_time(self, time_str):
        try:
            h, m = map(int, time_str.strip().split(":"))
            return dtime(hour=h, minute=m)
        except Exception:
            return dtime(0, 0)
