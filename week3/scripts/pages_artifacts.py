"""Check or stage maintained static assets; never publish or copy private files."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ASSETS = (
    'index.html', 'app.mjs', 'engine.mjs', 'styles.css', 'fitness.json',
    'club-portal.html', 'class-booking.html', 'member-offers.html',
    'customer.mjs', 'customer.css', 'scenario.html', 'scenario.mjs',
    'identity.json', 'identity.css', 'avatar-avery.svg', 'icon-club.svg',
    'icon-booking.svg', 'icon-offers.svg', 'icon-recall.svg',
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=ROOT.parent / 'docs' / 'recall')
    parser.add_argument('--write', action='store_true', help='Stage reviewed public assets; does not push.')
    parser.add_argument('--check', action='store_true', help='Compare without writing.')
    args = parser.parse_args()
    if args.check and args.write:
        parser.error('Choose --check or --write.')
    args.write = not args.check
    changed = []
    for name in ASSETS:
        source, target = ROOT / 'site' / name, args.destination / name
        if not target.exists() or source.read_bytes() != target.read_bytes():
            changed.append(name)
            if args.write:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    if changed:
        print(('Staged: ' if args.write else 'Out of sync: ') + ', '.join(changed))
    else:
        print('Maintained Pages assets match the source.')
    # This fixture was never loaded by the fitness app. Remove only this known
    # obsolete public asset; leave unrelated destination files untouched.
    obsolete = args.destination / 'demo.json'
    if obsolete.exists():
        print(('Removed obsolete asset: ' if args.write else 'Obsolete asset: ') + 'demo.json')
        if args.write:
            obsolete.unlink()
        else:
            changed.append('demo.json')
    return 0 if args.write or not changed else 1


if __name__ == '__main__':
    raise SystemExit(main())
