"""
A hacky Latin lemmatiser based on the CLTK lemmata dataset.
Does not explicitly depend on the CLTK toolkit, but on an extracted copy of the dataset.
Accepts an input parameters file in YAML format with the following keys:
- text_path: the path to the text file to be lemmatised
- word_overrides_path: the path to a CSV file containing custom word overrides
- lemma_overrides_path: the path to a CSV file containing custom lemma overrides
- proper_names_path: the path to a text file listing proper names (one per line)
- output_path: the path to the output CSV file to be generated

"""

import string
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from latin_lemmatizer.lemmata import LEMMATA
from latin_lemmatizer.utils import drop_macrons, load_from_parameters_yaml, load_parameters_yaml, write_output_csv

app = typer.Typer()
console = Console()


@app.command()
def main(input_parameters: Annotated[Path, typer.Option(resolve_path=True)]):
    console.print("[green]Running Latin Lemmatizer[/green]")
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
    for line in inputs.lines:
        line = line.translate(str.maketrans("", "", punctuation))  # Remove punctuation
        line = drop_macrons(line)  # Drop macrons
        words = line.split()  # Split the line into words
        for word in words:  # Iterate the words in the line
            lemma = None  # Clear the lemma variable from the previous word
            if word.endswith("que"):  # Strip -que suffix
                word = word[:-3]

            # Initial lemma lookup
            lemma = LEMMATA.get(word)

            # If a word starts with a capital letter and fails to lemmatize then it is
            # probably not a proper noun. This is because most proper nouns in the CLTK lemmata
            # dataset correctly begin with an upper case letter and lemmatize successfully,
            # wheras other words that start with an upper case letter are likely to fail.
            if word[0].isupper():
                if lemma is None:
                    word = word.lower()
                    lemma = LEMMATA.get(word)
                if lemma is not None:
                    lemma_stripped = lemma.translate(str.maketrans("", "", "1234"))
                    if lemma_stripped not in inputs.names:
                        word = word.lower()
                        lemma = LEMMATA.get(word)

            # Apply word word overrides
            if word in inputs.word_word_overrides:
                word = inputs.word_word_overrides[word]
                lemma = LEMMATA.get(word)

            # Apply word lemma overrides
            if word in inputs.word_lemma_overrides:
                lemma = inputs.word_lemma_overrides[word]

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

    # Log any bad words to the console
    if bad_words:
        console.print(f"\n[purple]Failed to lemmatise the following [red]{len(bad_words)}[/red] words:[/purple]")
        for word in bad_words:
            console.print(f"[purple] {word}[/purple]")

    # Sort output data by frequency and then write the output CSV
    output_data_sorted_items = sorted(output_data.items(), key=lambda x: x[1]["freq"], reverse=True)
    write_output_csv(output_data_sorted_items, params, console)


if __name__ == "__main__":
    app()
