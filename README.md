# translate
A [maubot](https://github.com/maubot/maubot) to translate words using Google Translate
or LibreTranslate (Deepl is also planned)

## Usage

After inviting the bot to your room, simply use the `!translate` command:

    !translate en uk Hello, world!
    
which results in

    Translate Bot:
    > rubo77
    > !translate en uk Hello, world!
    Привіт Світ!

You can also use the alias `tr`:

    !tr en uk Hello, world!

The first parameter (source language) can be set to `auto` or omitted entirely
to let the bot detect the source language. Additionally, you can reply
to a message with `!tr <from> <to>` (no text) to translate the message you
replied to.

## supported languages:

This depends on the translation provider you choose. For google, a list of
supported languages can be found at https://cloud.google.com/translate/docs/languages
