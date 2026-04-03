"""
Mitch's hacky wrapper for the CLTK Latin Lemmatiser
Accepts an input parameters file in YAML format with the following keys:
- text_path: the path to the text file to be lemmatised
- word_overrides_path: the path to a CSV file containing custom word overrides
- lemma_overrides_path: the path to a CSV file containing custom lemma overrides
- proper_names_path: the path to a text file listing proper names (one per line)
- output_filepath: the path to the output CSV file to be generated

"""

import csv
import string
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console

from latin_lemmatizer.lemmata import LEMMATA
from latin_lemmatizer.utils import drop_macrons

app = typer.Typer()
console = Console()


@app.command()
def main(input_parameters: Annotated[Path, typer.Option()]):
    # Load and validate the input parameters file
    with open(input_parameters, encoding="utf-8") as file:
        params = yaml.safe_load(file)
    console.print(f"Loaded parameters file {input_parameters}")
    stop = False
    for key in ["text_path", "word_overrides_path", "lemma_overrides_path", "proper_names_path", "output_filepath"]:
        if key not in params:
            console.print(f"[red]Error: Missing required parameter {key} in {input_parameters}[/red]")
            stop = True
    if stop:
        return

    # Load the text file
    with open(params["text_path"], encoding="utf-8") as file:
        lines = file.readlines()
    console.print("\nLoaded the text file successfully. Here is the first line!")
    console.print(f"[yellow]{lines[0].replace('\n', ' ')}[/yellow]\n")

    # Load the proper names
    console.print(f"Loading proper names from {params['proper_names_path']}...")
    with open(params["proper_names_path"], encoding="utf-8") as file:
        names = set()
        for name in file:
            names.add(name.strip())

    # Load the word overrides
    console.print(f"Loading custom word overrides from {params['word_overrides_path']}...")
    with open(params["word_overrides_path"], encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        word_overrides = {row[0]: row[1].strip() for row in reader}

    # Load the lemma overrides
    console.print(f"Loading custom lemma overrides from {params['lemma_overrides_path']}...")
    with open(params["lemma_overrides_path"], encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        lemma_overrides = {row[0]: row[1].strip() for row in reader}

    # Punctuation string
    punctuation = string.punctuation + "“”‘’—…"

    # Initialise the output dictionaries
    output_data = {}
    bad_words = set()

    # Iterate the lines
    console.print("Now running the lemmatiser...")
    for line in lines:
        line = line.translate(str.maketrans("", "", punctuation))  # Remove punctuation
        line = drop_macrons(line)  # Drop macrons
        words = line.split()  # Split the line into words
        for word in words:  # Iterate the words in the line
            if word.endswith("que"):  # Strip -que suffix
                word = word[:-3]

            # Apply word overrides
            if word in word_overrides:
                word = word_overrides[word]

            # Initial lemma lookup
            lemma = LEMMATA.get(word)

            # Check if word is upper case
            if word[0].isupper():
                # Check if the word is a proper name
                if lemma is not None:
                    lemma_stripped = lemma.translate(str.maketrans("", "", "1234"))
                    if lemma_stripped not in names:
                        word = word.lower()
                        lemma = LEMMATA.get(word)

                # If the lemmas is none, try the lower case word. If that works then use it
                else:
                    word_lower = word.lower()
                    lemma_lower = LEMMATA.get(word_lower)
                    if lemma_lower is not None:
                        word, lemma = word_lower, lemma_lower

            # Check for lemma overrides
            if lemma in lemma_overrides:
                lemma = lemma_overrides[lemma]

            # If the lemma is still none then add it to the bad words set and move on
            if lemma is None:
                bad_words.add(word)
                continue

            # Otherwise update the counts in the output data dictionary
            if lemma in output_data:
                output_data[lemma]["freq"] += 1
                output_data[lemma]["hits"].add(word)
            else:
                output_data[lemma] = {"freq": 1, "hits": set([word])}

    # Sort output data by frequency
    output_data_sorted_items = sorted(output_data.items(), key=lambda x: x[1]["freq"], reverse=True)

    console.print(f"Writing output CSV to {params['output_filepath']}...")
    with open(params["output_filepath"], "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["lemma", "frequency", "hits..."])
        for item in output_data_sorted_items:
            row = [item[0], item[1]["freq"]] + sorted(list(item[1]["hits"]))
            writer.writerow(row)


if __name__ == "__main__":
    app()
