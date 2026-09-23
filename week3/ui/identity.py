"""Shared presentation identities; data and SVG assets also serve the browser demo."""
import base64
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'site'
IDENTITIES = json.loads((ASSETS / 'identity.json').read_text())


def asset_url(name):
    return 'data:image/svg+xml;base64,' + base64.b64encode((ASSETS / name).read_bytes()).decode()


def app_identity(service):
    item = IDENTITIES[service]
    return (f'<span class="recall-app-identity" style="--identity-color:{item["color"]}">'
            f'<span class="recall-app-icon"><img src="{asset_url(item["icon"])}" alt=""></span>'
            f'<span class="identity-name">{item["name"]}</span></span>')


def persona():
    return (f'<div class="recall-persona"><img class="persona-avatar" src="{asset_url("avatar-avery.svg")}" alt="Illustration of Avery">'
            '<div><div class="persona-label">Fictional club member</div><div class="persona-name">Avery Example</div></div>'
            '<div class="persona-facts"><span class="persona-fact"><strong>INTEREST</strong>Evening yoga · after 6 pm</span>'
            '<span class="persona-fact"><strong>KEEP</strong>Paid Saturday strength class</span></div></div>')


def identity_css():
    return (ASSETS / 'identity.css').read_text()
