# meta developer: @forever_hyoneya
# module name: EzPraccUltra

from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from .. import loader, utils
import os
from datetime import datetime
import json

@loader.tds
class EzPraccUltra(loader.Module):
    """💎 EzPracc Ultra — праки с аналитикой, кастомом и архивом"""
    strings = {"name": "EzPraccUltra"}

    def __init__(self):
        self.archive_path = "EzPraccArchive"
        self.log_file = "EzPracc.log"
        self.stats_file = "EzPraccStats.json"
        self.config_file = "EzPraccConfig.json"
        os.makedirs(self.archive_path, exist_ok=True)
        self._load_stats()
        self._load_config()

    def _load_stats(self):
        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r") as f:
                self.stats = json.load(f)
        else:
            self.stats = {"win": 0, "lose": 0}

    def _save_stats(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f)

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "win_caption": "🏆 Прак | Вин",
                "lose_caption": "😵‍💫 Прак | Луз",
                "autodelete": False,
                "cloud_chat": None
            }

    def _save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    async def pwcmd(self, message):
        """💎 .pw — сохранить как победу"""
        self.stats["win"] += 1
        self._save_stats()
        await self._save_media(message, self.config["win_caption"])

    async def plcmd(self, message):
        """💔 .pl — сохранить как поражение"""
        self.stats["lose"] += 1
        self._save_stats()
        await self._save_media(message, self.config["lose_caption"])

    async def praccstatscmd(self, message):
        """📊 .praccstats — статистика праков"""
        total = self.stats["win"] + self.stats["lose"]
        winrate = round((self.stats["win"] / total) * 100, 2) if total > 0 else 0
        await message.edit(
            f"📈 Статистика праков:\n\n"
            f"🏆 Побед: {self.stats['win']}\n"
            f"💀 Поражений: {self.stats['lose']}\n"
            f"⚖️ Всего: {total}\n"
            f"🔥 Winrate: {winrate}%"
        )

    async def setwincmd(self, message):
        """🖊 .setwin <текст> — задать подпись для побед"""
        self.config["win_caption"] = utils.get_args_raw(message)
        self._save_config()
        await message.edit("✅ Подпись для побед обновлена!")

    async def setlosecmd(self, message):
        """🖊 .setlose <текст> — задать подпись для поражений"""
        self.config["lose_caption"] = utils.get_args_raw(message)
        self._save_config()
        await message.edit("✅ Подпись для поражений обновлена!")

    async def _save_media(self, message, caption):
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await message.edit("⚠️ Ответь на сообщение с фото или видео!")
            return

        media_type = None
        if isinstance(reply.media, MessageMediaPhoto):
            media_type = "photo"
        elif isinstance(reply.media, MessageMediaDocument):
            media_type = "video" if reply.file.mime_type.startswith("video") else None

        if not media_type:
            await message.edit("❌ Медиа не поддерживается.")
            return

        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        full_caption = f"{caption}\n🕒 {timestamp}"

        file_ext = "jpg" if media_type == "photo" else "mp4"
        file_path = await self._client.download_media(reply.media, file=os.path.join(self.archive_path, f"{timestamp.replace(':', '-')}.{file_ext}"))

        await message.client.send_file(
            entity=message.chat_id,
            file=file_path,
            caption=full_caption
        )

        if self.config["cloud_chat"]:
            await message.client.send_file(
                entity=self.config["cloud_chat"],
                file=file_path,
                caption=full_caption
            )

        with open(self.log_file, "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] Saved {media_type}: {file_path} | Caption: {caption}\n")

        if self.config["autodelete"]:
            await reply.delete()

        await message.edit("✅ Медиа сохранено и отправлено!")

