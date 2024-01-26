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
from typing import Dict, List, Pattern, Tuple, Any
import asyncio
import json
import re

from aiohttp import ClientSession
from yarl import URL

from . import AbstractTranslationProvider, Result


class DeepLTranslate(AbstractTranslationProvider):
    url: URL = URL("https://www2.deepl.com/jsonrpc")
    user_agent: str = ("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
    headers: Dict[str, str] = {"User-Agent": user_agent, "Accept-Charset": "UTF-8", "DNT": 1,
                               "Accept": "*/*", "Content-Type": "text/plain",
                               "Connection": "keep-alive", "Origin": "https://www.deepl.com",
                               "Referer": "https://www.deepl.com/translator"}
    supported_languages: Dict[str, str] = {
        "DE": "German", "EN": "English", "FR": "French", "ES": "Spanish", "IT": "Italian",
        "NL": "Dutch", "PL": "Polish", "PT": "Portuguese", "RU": "Russian",
    }

    paragraph_regex: Pattern = re.compile(r"(?:\s*\n)+\s*")

    _request_id: int

    def __init__(self, args: Dict) -> None:
        super().__init__(args)
        self._request_id = 0

    @property
    def request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _make_request(self, method: str, params: Dict[str, Any], sess: ClientSession) -> Any:
        req = {
            "id": self.request_id,
            "method": f"LMT_{method}",
            "jsonrpc": "2.0",
            "params": params,
        }
        resp = await sess.post(self.url, headers=self.headers, data=json.dumps(req))
        return await resp.json(content_type=None)

    def _split_paragraphs(self, text: str) -> List[str]:
        parts = (part.strip() for part in self.paragraph_regex.split(text))
        return [part for part in parts if len(part) > 0]

    async def _req_split_sentences(self, paragraphs: List[str], from_lang: str, sess: ClientSession,
                                   ) -> Tuple[List[List[str]], str]:
        data = await self._make_request("split_into_sentences", {
            "texts": paragraphs,
            "lang": {
                "lang_user_selected": from_lang,
                "user_preferred_langs": [],
            }
        }, sess=sess)
        print(data)
        return data["result"]["splitted_texts"], data["result"]["lang"]

    async def _req_translate(self, paragraphs: List[List[str]], from_lang: str, to_lang: str,
                             sess: ClientSession) -> List[List[str]]:
        jobs = []
        job_indexes = []
        ji = 0
        for pi, paragraph in enumerate(paragraphs):
            for si, sentence in enumerate(paragraph):
                jobs.append({
                    "kind": "default",
                    "raw_en_context_before": paragraph[:si],
                    "raw_en_sentence": sentence,
                    "raw_en_context_after": paragraph[si + 1:],
                })
                job_indexes.append((pi, si))
        data = await self._make_request("handle_jobs", {
            "jobs": jobs,
            "lang": {
                "source_lang_computed": from_lang,
                "target_lang": to_lang,
                "user_preferred_langs": [],
            }
        }, sess=sess)
        print(data)
        for ji, translation in enumerate(data["result"]["translations"].values()):
            pi, si = job_indexes[ji]
            if len(translation["beams"]) > 0:
                paragraphs[pi][si] = translation["beams"][0]["postprocessed_sentence"]
        return paragraphs

    async def translate(self, text: str, to_lang: str, from_lang: str = "auto") -> Result:
        if not from_lang:
            from_lang = "auto"
        elif from_lang != "auto":
            from_lang = from_lang.upper()
        to_lang = to_lang.upper()
        async with ClientSession() as sess:
            paragraphs, from_lang_computed = await self._req_split_sentences(
                self._split_paragraphs(text), sess=sess, from_lang=from_lang)
            await asyncio.sleep(1)
            paragraphs = await self._req_translate(paragraphs, from_lang=from_lang_computed,
                                                   to_lang=to_lang, sess=sess)
            return Result(text="\n".join(" ".join(paragraph) for paragraph in paragraphs),
                          source_language=from_lang_computed)

    def is_supported_language(self, code: str) -> bool:
        return code.upper() in self.supported_languages.keys()

    def get_language_name(self, code: str) -> str:
        return self.supported_languages[code]

    def get_supported_languages(self) -> dict:
        return self.supported_languages


make_translation_provider = DeepLTranslate
