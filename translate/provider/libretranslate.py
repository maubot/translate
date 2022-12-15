# translate - A maubot plugin to translate words.
# Copyright (C) 2022 Tammes Burghard
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
import json
import re
from typing import Dict

from aiohttp import ClientSession, client_exceptions
from yarl import URL

from . import AbstractTranslationProvider, Result


class LibreTranslate(AbstractTranslationProvider):
    headers: Dict[str, str] = {"Content-Type": "application/json"}

    def __init__(self, args: Dict) -> None:
        super().__init__(args)
        if args.get("url") is None:
            raise ValueError("Please specify the url of your preferred libretranslate instance in provider.args.url")
        else:
            self._base_url = args.get("url")
            if not re.match(r"^https?://", self._base_url):
                self._base_url = "https://" + self._base_url
        self.url: URL = URL(self._base_url + "/translate")
        self.api_key = args.get("api_key")
        self.supported_languages = {"auto": "Detect language"}

    async def post_init(self):
        try:
            async with ClientSession() as sess:
                resp = await sess.get(self._base_url + "/languages")
                for lang in await resp.json():
                    self.supported_languages[lang["code"]] = lang["name"]
        except client_exceptions.ClientError:
            raise ValueError(f"This url ({self._base_url}) does not point to a compatible libretranslate instance. "
                             f"Please change it")

    async def translate(self, text: str, to_lang: str, from_lang: str = "auto") -> Result:
        if not from_lang:
            from_lang = "auto"
        async with ClientSession() as sess:
            data=json.dumps({"q": text, "source": from_lang, "target": to_lang,
                  "format": "text", "api_key": self.api_key})
            resp = await sess.post(self.url, data=data, headers=self.headers)
            if resp.status == 403:
                raise ValueError("Request forbidden. You did probably configure an incorrect api key.")
            data = await resp.json()
            return Result(text=data["translatedText"],
                          source_language=data["detectedLanguage"]["language"] if from_lang == "auto" else from_lang)

    def is_supported_language(self, code: str) -> bool:
        return code.lower() in self.supported_languages.keys()

    def get_language_name(self, code: str) -> str:
        return self.supported_languages[code]

    def get_supported_languages(self) -> dict:
        return self.supported_languages


make_translation_provider = LibreTranslate
