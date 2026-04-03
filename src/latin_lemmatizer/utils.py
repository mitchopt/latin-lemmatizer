# Utils for latin lemmatizer
import csv
from dataclasses import dataclass

import yaml


# Drop macrons from string
def drop_macrons(word):
    word = word.replace("ā", "a").replace("Ā", "A")
    word = word.replace("ē", "e").replace("Ē", "E")
    word = word.replace("ī", "i").replace("Ī", "I")
    word = word.replace("ō", "o").replace("Ō", "O")
    word = word.replace("ū", "u").replace("Ū", "U")
    word = word.replace("ȳ", "y").replace("Ȳ", "Y")
    return word


def load_parameters_yaml(input_parameters, console):
    try:
        with open(input_parameters, encoding="utf-8") as file:
            params = yaml.safe_load(file)
    except FileNotFoundError:
        console.print(f"[red]Error: could not find the specified input parameters file:\n {input_parameters} [/red]")
        return None
    if "output_path" not in params:
        console.print("[red]Error: 'output_path' is missing from the input parameters yaml.[/red]")
        return None
    return params


@dataclass
class Inputs:
    """Class for holding inputs loaded from the parameters file."""

    lines: list
    word_word_overrides: dict
    lemma_lemma_overrides: dict
    word_lemma_overrides: dict
    names: set


# Load files based on the input parameters
def load_from_parameters_yaml(params, console):
    # Track failures to load files so that we can detect all issues before exiting, rather than only the first one
    fail = False
    # Load the text file
    try:
        with open(params["text_path"], encoding="utf-8") as file:
            lines = file.readlines()
        if lines:
            console.print(f"Loaded text file with [green]{len(lines)}[/green] lines. Here is the first one:")
            console.print(f"[yellow]{lines[0].translate(str.maketrans('', '', '\n'))}[/yellow]")
    except KeyError:
        console.print('[red]Error: "text_path" is missing from the input parameters file.')
        fail = True
    except FileNotFoundError:
        console.print(f"[red]Error: could not find the specified text file:\n {params['text_path']}[/red]")
        fail = True

    # Load the word to word overrides if provided
    if "word_word_overrides_path" in params:
        try:
            with open(params["word_word_overrides_path"], encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                word_word_overrides = {row[0]: row[1].strip() for row in reader if len(row) == 2}
        except FileNotFoundError:
            console.print("[red]Error: could not find the specified word overrides file:[/red]")
            console.print(f"[red]{params['word_word_overrides_path']}[/red]")
            fail = True

    # Load the lemma to lemma overrides if provided
    if "lemma_lemma_overrides_path" in params:
        try:
            with open(params["lemma_lemma_overrides_path"], encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                lemma_lemma_overrides = {row[0]: row[1].strip() for row in reader if len(row) == 2}
        except FileNotFoundError:
            console.print("[red]Error: could not find the specified lemma overrides file:[/red]")
            console.print(f"[red]{params['lemma_lemma_overrides_path']}[/red]")
            fail = True

    # Load the word to lemma overrides if provided
    if "word_lemma_overrides_path" in params:
        try:
            with open(params["word_lemma_overrides_path"], encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                word_lemma_overrides = {row[0]: row[1].strip() for row in reader if len(row) == 2}
        except FileNotFoundError:
            console.print("[red]Error: could not find the specified word to lemma overrides file:[/red]")
            console.print(f"[red]{params['word_lemma_overrides_path']}[/red]")
            fail = True

    # Load the proper names if provided
    if "proper_nouns_path" in params:
        try:
            with open(params["proper_nouns_path"], encoding="utf-8") as file:
                names = set()
                for name in file:
                    names.add(name.strip())
        except FileNotFoundError:
            console.print("[red]Error: could not find the specified proper nouns file:[/red]")
            console.print(f"[red]{params['proper_nouns_path']}[/red]")
            fail = True

    # Return None on failure
    if fail:
        return None
    # Otherwise populate and return an Inputs dataclass
    else:
        return Inputs(
            lines=lines,
            word_word_overrides=word_word_overrides if "word_word_overrides_path" in params else {},
            lemma_lemma_overrides=lemma_lemma_overrides if "lemma_lemma_overrides_path" in params else {},
            word_lemma_overrides=word_lemma_overrides if "word_lemma_overrides_path" in params else {},
            names=names if "proper_nouns_path" in params else set(),
        )


def write_output_csv(output_data_sorted_items, params, console):
    console.print(f"Writing output CSV to [green]{params['output_path']}[/green]")
    with open(params["output_path"], "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["lemma", "frequency", "hits..."])
        for item in output_data_sorted_items:
            row = [item[0], item[1]["freq"]] + sorted(list(item[1]["hits"]))
            writer.writerow(row)
