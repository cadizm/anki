import argparse
import csv
import random
import re
import unicodedata

import genanki

from text_to_speech import text_to_speech


def normalized_ascii(romaji):
    text = "_".join(romaji.split())
    text = re.sub(r"[\[\]\|\-\~,]", "", text)
    text = re.sub(r"\.+", ".", text)
    normalized = unicodedata.normalize("NFKD", text)

    return normalized.encode("ascii", errors="ignore").decode("ascii")


def make_media_model():
    return genanki.Model(
        2115324838,  # random.randrange(1 << 30, 1 << 31)
        "Model with Answer Audio",
        fields=[
            {"name": "QuestionText"},
            {"name": "AnswerText"},
            {"name": "AnswerAudio"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": """
                    <div style="font-size: 24px; text-align: center;">{{QuestionText}}</div>
                """,
                "afmt": """
                    {{FrontSide}}
                    <hr id="answer">
                    <div style="font-size: 24px; text-align: center; color: green;">{{AnswerText}}</div>
                    {{#AnswerAudio}}
                        {{AnswerAudio}}
                    {{/AnswerAudio}}
                """,
            },
        ],
        css="""
            .card { font-family: arial; text-align: center; color: black; background-color: white; }
            img { max-width: 300px; height: auto; border-radius: 8px; }
        """,
    )


def make_note(model, row, audio_filename):
    question = row["translation"]
    answer = f"{row['hiragana']} ({row['romaji']})"
    return genanki.Note(
        model=model,
        fields=[
            question,
            answer,
            f"[sound:{audio_filename}]",
        ],
    )


def make_deck(csv_infile, title):
    DECK_ID = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(DECK_ID, title)
    model = make_media_model()

    with open(csv_infile, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            audio_filename = normalized_ascii(f"{row['romaji']}.mp3")
            deck.add_note(make_note(model, row, audio_filename))

    return deck


def make_audio_files(infile, audio_dir):
    audio_files = []
    with open(infile, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            audio_filename = normalized_ascii(f"{row['romaji']}.mp3")
            answer_audio = text_to_speech(
                row["hiragana"], f"{audio_dir}/{audio_filename}"
            )
            audio_files.append(answer_audio)

    return audio_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        required=True,
        action="store",
        help="CSV infile with columns: romaji, hiragana, translation",
    )
    parser.add_argument(
        "--audio-dir",
        required=True,
        action="store",
        help="Directory to store generated audio (must already exist)",
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
    package = genanki.Package(deck)
    package.media_files = make_audio_files(args.csv, args.audio_dir)
    package.write_to_file(f"{args.deck_filename}.apkg")
    print(f"Done.")
