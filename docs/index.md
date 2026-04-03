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
We can see that arma has been lemmatized as the verb ``armo`` instead of the desired arma (arma is already nominative singular). So we will include a row in ``word_lemma_overrides.csv``
```csv
arma, arma
```
Note that user overrides are simply trusted. If we add ``arma, potato`` to the overrides, the output will be
```csv
lemma,frequency,hits...
potato,1,arma
vir,1,virum
cano,1,cano
```
