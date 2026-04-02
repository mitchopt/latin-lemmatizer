# Latin Lemmatizer

![PyPI version](https://img.shields.io/pypi/v/Latin-Lemmatizer.svg)

Custom tool for Latin text lemmatisation using CLTK

* [GitHub](https://github.com/mitchopt/Latin-Lemmatizer/) | [PyPI](https://pypi.org/project/Latin-Lemmatizer/) | [Documentation](https://mitchopt.github.io/Latin-Lemmatizer/)
* Created by [Mitchell G. Harris](https://github.com/mitchopt/) | GitHub [@mitchopt](https://github.com/mitchopt) | PyPI [@mitchopt](https://pypi.org/user/mitchopt/)
* MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://mitchopt.github.io/Latin-Lemmatizer/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/Latin-Lemmatizer.git
cd Latin-Lemmatizer

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `latin_lemmatizer`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

Latin Lemmatizer was created in 2026 by Mitchell G. Harris.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
