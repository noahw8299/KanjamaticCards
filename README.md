# KanjamaticCards - a Japanese Vocabulary Anki Generator

## Overview

This Python script is designed to generate a CSV file compatible with Anki flashcards, containing Japanese vocabulary along with furigana readings, English definitions, example sentences, and more. It utilizes various libraries and APIs to enhance the learning experience.

## Features

### 1. Furigana Addition

Automatically adds furigana readings to Japanese words using the SudachiPy tokenizer. This feature enhances the visual learning experience by providing pronunciation guides for kanji characters.

### 2. Translation

Translates Japanese words and example sentences to English using Google Translator. This functionality aids in understanding the meaning of Japanese words and sentences.

### 3. Definitions

Retrieves English definitions of Japanese words using the Jisho API. This feature provides concise and accurate explanations of the meaning and usage of each vocabulary item.

### 4. Anki Compatibility

Generates a CSV file suitable for import into Anki, a popular flashcard application. The resulting flashcards include furigana readings, English definitions, and example sentences, making it convenient for Japanese language learners to review and reinforce their knowledge.

## Dependencies

- `pandas`: Data manipulation library for handling DataFrame operations.
  
- `re`: Regular expression library for string manipulation.

- `jisho_api`: API for accessing Jisho, an online Japanese dictionary.

- `sudachipy`: Japanese morphological analyzer and tokenizer.

- `wanakana`: Library for working with Japanese kana characters.

- `deep_translator`: API wrapper for Google Translator.

## Usage

1. Install the required dependencies using `pip install pandas re jisho-api sudachipy wanakana deep-translator`.

2. Customize the `KANJI_READING_MAPPING` dictionary to include specific kanji and their readings.

3. Place your vocabulary data in a CSV file with a column named 'Vocab'.

4. Run the script, and it will generate a new CSV file ('vocab.csv') suitable for Anki.

5. Import the generated CSV file into Anki to create flashcards with furigana, definitions, and translations.

## Example

...python
# Example Vocabulary CSV ('new_vocab.csv')
Vocab
私
貴女
...

# Run the script
python generate_anki_csv.py

# Generated CSV ('vocab.csv') suitable for Anki
index,word,word_with_reading,definition,example_sentence,sentence_with_reading,sentence_translation,Kanji,v1,word_audio,sentence_audio
私,私,私[わたし],I; me,私は学生です。,私は学生です。,I am a student.,True,,,,,
貴女,貴女,貴女[あなた],You (polite),貴女は先生ですか？,貴女は先生ですか？,Are you a teacher?,True,,,,,
...

## License
This project is licensed under the [MIT License](LICENSE). Feel free to customize and use it according to your needs.
