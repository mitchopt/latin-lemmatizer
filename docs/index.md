# Latin Lemmatizer

Custom tool for Latin text lemmatisation. Uses an extracted copy of the CLTK Latin lemmata data, but does not explicitly depend on CLTK.

## Getting started

- [Installation](installation.md) - how to install Latin Lemmatizer

## Usage
An --input-parameters option pointing to a yaml file is necessary.
```bash
uv run latin_lemmatizer --input-parameters ./input_parameters.yaml
```
The input parameters yaml **must** specify `text_path` and `output_path` values
```yaml
text_path: "./data/test.txt"
output_path: "./outputs/test.csv"
```

## Features

This tool uses a naive dictionary lookup to lemmatize a Latin text file. Lemma frequency information is then written to a CSV file. Several user override options can be activated by including filepaths in the input parameters yaml. For example:
```yaml
text_path: "./data/test.txt"
output_path: "./outputs/test.csv"
word_lemma_overrides_path: "./data/word_lemma_overrides.csv"
word_word_overrides_path: "./data/word_word_overrides.csv"
lemma_lemma_overrides_path: "./data/lemma_lemma_overrides.csv"
proper_nouns_path: "./data/proper_names.txt"
```

### proper nouns
A text file containing proper names (one per line) can be provided. Words beginning with an upper case letter will be converted to lower case, unless they are included in the proper nouns file. This occurs _before_ any other input override. For example, the word _Arma_ will fail lemmatization unless convered to lower case. On the other hand, _Iuppiter_ will fail unless it remains upper case. Therefore the default behaviour is to convert all words to lower case unless found in the proper nouns override.

### word-lemma overrides
word-lemma overrides are used to bypass the lookup entirely. Consider the following Latin sentence:
```text
arma virumque canō
```
The default output of the lemmatizer is
```csv
lemma,frequency,hits...
armo,1,arma
vir,1,virum
cano,1,cano
```
We can see that arma has been lemmatized as the verb ``armo`` instead of the desired arma (arma is already nominative singular). So we will include a row ``arma, arma`` in the ``word_lemma_overrides.csv`` with the word on the left and the correct lemma on the right. Note that all user overrides are trusted. If we add ``arma, potato`` as a word-lemma override, the output will be
```csv
lemma,frequency,hits...
potato,1,arma
vir,1,virum
cano,1,cano
```

### word-word overrides
word-word overrides allow us to replace one word with another _before_ lemmatization.

### lemma-lemma overrides
lemma-lemma overrides us allow us to replace one lemma with another _after_ lemmatization.

### Summary
Consider two words with two default lemmas:
```bash
word1: lemma1
word2: lemma2
```
With no overrides, the sentence ``word1 word2`` will lemmatize to
```csv
lemma, frequency, hits...
lemma1, 1, word1
lemma2, 1, word2
```
With a word-lemma override ``word1, lemma3`` the sentence will instead lemmatize to
```csv
lemma, frequency, hits...
lemma3, 1, word1
lemma2, 1, word2
```
With a word-word override ``word1, word2`` the sentence will instead lemmatize to
```csv
lemma, frequency, hits...
lemma2, 2, word1, word2
```
With a lemma-lemma override ``lemma2, lemma3`` the sentence will instead lemmatize to
```csv
lemma, frequency, hits...
lemma1, 1, word1
lemma3, 1, word2
```

