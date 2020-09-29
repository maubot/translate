# translate
A [maubot](https://github.com/maubot/maubot) to translate words using Google Translate (DeepL is planned too)

## Usage

After inviting the bot to your room, simply use the `!translate` command:

    !translate en ru Hello world.
    
which results in

    Translate Bot:
    > rubo77
    > !translate en ru Hello world.
    Привет, мир.

You can also use the alias `tr`:

    !tr en ru Hello world.

The first parameter (source language) can be set to `auto` or omitted entirely
to let Google Translate detect the source language. Additionally, you can reply
to a message with `!tr <from> <to>` (no text) to translate the message you
replied to.

## supported languages:

- de: (german)
- en: (english)
- zh: (chinese)
- ...

Full list of supported languages: https://cloud.google.com/translate/docs/languages
