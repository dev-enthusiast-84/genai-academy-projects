"""Keep maintained documentation links and the public asset boundary reviewable."""
from pathlib import Path
import re
from urllib.parse import unquote
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def test_relative_documentation_links_resolve():
    sources = [*ROOT.glob('*.md'), ROOT / 'site/README.md',
               *(ROOT / 'docs').rglob('*.md'), *(ROOT / 'data').rglob('*.md')]
    missing = []
    for source in sources:
        for target in re.findall(r'\]\(([^\s)]+)\)', source.read_text()):
            if ':' in target or target.startswith('#'):
                continue
            relative = unquote(target.split('#', 1)[0])
            if not (source.parent / relative).exists():
                missing.append(f'{source.relative_to(ROOT)}: {target}')
    assert not missing, missing


def test_public_asset_allowlist_excludes_private_and_unused_files():
    spec = importlib.util.spec_from_file_location('pages_assets', ROOT / 'scripts/pages_artifacts.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert all((ROOT / 'site' / name).is_file() for name in module.ASSETS)
    assert not {'demo.json', '.env', 'README.md'} & set(module.ASSETS)
    assert all('/' not in name and not name.startswith('.') for name in module.ASSETS)
