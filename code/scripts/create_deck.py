import pandas as pd
import re
from jisho_api.sentence import Sentence
from jisho_api.word import Word
from sudachipy import tokenizer
from sudachipy import dictionary
from wanakana import to_hiragana, is_japanese, is_katakana, is_hiragana, is_kanji
from deep_translator import (ChatGptTranslator, GoogleTranslator)
import string

# Initialize SudachiPy tokenizer
tokenizer_obj = dictionary.Dictionary(dict_type="small").create()

# Dictionary mapping kanji to their readings
KANJI_READING_MAPPING = {
    '私': '私[わたし]',
    '貴女': '貴女[あなた]',
    '何': '何[なに]',
    '外宇宙': '外宇宙[がいうちゅう]',
    '異星人': '異星人[いせいじん]',
    '優那': '優那[ゆうな]',
    '菜々美': '菜々美[ななみ]'
}

# Japanese punctuation characters
JAPANESE_PUNCTUATION = '　〜！？。、（）：「」『』０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'

# Special characters to handle
SPECIAL_CHARACTERS = '〜'

def is_japanese_extended(text):
    """
    Check if a given text is Japanese extended (not punctuation).
    """
    return is_japanese(text) and text not in string.punctuation and text not in JAPANESE_PUNCTUATION

def to_anki_format(index, kanji, reading):
    """
    Format a kanji with reading for Anki flashcards.
    """
    return '{}{}[{}]'.format(' ' if index > 0 else '', kanji, reading) 

def add_furigana(text):
    """
    Add furigana to Japanese text using SudachiPy tokenizer.
    """
    # Tokenize the text
    tokens = [m for m in tokenizer_obj.tokenize(text, tokenizer.Tokenizer.SplitMode.C)]
    parsed = ''
    token_indexes_to_skip = []

    # Iterate through tokens
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

                    # Parse the token and add furigana
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
    """
    Translate Japanese word to English using Google Translator.
    """
    return GoogleTranslator(source='japanese', target='english').translate(text=word)

def scrape_def(word):
    """
    Scrape definitions of a word using Jisho API.
    """
    r = Word.request(word)
    result = ""
    
    # Concatenate English definitions
    for item in r.data[0].senses[0].english_definitions:
        result += f"{item}; "
    
    parts_of_speech = r.data[0].senses[0].parts_of_speech
    
    # Format parts of speech and definitions
    if len(parts_of_speech) == 1:
        return f"{parts_of_speech[0]}\n" + result[:-2]
    else:
        return f"{parts_of_speech[1]} - {parts_of_speech[0]}\n" + result[:-2]

def define_word(row):
    """
    Define a word by checking if a definition exists in the row.
    If not, scrape the definition using Jisho API.
    """
    if pd.isna(row['Definition']):
        return scrape_def(row['Vocab'])
    else:
        return row['Definition']

def get_example(row):
    """
    Get example sentence, furigana, and English translation.
    """
    if pd.isna(row['Sentence']):
        r = Sentence.request(row['Vocab'])
        if r is not None:
            if r.data:  # Check if data is not empty
                for item in r.data:
                    sentence = item.japanese
                    no_furigana, furigana = replace_parentheses(sentence)
                    english = item.en_translation
                    return no_furigana, furigana, english
        return None, None, None  # Return None if no match found or no data
    elif pd.isna(row['Sentence_def']):
        return row['Sentence'], add_furigana(row['Sentence']), translate(row['Sentence'])
    else:
        return row['Sentence'], add_furigana(row['Sentence']), row['Sentence_def']

def replace_parentheses(input_string):
    """
    Replace parentheses in the input string with brackets and remove content within parentheses.
    """
    # Replace all parentheses with brackets
    brackets_replaced = input_string.replace('(', '[').replace(')', ']')

    # Remove parentheses and content within them using regular expressions
    parentheses_removed = re.sub(r'\([^)]*\)', '', input_string)

    return parentheses_removed, brackets_replaced

# Read the vocabulary CSV file into a DataFrame
vocabulary = pd.read_csv('../../data/new_vocab.csv')

# Initialize an empty DataFrame with specific columns
data = []
columns = ['index', 'word', 'word_with_reading', 'definition', 'example_sentence', 'sentence_with_reading', 'sentence_translation', 'Kanji', 'v1', 'word_audio', 'sentence_audio']
df = pd.DataFrame(data, columns=columns)

# Populate the 'index' and 'word' columns with vocabulary data
df['index'] = vocabulary['Vocab']
df['word'] = vocabulary['Vocab']

# Apply the 'add_furigana' function to create 'word_with_reading'
df['word_with_reading'] = vocabulary['Vocab'].apply(add_furigana)

# Apply the 'define_word' function to create 'definition'
df['definition'] = vocabulary.apply(define_word, axis=1)

# Apply the 'get_example' function to create 'example_sentence', 'sentence_with_reading', and 'sentence_translation'
sentences = vocabulary.apply(get_example, axis=1, result_type='expand')
df['example_sentence'] = sentences[0]
df['sentence_with_reading'] = sentences[1]
df['sentence_translation'] = sentences[2]

# Set 'Kanji' column to True for all rows
df['Kanji'] = True

# Save the resulting DataFrame to a new CSV file
df.to_csv('../../data/vocab.csv', encoding="utf-8", index=False, header=False)
