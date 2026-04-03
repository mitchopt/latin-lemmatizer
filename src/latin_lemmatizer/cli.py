"""
A hacky Latin lemmatiser based on the CLTK lemmata dataset.
Does not explicitly depend on the CLTK toolkit, but on an extracted copy of the dataset.
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
from rich.console import Console

from latin_lemmatizer.lemmata import LEMMATA
from latin_lemmatizer.utils import drop_macrons, load_from_parameters_yaml, load_parameters_yaml

app = typer.Typer()
console = Console()


@app.command()
def main(input_parameters: Annotated[Path, typer.Option(resolve_path=True)]):
    # Load the input parameters yaml file
    params = load_parameters_yaml(input_parameters, console)
    if params is None:
        console.print("[red]\n       Failed to load input parameters yaml.[/red]")
        console.print("[red]       Terminating program.[/red]")
        return

    # Load the input parameters from the params dictionary
    inputs = load_from_parameters_yaml(params, console)
    if inputs is None:
        console.print("[red]\n       Failed to load input files.[/red]")
        console.print("[red]       Terminating program.[/red]")
        return

    # Punctuation string
    punctuation = string.punctuation + "“”‘’—…"

    # Initialise the output dictionaries
    output_data = {}
    bad_words = set()

    # Iterate the lines
    # console.print("Now running the lemmatiser...")
    for line in inputs.lines:
        line = line.translate(str.maketrans("", "", punctuation))  # Remove punctuation
        line = drop_macrons(line)  # Drop macrons
        words = line.split()  # Split the line into words
        for word in words:  # Iterate the words in the line
            lemma = None  # Clear the lemma variable from the previous word
            if word.endswith("que"):  # Strip -que suffix
                word = word[:-3]

            # Apply word word overrides
            if word in inputs.word_word_overrides:
                word = inputs.word_word_overrides[word]

            # Initial lemma lookup
            lemma = LEMMATA.get(word)

            # Apply word lemma overrides
            if word in inputs.word_lemma_overrides:
                lemma = inputs.word_lemma_overrides[word]
            
            # Word lemma overrides give a user specified lemma for a word, so we can skip further processing
            else:
                # Check if word is upper case
                if word[0].isupper():
                    # Check if the word is not a proper noun
                    if lemma is not None:
                        lemma_stripped = lemma.translate(str.maketrans("", "", "1234"))
                        if lemma_stripped not in inputs.names:
                            word = word.lower()
                            lemma = LEMMATA.get(word)

                    # If the lemma is none, try the lower case word. If that works then use it
                    else:
                        word_lower = word.lower()
                        lemma_lower = LEMMATA.get(word_lower)
                        if lemma_lower is not None:
                            word, lemma = word_lower, lemma_lower

                # Apply lemma lemma overrides
                if lemma in inputs.lemma_lemma_overrides:
                    lemma = inputs.lemma_lemma_overrides[lemma]

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

    # console.print(f"Writing output CSV to {params['output_filepath']}...")
    with open(params["output_filepath"], "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["lemma", "frequency", "hits..."])
        for item in output_data_sorted_items:
            row = [item[0], item[1]["freq"]] + sorted(list(item[1]["hits"]))
            writer.writerow(row)


if __name__ == "__main__":
    app()
