# translate - A maubot plugin to translate words.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Optional, Tuple, Type, Dict

from mautrix.util.config import BaseProxyConfig
from mautrix.types import RoomID, EventType, MessageType
from maubot import Plugin, MessageEvent
from maubot.handlers import command, event

from .provider import AbstractTranslationProvider
from .util import Config, LanguageCodePair, TranslationProviderError, AutoTranslateConfig

try:
    import langdetect
    from langdetect.lang_detect_exception import LangDetectException
except ImportError:
    langdetect = None
    LangDetectException = None


class TranslatorBot(Plugin):
    translator: Optional[AbstractTranslationProvider]
    auto_translate: Dict[RoomID, AutoTranslateConfig]
    config: Config

    async def start(self) -> None:
        await super().start()
        self.on_external_config_update()

    def on_external_config_update(self) -> None:
        self.translator = None
        self.config.load_and_update()
        self.auto_translate = self.config.load_auto_translate()
        try:
            self.translator = self.config.load_translator()
        except TranslationProviderError:
            self.log.exception("")

    @classmethod
    def get_config_class(cls) -> Type['BaseProxyConfig']:
        return Config

    @event.on(EventType.ROOM_MESSAGE)
    async def event_handler(self, evt: MessageEvent) -> None:
        if (langdetect is None or evt.content.msgtype == MessageType.NOTICE
                or evt.sender == self.client.mxid):
            return
        try:
            atc = self.auto_translate[evt.room_id]
        except KeyError:
            return

        def is_acceptable(lang: str) -> bool:
            return lang == atc.main_language or lang in atc.accepted_languages

        try:
            if is_acceptable(langdetect.detect(evt.content.body)):
                return
        except LangDetectException:
            return
        result = await self.translator.translate(evt.content.body, to_lang=atc.main_language)
        if is_acceptable(result.source_language) or result.text == evt.content.body:
            return
        await evt.respond(f"[{evt.sender}](https://matrix.to/#/{evt.sender}) said "
                          f"(in {self.translator.get_language_name(result.source_language)}): "
                          f"{result.text}")

    @command.new("translate", aliases=["tr"])
    @LanguageCodePair("language", required=False)
    @command.argument("text", pass_raw=True, required=False)
    async def command_handler(self, evt: MessageEvent, language: Optional[Tuple[str, str]],
                              text: str) -> None:
        if not language:
            await evt.reply("Usage: !translate [from] <to> [text or reply to message]")
            return
        if not self.config["response_reply"]:
            evt.disable_reply = True
        if not self.translator:
            self.log.warn("Translate command used, but translator not loaded")
            return
        if not text and evt.content.get_reply_to():
            reply_evt = await self.client.get_event(evt.room_id, evt.content.get_reply_to())
            text = reply_evt.content.body
        if not text:
            await evt.reply("Usage: !translate [from] <to> [text or reply to message]")
            return
        result = await self.translator.translate(text, to_lang=language[1], from_lang=language[0])
        await evt.reply(result.text)
