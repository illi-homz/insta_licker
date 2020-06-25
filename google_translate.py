from googletrans import Translator


def en_translator(text):
    translator = Translator()
    translate = translator.translate(text, dest='en')
    return translate.text

def ru_translator(text):
    translator = Translator()
    translate = translator.translate(text, dest='ru')
    return translate.text
