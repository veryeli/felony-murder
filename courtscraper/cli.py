"""This module provides the RP To-Do CLI."""
# rptodo/cli.py
from typing import Optional

import typer

from courtscraper.ny.scrape import run_scraper
from courtscraper.ny.doccs_foil_text_to_xlsx import txt_to_xlsx
from courtscraper import __app_name__, __version__

app = typer.Typer()

@app.command(name="scrape")
def scrape() -> None:
    """Run the scraper."""
    print('scraping')
    run_scraper()

@app.command(name="parse-doccs-foil")
def parse_doccs_foil() -> None:
    """Parse the DOCCS FOIL data."""
    print('parsing')
    txt_to_xlsx()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return