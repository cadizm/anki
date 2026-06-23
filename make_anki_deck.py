import argparse
import csv
import random

import genanki


def make_note(row):
    question = row["translation"]
    answer = f"{row['hiragana']} ({row['romaji']})"

    return genanki.Note(model=genanki.BASIC_MODEL, fields=[question, answer])


def make_deck(infile, title):
    DECK_ID = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(DECK_ID, title)

    with open(infile, "r", encoding="utf-8-sig") as csv_infile:
        reader = csv.DictReader(csv_infile)
        for row in reader:
            deck.add_note(make_note(row))

    return deck


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        required=True,
        action="store",
        help="CSV infile with columns: romaji, hiragana, translation",
    )
    parser.add_argument(
        "--deck-title", required=True, action="store", help="Title to use for Anki deck"
    )
    parser.add_argument(
        "--deck-filename",
        required=True,
        action="store",
        help="Filename to use for Anki deck (without extension)",
    )
    args = parser.parse_args()

    deck = make_deck(args.csv, args.deck_title)
    package_name = f"{args.deck_filename}.apkg"

    genanki.Package(deck).write_to_file(package_name)
    print(f"Generated {package_name}")
