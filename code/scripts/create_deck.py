import pandas as pd
from sudachipy import tokenizer
from sudachipy import dictionary
from wanakana import to_hiragana, is_japanese, is_katakana, is_hiragana, is_kanji
from deep_translator import (ChatGptTranslator, GoogleTranslator)
import string

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

def translate(word):
    return GoogleTranslator(source='japanese', target='english').translate(text=word)

vocabulary = pd.read_csv('../../data/new_vocab.csv')

data = []
columns = ['index', 'word', 'word_with_reading', 'definition', 'example_sentence', 'sentence_with_reading', 'sentence_translation', 'Kanji', 'v1', 'word_audio', 'setence_audio']
df = pd.DataFrame(data, columns=columns)

df['index'] = vocabulary['Vocab']
df['word'] = vocabulary['Vocab']
df['word_with_reading'] = vocabulary['Vocab'].apply(add_furigana)
df['definition'] = vocabulary['Vocab'].apply(translate)
df['example_sentence'] = vocabulary['Sentence']
df['sentence_with_reading'] = vocabulary['Sentence'].apply(add_furigana)
df['sentence_translation'] = vocabulary['Sentence'].apply(translate)
df['Kanji'] = True

df.to_csv('../../data/vocab.csv', encoding="utf-8", index=False, header=False)