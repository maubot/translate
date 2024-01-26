# translate
A [maubot](https://github.com/maubot/maubot) to translate words using [Google
Translate](https://translate.google.com/about/) or
[LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)
(Deepl is planned too)

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

Since this depends on which translation provider you choose and can even vary from
one LibreTranslate instance to another, you can use the following command to get
all the supported languages and their codes:

    !languages

## Providers

To initiate a translation, the given message arguments are paresed and
passed forward to as a HTTP-requests to the given provider. The
communication does consume the provider specific API methods.

### google

Cloud Translation API uses Google's neural machine translation
technology to let you dynamically translate text through the API using
a Google pre-trained or custom model.

It has two editions: Basic and Advanced. Both provide fast and dynamic
translation, but Advanced offers additional customization features,
such as domain-specific translation, formatted document translation,
and batch translation.

The `first 500,000 characters` sent to the API to process (Basic and
Advanced combined) per month are free.

### deepl

The DeepL API provides programmatic access to DeepL’s machine
translation technology, making it possible to bring high quality
translation capabilities directly to this translation bot.
For further infomation, please consult their
[API-Documentation](https://www.deepl.com/docs-api/introduction "DeepL-API").

Depending of the choosen model (DeepL API Pro vs. Deepl API Free) the
correct connection URL needs to be send in the POST requests. Both
API's do require an `auth_key`. The `auth_key` does identify the given
customer and is used to charge accordingly.
With the DeepL API Free plan, you can translate up to `500,000
characters` per month for free.

To use `DeepL API Free`, devolopers may register free of charge and
recieve an `auth_key`. Thus, the have to provide a valid credit-card
number.
