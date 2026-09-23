"""Browser regression: python3 tests/embedded_apps.py (requires Playwright Chromium)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    root = Path(__file__).resolve().parents[1]
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(root / 'site')))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 1000})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('dialog', lambda dialog: dialog.accept())
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            expect(page.locator('#connected-apps iframe')).to_have_count(3)
            club = page.frame_locator('iframe[title="Club Portal customer app"]')
            booking = page.frame_locator('iframe[title="Class Booking customer app"]')
            offers = page.frame_locator('iframe[title="Member Offers customer app"]')
            expect(booking.locator('.empty')).to_contain_text('No personalized suggestions yet')
            expect(offers.locator('.empty')).to_contain_text('No personalized invitation yet')
            club.locator('#agree').check()
            club.locator('#grant').click()
            expect(booking.locator('.recommendation')).to_contain_text('Evening yoga')
            expect(offers.locator('.invitation')).to_contain_text('yoga invitation')
            expect(page.locator('#consent-summary')).to_contain_text('Sharing consent active')
            club.locator('#delete-source').click()
            expect(club.get_by_role('heading', name='Your questionnaire is deleted.')).to_be_visible()
            expect(booking.locator('.recommendation')).to_be_visible()
            expect(offers.locator('.invitation')).to_be_visible()
            # The embedded link scrolls to Recall without navigating or reloading it.
            page.evaluate('window.navigationCheck = true')
            club.locator('.recall-link').first.click()
            expect(page.locator('#request')).to_be_focused()
            assert page.evaluate('window.navigationCheck') is True
            page.locator('#rehearse').click()
            page.locator('#consent').check()
            page.locator('#approve').click()
            expect(page.locator('#notice')).to_contain_text('Withdrawal verified')
            expect(booking.locator('.empty')).to_contain_text('Personalized recommendations removed')
            expect(offers.locator('.empty')).to_contain_text('removed')
            expect(booking.locator('.booking-ticket')).to_contain_text('PAID · CONFIRMED')
            expect(club.get_by_role('heading', name='Sharing consent withdrawn.')).to_be_visible()
            page.locator('#reset').click()
            expect(club.locator('#agree')).to_be_visible()
            expect(booking.locator('.empty')).to_contain_text('No personalized suggestions yet')
            expect(offers.locator('.empty')).to_contain_text('No personalized invitation yet')
            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            frames = page.locator('#connected-apps iframe')
            boxes = [frames.nth(i).bounding_box() for i in range(3)]
            assert all(boxes[i + 1]['y'] > boxes[i]['y'] + boxes[i]['height'] for i in range(2))
            assert not errors, errors
            browser.close()
            print('Embedded apps: consent, deletion, withdrawal, reset, and mobile layout passed.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    main()
