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
from typing import Dict

from aiohttp import ClientSession
from yarl import URL

from . import AbstractTranslationProvider, Result


class GoogleTranslate(AbstractTranslationProvider):
    # Secret translation endpoint used by the Google Translate extension and other such things.
    url: URL = URL("https://translate.googleapis.com/translate_a/single")
    # Needs to be some real browser so Google accepts it
    user_agent: str = ("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
    headers: Dict[str, str] = {"User-Agent": user_agent, "Accept-Charset": "UTF-8",
                               "Connection": "keep-alive", "Accept": "application/json"}
    # From https://cloud.google.com/translate/docs/languages
    supported_languages = {
        "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic", "hy": "Armenian",
        "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian",
        "bg": "Bulgarian", "ca": "Catalan", "ceb": "Cebuano", "zh-cn": "Chinese (Simplified)",
        "zh": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)", "co": "Corsican",
        "hr": "Croatian", "cs": "Czech", "da": "Danish", "nl": "Dutch", "en": "English",
        "eo": "Esperanto", "et": "Estonian", "fi": "Finnish", "fr": "French", "fy": "Frisian",
        "gl": "Galician", "ka": "Georgian", "de": "German", "el": "Greek", "gu": "Gujarati",
        "ht": "HaitianCreole", "ha": "Hausa", "haw": "Hawaiian", "he": "Hebrew", "iw": "Hebrew",
        "hi": "Hindi", "hmn": "Hmong", "hu": "Hungarian", "is": "Icelandic", "ig": "Igbo",
        "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese", "jw": "Javanese",
        "kn": "Kannada", "kk": "Kazakh", "km": "Khmer", "ko": "Korean", "ku": "Kurdish",
        "ky": "Kyrgyz", "lo": "Lao", "la": "Latin", "lv": "Latvian", "lt": "Lithuanian",
        "lb": "Luxembourgish", "mk": "Macedonian", "mg": "Malagasy", "ms": "Malay",
        "ml": "Malayalam", "mt": "Maltese", "mi": "Maori", "mr": "Marathi", "mn": "Mongolian",
        "my": "Myanmar", "ne": "Nepali", "no": "Norwegian", "ny": "Nyanja", "ps": "Pashto",
        "fa": "Persian", "pl": "Polish", "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian",
        "ru": "Russian", "sm": "Samoan", "gd": "ScotsGaelic", "sr": "Serbian", "st": "Sesotho",
        "sn": "Shona", "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak", "sl": "Slovenian",
        "so": "Somali", "es": "Spanish", "su": "Sundanese", "sw": "Swahili", "sv": "Swedish",
        "tl": "Tagalog", "tg": "Tajik", "ta": "Tamil", "te": "Telugu", "th": "Thai",
        "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek", "vi": "Vietnamese",
        "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu",
        "auto": "Detect language",
    }

    def __init__(self, args: Dict) -> None:
        super().__init__(args)

    async def translate(self, text: str, to_lang: str, from_lang: str = "auto") -> Result:
        if not from_lang:
            from_lang = "auto"
        async with ClientSession() as sess:
            resp = await sess.get(self.url.with_query({"client": "gtx", "dt": "t", "q": text,
                                                       "sl": from_lang, "tl": to_lang}),
                                  headers=self.headers)
            data = await resp.json()
            return Result(text="".join(item[0] for item in data[0] if len(item) > 0 and item[0]),
                          source_language=data[8][0][0] if len(data) > 8 else data[2])

    def is_supported_language(self, code: str) -> bool:
        return code.lower() in self.supported_languages.keys()

    def get_language_name(self, code: str) -> str:
        return self.supported_languages[code.lower()]


make_translation_provider = GoogleTranslate
