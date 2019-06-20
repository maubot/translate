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
from typing import Dict, Optional, Tuple, Type
from abc import ABC, abstractmethod
from importlib import import_module

from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from maubot.handlers.command import Argument


class AbstractTranslationProvider(ABC):
    @abstractmethod
    def __init__(self, prefs: Dict) -> None:
        pass

    @abstractmethod
    async def translate(self, text: str, to_lang: str, from_lang: str = "auto") -> str:
        pass

    @abstractmethod
    def is_supported_language(self, code: str) -> bool:
        pass


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("provider.id")
        helper.copy("provider.args")


class LanguageCodePair(Argument):
    def __init__(self, name: str, label: str = None, *, required: bool = False):
        super().__init__(name, label=label, required=required, pass_raw=True)

    def match(self, val: str, evt: MessageEvent = None, instance: 'TranslatorBot' = None
              ) -> Tuple[str, Optional[Tuple[str, str]]]:
        parts = val.split(" ", 2)
        is_supported = (instance.translator.is_supported_language
                        if instance.translator
                        else lambda code: True)
        if len(parts) == 0 or not is_supported(parts[0]):
            return val, None
        elif len(parts) == 1:
            return "", ("auto", parts[0])
        elif len(parts) == 2:
            if is_supported(parts[1]):
                return "", (parts[0], parts[1])
            return parts[1], ("auto", parts[0])
        elif is_supported(parts[1]):
            return parts[2], (parts[0], parts[1])
        return " ".join(parts[1:]), ("auto", parts[0])


class TranslatorBot(Plugin):
    translator: Optional[AbstractTranslationProvider]

    async def start(self) -> None:
        await super().start()
        self.translator = None
        self.on_external_config_update()

    def on_external_config_update(self) -> None:
        self.config.load_and_update()
        self.translator = None
        try:
            provider = self.config["provider.id"]
            mod = import_module(f".{provider}", "translate.provider")
            make = mod.make_translation_provider
        except (KeyError, AttributeError, ImportError):
            self.log.exception("Failed to import translation provider")
            return
        try:
            self.translator = make(self.config["provider.args"])
        except Exception:
            self.log.exception("Failed to initialize translation provider")

    @command.new("translate", aliases=["tr"])
    @LanguageCodePair("language", required=True)
    @command.argument("text", pass_raw=True, required=False)
    async def command_handler(self, evt: MessageEvent, language: Tuple[str, str],
                              text: str) -> None:
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
        await evt.reply(result)

    @classmethod
    def get_config_class(cls) -> Type['BaseProxyConfig']:
        return Config
