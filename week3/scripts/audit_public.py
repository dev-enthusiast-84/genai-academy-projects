"""Read-only public-page audit; isolated browser state, no model calls or writes."""
import argparse
import json
import hashlib
from pages_artifacts import ASSETS, ROOT
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://dev-enthusiast-84.github.io/genai-academy-projects/recall/')
    parser.add_argument('--output', type=Path, default=Path('docs/audit/public-observation.json'))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        observations = []
        for name in ['index.html', 'club-portal.html', 'class-booking.html', 'member-offers.html', 'scenario.html']:
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            response = page.goto(args.url.rstrip('/') + '/' + name)
            page.wait_for_load_state('networkidle')
            row = {'page': name, 'status': response.status, 'title': page.title(), 'errors': errors}
            if name == 'index.html':
                page.locator('#settings-open').click()
                row['providers'] = page.locator('#provider option').all_text_contents()
                row['embedded_customer_apps'] = page.locator('#connected-apps iframe').count()
                page.keyboard.press('Escape')
                page.screenshot(path=str(args.output.with_suffix('.png')), full_page=True)
            page.set_viewport_size({'width': 390, 'height': 844})
            row['mobile_overflow'] = page.evaluate('document.documentElement.scrollWidth > innerWidth')
            observations.append(row)
            page.close()
        assets = []
        for name in ASSETS:
            response = context.request.get(args.url.rstrip('/') + '/' + name)
            current = response.body()
            assets.append({'asset': name, 'status': response.status,
                           'matches_source': current == (ROOT / 'site' / name).read_bytes(),
                           'sha256': hashlib.sha256(current).hexdigest()})
        browser.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'url': args.url, 'observations': observations, 'assets': assets}, indent=2) + '\n')
    print(json.dumps(observations, indent=2))


if __name__ == '__main__':
    main()
