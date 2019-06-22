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
from typing import Optional, Tuple, NamedTuple, Set, Dict, TYPE_CHECKING
from importlib import import_module

from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from mautrix.types import RoomID
from maubot import MessageEvent
from maubot.handlers.command import Argument

from .provider import AbstractTranslationProvider

if TYPE_CHECKING:
    from .bot import TranslatorBot

AutoTranslateConfig = NamedTuple("AutoTranslateConfig", main_language=str,
                                 accepted_languages=Set[str])


class TranslationProviderError(Exception):
    pass


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("provider.id")
        helper.copy("provider.args")
        helper.copy("auto_translate")
        helper.copy("response_reply")

    def load_translator(self) -> AbstractTranslationProvider:
        try:
            provider = self["provider.id"]
            mod = import_module(f".{provider}", "translate.provider")
            make = mod.make_translation_provider
        except (KeyError, AttributeError, ImportError) as e:
            raise TranslationProviderError("Failed to load translation provider") from e
        try:
            return make(self["provider.args"])
        except Exception as e:
            raise TranslationProviderError("Failed to initialize translation provider") from e

    def load_auto_translate(self) -> Dict[RoomID, AutoTranslateConfig]:
        atc = {value.get("room_id"): AutoTranslateConfig(value.get("main_language", "en"),
                                                         set(value.get("accepted_languages", [])))
               for value in self["auto_translate"] if "room_id" in value}
        return atc


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
