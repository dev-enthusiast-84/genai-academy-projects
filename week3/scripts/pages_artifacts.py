"""Copy public app assets to the repository's GitHub Pages directory."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site'
DESTINATION = ROOT.parent / 'docs' / 'recall'
PUBLIC_SUFFIXES = {'.html', '.css', '.mjs', '.json'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report missing or outdated artifacts without writing.')
    args = parser.parse_args()
    assets = sorted(path for path in SOURCE.iterdir() if path.is_file() and path.suffix in PUBLIC_SUFFIXES)
    stale = [path for path in assets if not (DESTINATION / path.name).is_file()
             or path.read_bytes() != (DESTINATION / path.name).read_bytes()]
    if args.check:
        for path in stale:
            print(f'Missing or outdated: docs/recall/{path.name}')
        if not stale:
            print(f'All {len(assets)} GitHub Pages artifacts match site/.')
        return bool(stale)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for path in stale:
        shutil.copyfile(path, DESTINATION / path.name)
        print(f'Updated docs/recall/{path.name}')
    print(f'{len(assets)} public artifacts ready; review and commit docs/recall/ before publishing.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
