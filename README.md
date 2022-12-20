# translate
A [maubot](https://github.com/maubot/maubot) to translate words using [Google
Translate](https://translate.google.com/about/) or
[LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)
(Deepl is planned too)

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
to let the bot detect the source language. Additionally, you can reply
to a message with `!tr <from> <to>` (no text) to translate the message you
replied to.

## supported languages:

Since this depends on which translation provider you choose and can even vary from
one LibreTranslate instance to another, you can use the following command to get
all the supported languages and their codes:

    !languages
