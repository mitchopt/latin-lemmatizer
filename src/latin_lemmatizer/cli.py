"""
Mitch's hacky wrapper for the CLTK Latin Lemmatiser
Accepts an input parameters file in YAML format with the following keys:
- text_path: the path to the text file to be lemmatised
- word_overrides_path: the path to a CSV file containing custom word overrides
- proper_names_path: the path to a text file listing proper names (one per line)
- output_filepath: the path to the output CSV file to be generated

"""

import csv
import string
from pathlib import Path
from typing import Annotated

import typer
import yaml
from cltk.alphabet.lat import normalize_lat
from cltk.lemmatize.lat import LatinBackoffLemmatizer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main(input_parameters: Annotated[Path, typer.Option()]):
    # Load and validate the input parameters file
    with open(input_parameters, encoding="utf-8") as file:
        params = yaml.safe_load(file)
    console.print(f"Loaded the following parameters from {input_parameters}")
    for key, val in params.items():
        console.print(f"{key}: {val}")
    stop = False
    for key in ["text_path", "word_overrides_path", "proper_names_path", "output_filepath"]:
        if key not in params:
            console.print(f"[red]Error: Missing required parameter {key} in {input_parameters}[/red]")
            stop = True
    if stop:
        return

    # Load the text file
    with open(params["text_path"], encoding="utf-8") as file:
        lines = file.readlines()
    console.print("Loaded the text file successfully. Here is the first line!")
    console.print(f"[yellow]{lines[0]}[/yellow]")

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

    # Punctuation string
    punctuation = string.punctuation + "“”‘’—…"

    # Initialise the lemmatiser
    console.print("Now running the lemmatiser...")
    L = LatinBackoffLemmatizer()

    # Initialise the output data dictionary
    output_data = {}

    # Iterate the lines
    for line in lines:
        line = line.translate(str.maketrans("", "", punctuation))  # Remove punctuation
        line = normalize_lat(line, drop_macrons=True)  # Drop macrons
        words = line.split()
        # Iterate the words in the line
        for word in words:
            # Strip -que suffix
            if word.endswith("que"):
                word = word[:-3]
            lemma = L.lemmatize([word])[0]  # Lemmatize the word
            # Check if the word begins with a capital letter
            if lemma[0][0].isupper():
                if lemma[1] not in names:
                    word = word.lower()  # If it is not a name then lower case it
                    lemma = L.lemmatize([word])[0]  # Lemmatize the lower case word

            # Check for word overrides
            if lemma[0] in word_overrides:
                lemma = (lemma[0], word_overrides[lemma[0]])

            # Update the counts in the data dictionary if the lemma has been seen
            if lemma[1] in output_data:
                output_data[lemma[1]]["freq"] += 1
                output_data[lemma[1]]["hits"].add(lemma[0])
                continue

            # Otherwise generate a new entry in the output data dictionary
            output_data[lemma[1]] = {"freq": 1, "hits": set([lemma[0]])}

    console.print(f"Writing output CSV to {params['output_filepath']}...")
    with open(params["output_filepath"], "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["lemma", "frequency", "hits..."])
        for word in output_data:
            row = [word, output_data[word]["freq"]] + list(output_data[word]["hits"])
            writer.writerow(row)


if __name__ == "__main__":
    app()
