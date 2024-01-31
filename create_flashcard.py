import pandas as pd
from sudachipy import tokenizer
from sudachipy import dictionary
from wanakana import to_hiragana, is_japanese, is_katakana, is_hiragana, is_kanji
from deep_translator import (ChatGptTranslator, GoogleTranslator)
import string

chat_gpt_apikey = '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'

tokenizer_obj = dictionary.Dictionary(dict_type="small").create()

KANJI_READING_MAPPING = {
    '私': '私[わたし]',
    '貴女': '貴女[あなた]',
    '何': '何[なに]',
    '外宇宙': '外宇宙[がいうちゅう]',
    '異星人': '異星人[いせいじん]',
    '優那': '優那[ゆうな]',
    '菜々美': '菜々美[ななみ]'
}

JAPANESE_PUNCTUATION = '　〜！？。、（）：「」『』０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'

SPECIAL_CHARACTERS = '〜'

def is_japanese_extended(text):
    return is_japanese(text) and text not in string.punctuation and text not in JAPANESE_PUNCTUATION

def to_anki_format(index, kanji, reading):
    return '{}{}[{}]'.format(' ' if index > 0 else '', kanji, reading) 

def add_furigana(text):
    tokens = [m for m in tokenizer_obj.tokenize(text, tokenizer.Tokenizer.SplitMode.C)]
    parsed = ''
    token_indexes_to_skip = []
    for index, token in enumerate(tokens):   
        if index in token_indexes_to_skip:
          continue
        to_parse = is_japanese_extended(token.surface()) and not is_katakana(token.surface()) and not is_hiragana(token.surface())
        if to_parse:
            if token.surface()[-1] in SPECIAL_CHARACTERS:
                parsed += add_furigana(token.surface()[:-1]) + token.surface()[-1]
            else:
                if index > 0:
                    parsed += ' '
                reading = to_hiragana(token.reading_form())
                if token.surface() in KANJI_READING_MAPPING:
                    parsed += KANJI_READING_MAPPING[token.surface()]
                elif index < len(tokens)-1 and token.surface() + tokens[index+1].surface() in KANJI_READING_MAPPING:
                    parsed += KANJI_READING_MAPPING[tokens[index].surface() + tokens[index+1].surface()]
                    token_indexes_to_skip.append(index+1)
                else:
                    surface_index = 0
                    reading_index = 0
                    while len(token.surface()) > surface_index:
                        if is_hiragana(token.surface()[surface_index]) or is_katakana(token.surface()[surface_index]):
                            parsed += token.surface()[surface_index]
                            reading_index += 1
                            surface_index += 1
                        else:
                            next_index = -1
                            for token_index in range(surface_index, len(token.surface())):
                                if is_hiragana(token.surface()[token_index]) or is_katakana(token.surface()[token_index]):
                                    next_index = token_index
                                    break
                            if next_index < 0:
                                parsed += to_anki_format(
                                  index=surface_index, 
                                  kanji=token.surface()[surface_index:], reading=reading[reading_index:])
                                break
                            else:
                                reading_index_tail = reading_index
                                while reading[reading_index_tail] != token.surface()[next_index] or (reading_index_tail < len(reading)-1 and reading[reading_index_tail] == reading[reading_index_tail+1]):
                                    reading_index_tail += 1
                                parsed += to_anki_format(
                                  index=surface_index, 
                                  kanji=token.surface()[surface_index:next_index], reading=reading[reading_index:reading_index_tail])
                                reading_index = reading_index_tail
                            reading_length = next_index - surface_index
                            if reading_length > 0:
                                surface_index += reading_length
                            else:
                                break
        else:
            parsed += token.surface()
    return parsed

data = []
columns = ['index', 'word', 'word_with_reading', 'defintion', 'example_sentence', 'sentence_with_reading', 'setence_translation', 'Kanji', 'v1', 'word_audio', 'setence_audio']

while input("you got a word for me?\n").lower() == 'yes':

    word = input("enter some shit if u want idc\n")

    definition = GoogleTranslator(source='japanese', target='english').translate(text=word)

    sentence = input("u got a sentence to go wit that bitch?\n")

    if sentence.lower() == 'no':
        sentence = None
        sentence_def = None
    else:
        sentence_def = GoogleTranslator(source='japanese', target='english').translate(text=sentence)

    info = [word, word, add_furigana(word), definition, sentence, add_furigana(sentence) if sentence is not None else None, sentence_def, True, None, None, None]

    data.append(info)

df = pd.DataFrame(data, columns=columns)

df.to_csv('vocab.csv', encoding="utf-8", index=False, header=False)