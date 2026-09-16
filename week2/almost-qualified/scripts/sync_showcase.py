"""Copy only reviewed public HTML assets into the repository's GitHub Pages tree."""
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPOSITORY = PROJECT.parents[1]
DESTINATION = REPOSITORY / "docs" / "almost-qualified"
GITHUB = "https://github.com/dev-enthusiast-84/genai-academy-projects/blob/main"


def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    showcase = (PROJECT / "site" / "index.html").read_text(encoding="utf-8")
    showcase = showcase.replace('href="../docs/pitch_deck.html"', 'href="pitch_deck.html"')
    deck = (PROJECT / "docs" / "pitch_deck.html").read_text(encoding="utf-8")
    deck = deck.replace(
        'href="../../project-handout/',
        f'href="{GITHUB}/week2/project-handout/',
    )
    for name, content in (("index.html", showcase), ("pitch_deck.html", deck)):
        destination = DESTINATION / name
        destination.write_text(content, encoding="utf-8")
        print(f"Updated {destination.relative_to(REPOSITORY)}")


if __name__ == "__main__":
    main()
