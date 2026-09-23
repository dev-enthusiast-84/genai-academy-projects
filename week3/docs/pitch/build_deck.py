"""Build the HTML pitch deck and speaker script; optionally export PDF with Chromium."""
from pathlib import Path
from html import escape
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ui.identity import app_identity, persona, identity_css, asset_url, IDENTITIES

OUT = Path(__file__).resolve().parent
SLIDES = [{'kicker': 'THE SETTING',
  'title': 'Meet Avery.\nOne fitness club. Three apps.',
  'subtitle': 'Avery is a fictional club member who shares an interest in evening yoga.',
  'cards': [('CLUB PORTAL',
             'Membership & interests',
             'Avery fills in a fitness questionnaire and agrees to share it.'),
            ('CLASS BOOKING',
             'Bookings & recommendations',
             'Uses shared interests to suggest yoga. Also holds a paid Saturday class.'),
            ('MEMBER OFFERS',
             'Personalized promotions',
             'Uses shared interests to prepare a yoga invitation.')],
  'band': 'Avery consents once. Their interests create saved information in all three apps.',
  'foot': 'Working demo: three local fitness apps with synthetic records. The invitation is a preview; no '
          'message is sent.',
  'cue': 'Introduce Avery as a person first. Explain what each app does before discussing withdrawal.',
  'script': 'Meet Avery, a member of a fitness club in our demo. Avery fills in a questionnaire in Club '
            'Portal and agrees to share an interest in evening yoga. Class Booking uses it to recommend '
            'classes. Member Offers prepares a yoga invitation. Avery also has a paid Saturday booking. '
            'Everything is useful—until Avery decides they no longer want that personalization.'},
 {'kicker': 'THE PROBLEM → RECALL',
  'title': 'Avery changes their mind.\nThe other apps still remember.',
  'subtitle': 'Recall is a separate privacy dashboard for withdrawing consent across these connected apps.',
  'cards': [('1 · INVESTIGATE',
             'Find the linked copies',
             'Discover records, trace their origins, inspect their state.'),
            ('2 · APPROVE', 'Review the exact scope', 'The member approves removal; the paid booking stays.'),
            ('3 · VERIFY',
             'Check the actual result',
             'Remove approved copies and issue a verification receipt.')],
  'band': 'Remove the shared interests, recommendation and invitation. Keep the paid booking.',
  'foot': 'Success target: 9/10 completable trials within 3 minutes, no unauthorized deletion, paid booking '
          'preserved. Not an established benchmark.',
  'cue': 'Pause after “the copies remain.” Introduce Recall explicitly as the fourth app: the privacy '
         'dashboard.',
  'script': 'Avery deletes the questionnaire, but the recommendation and invitation remain. The source is '
            'gone; the copies remain. Recall is our separate privacy dashboard for fixing that gap. Avery '
            'asks: stop using my yoga interests, but keep my paid class. Recall traces the linked records, '
            'presents a removal plan, waits for approval, and verifies the result across all three apps.'},
 {'kicker': 'THE PROMISE TO AVERY',
  'title': 'Stop personalization.\nKeep the membership working.',
  'subtitle': 'Withdrawing consent should change how interests are used without erasing the whole account.',
  'cards': [('REMOVE',
             'Shared interests & copies',
             'The yoga preferences, recommendation, audience label and invitation.'),
            ('PRESERVE',
             'The services Avery still wants',
             'Paid Saturday class, membership contact card and public class listings.'),
            ('PREVENT REUSE',
             'Keep withdrawn copies out',
             'Block the removed record IDs from returning through an old import.')],
  'band': 'Success means removing the right information—and proving the useful parts still work.',
  'foot': 'Scope: the recorded questionnaire and its linked records in this demo. Reuse blocks cover their '
          'stable IDs, not arbitrary external copies.',
  'cue': 'Emphasize the contrast between stopping personalization and keeping the paid class. These are the '
         'promises the final slide will verify.',
  'script': 'Avery is not asking to leave the club. They want three things: remove the shared interests and '
            'the recommendations built from them; keep the paid class and membership; and stop old copies '
            'coming back. Deleting everything would be easy to explain—and wrong. Recall has to make a '
            'precise change, then show that the rest still works.'},
 {'kicker': 'HOW IT WORKS',
  'title': 'Three agents. A separate judge.\nLangGraph coordinates the work.',
  'subtitle': 'Distinct model roles, sequential handoffs, and a human approval boundary.',
  'cards': [('1 · MODEL ROLES',
             'Investigate, review, judge, audit',
             'gpt-4.1-mini: investigator, reviewer, auditor.\ngpt-4.1: separate judge.'),
            ('2 · WORKFLOW CONTROL',
             'Review → approval → execution',
             'LangGraph routes review and bounded repairs.\nApplication approval is saved in SQLite.'),
            ('3 · CONNECTED SERVICES',
             'Club · Booking · Offers',
             'Each app owns a store.\nVerify absence; resume unfinished work.')],
  'band': 'A plan is not permission. Every write must match the member’s approved scope.',
  'foot': 'Agent = model role. Investigator selects read tools; reviewer and auditor assess supplied '
          'evidence. Judge uses a separate model. SQLite owns approval/recovery.',
  'cue': 'Introduce each model role along the diagram. Pause at Avery’s approval, then follow the return '
         'path through verification and the outcome auditor.',
  'script': 'That precision takes a team with distinct roles. The investigator agent traces copies. The '
            'scope reviewer checks what belongs in the plan. A separate judge model challenges it. LangGraph '
            'coordinates those handoffs and bounded repairs. Avery alone approves the writes. After '
            'execution, service checks feed the outcome auditor agent. SQLite saves approval and progress, '
            'so interrupted work can resume.',
  'diagram': True},
 {'kicker': 'THE DEMONSTRATED RESULT',
  'title': 'Copies removed.\nPaid booking preserved.',
  'subtitle': 'The same Avery story, checked before, after, and on replay.',
  'cards': [('1 · BEFORE',
             'Copies survive source deletion',
             'The yoga recommendation and invitation remain.'),
            ('2 · AFTER APPROVAL',
             '7 targets verified absent',
             'Includes the source deleted earlier.\nThe paid Saturday booking remains confirmed.'),
            ('3 · REPLAY',
             'Old import is blocked',
             'The withdrawn preference record cannot return through the tested replay path.')],
  'band': 'A privacy choice becomes a visible change across apps, with a receipt.',
  'foot': 'Demonstrated on synthetic local stores. Other sectors require new integrations; this is not '
          'universal external-data deletion.',
  'cue': 'Connect the result back to Avery’s original request. Pause on the preserved booking, then close '
         'with the benefit.',
  'script': 'Now Avery’s request has a visible result. The recommendation and invitation disappear. Seven '
            'targets are verified absent, including the questionnaire deleted earlier. The paid Saturday '
            'class remains confirmed. An old import tries to restore a withdrawn preference; it is blocked. '
            'Avery can change their privacy choice without losing the service they paid for. That is Recall: '
            'consent with an undo button.'}]


def architecture_diagram():
    diagram = '''<div class="architecture">
<svg viewBox="0 0 1200 365" role="img" aria-labelledby="architecture-title architecture-description">
<title id="architecture-title">Three agent roles and a separate judge orchestrated by LangGraph</title>
<desc id="architecture-description">LangGraph review graph routes the request sequentially to the investigator agent, scope reviewer agent, and a different judge model. Review findings can trigger at most two repairs. A human approves the exact scope outside the graph. LangGraph execution calls the guarded executor and verification/audit; the three app stores supply fresh verification evidence to the outcome auditor agent. SQLite retains approval and progress. Model roles have no write authority.</desc>
<defs><marker id="flow-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#52677B" stroke-width="1.4"/></marker></defs>
<rect x="125" y="4" width="640" height="170" rx="8" fill="#E8F3F3" stroke="#087F8C" stroke-width="2"/>
<text x="445" y="28" class="diagram-label">LANGGRAPH ORCHESTRATION · REVIEW GRAPH</text>
<rect x="2" y="58" width="99" height="90" rx="6" fill="#fff" stroke="#CCDCE9"/>
<text x="51" y="76" class="diagram-label">REQUEST</text><image href="AVERY_IMAGE" x="32" y="84" width="38" height="38"/><text x="51" y="141" class="diagram-copy">Avery · Streamlit</text>
<rect x="143" y="45" width="180" height="95" rx="6" fill="#fff" stroke="#087F8C"/>
<text x="233" y="68" class="diagram-label agent-label">AGENT 1 · INVESTIGATOR</text><text x="233" y="95" class="diagram-title">Find &amp; trace copies</text><text x="233" y="120" class="diagram-copy">gpt-4.1-mini · read tools</text>
<rect x="354" y="45" width="180" height="95" rx="6" fill="#fff" stroke="#087F8C"/>
<text x="444" y="68" class="diagram-label agent-label">AGENT 2 · SCOPE REVIEWER</text><text x="444" y="95" class="diagram-title">Check the scope</text><text x="444" y="120" class="diagram-copy">gpt-4.1-mini · evidence</text>
<rect x="565" y="45" width="180" height="95" rx="6" fill="#EEF0FC" stroke="#666C9C"/>
<text x="655" y="68" class="diagram-label">SEPARATE LLM JUDGE</text><text x="655" y="95" class="diagram-title">Challenge the plan</text><text x="655" y="120" class="diagram-copy">gpt-4.1 · different model</text>
<g fill="none" stroke="#52677B" stroke-width="2" marker-end="url(#flow-arrow)">
<path d="M101 100 H141"/><path d="M323 92 H352"/><path d="M534 92 H563"/>
<path d="M655 141 V155 H233 V142"/>
<path d="M765 93 H799"/><path d="M978 93 H1010"/>
<path d="M1101 149 V235"/><path d="M1000 280 H937"/>
<path d="M737 280 H672"/><path d="M432 280 H366"/>
</g>
<text x="444" y="169" class="diagram-copy">Review findings → at most 2 repair rounds</text>
<rect x="800" y="45" width="178" height="105" rx="6" fill="#FFF0D4" stroke="#AB751A" stroke-width="2"/>
<text x="889" y="68" class="diagram-label">HUMAN APPROVAL</text><text x="889" y="98" class="diagram-title">Avery approves</text><text x="889" y="128" class="diagram-copy">Exact scope · outside graph</text>
<rect x="1012" y="45" width="184" height="105" rx="6" fill="#17324D"/>
<text x="1104" y="69" class="diagram-label inverse">CODE · GUARDED WRITE</text><text x="1104" y="99" class="diagram-title inverse">Executor</text><text x="1104" y="127" class="diagram-copy inverse">Approved records only</text>
<text x="798" y="209" class="diagram-label">LANGGRAPH EXECUTION GRAPH · EXECUTE → VERIFY / AUDIT</text>
<rect x="1000" y="237" width="196" height="89" rx="6" fill="#fff" stroke="#CCDCE9"/>
<text x="1098" y="256" class="diagram-label">THREE APP STORES</text>APP_STORE_ICONS
<rect x="737" y="237" width="199" height="89" rx="6" fill="#fff" stroke="#CCDCE9"/>
<text x="836" y="259" class="diagram-label">CODE · VERIFICATION</text><text x="836" y="285" class="diagram-title">Independent checks</text><text x="836" y="310" class="diagram-copy">Absence · preserved booking</text>
<rect x="432" y="237" width="239" height="89" rx="6" fill="#E8F3F3" stroke="#087F8C" stroke-width="2"/>
<text x="551" y="259" class="diagram-label agent-label">AGENT 3 · OUTCOME AUDITOR</text><text x="551" y="285" class="diagram-title">Assess the actual result</text><text x="551" y="310" class="diagram-copy">gpt-4.1-mini · cannot override failures</text>
<rect x="176" y="237" width="189" height="89" rx="6" fill="#fff" stroke="#087F8C"/>
<text x="270" y="266" class="diagram-title">Receipt</text><text x="270" y="294" class="diagram-copy">Verified or unresolved</text>
<text x="686" y="356" class="diagram-copy">SQLITE WORKFLOW STATE · exact approval · versions · progress · bounded retries</text>
</svg>
<ol class="architecture-mobile"><li><strong>LangGraph review graph:</strong> investigator agent → scope reviewer agent → separate judge model. Up to two repair rounds.</li><li><strong>Avery approves the exact scope.</strong> No agent can approve writes.</li><li><strong>LangGraph execution graph:</strong> guarded executor → service verification → outcome auditor agent.</li><li>Three HTTP app stores; SQLite workflow state saves approval and progress. Receipt reports verified or unresolved.</li></ol>
</div>'''
    badges = ''
    for x, service, label in [(1032, 'documents', 'Club'), (1098, 'search', 'Booking'), (1164, 'personalization', 'Offers')]:
        item = IDENTITIES[service]
        badges += (f'<rect x="{x-15}" y="267" width="30" height="30" rx="7" fill="{item["color"]}"/>'
                   f'<image href="{asset_url(item["icon"])}" x="{x-12}" y="270" width="24" height="24"/>'
                   f'<text x="{x}" y="315" class="diagram-copy">{label}</text>')
    return diagram.replace('AVERY_IMAGE', asset_url('avatar-avery.svg')).replace('APP_STORE_ICONS', badges)


def build_html():
    sections = []
    for i, s in enumerate(SLIDES):
        cards = ''.join(f'<article><small>{escape(k)}</small><h2>{escape(t)}</h2><p>{escape(b).replace(chr(10), "<br>")}</p></article>' for k,t,b in s['cards'])
        if i == 0:
            cards = ''.join(f'<article style="border-color:{color}">{app_identity(service)}<h2>{escape(title)}</h2><p>{escape(copy)}</p></article>'
                            for service, color, (_, title, copy) in zip(
                                ['documents', 'search', 'personalization'], ['#984b32', '#215446', '#69445e'], s['cards']))
            body = persona() + f'<div class="cards">{cards}</div>'
        else:
            body = architecture_diagram() if s.get("diagram") else f'<div class="cards">{cards}</div>' 
        sections.append(f'<section class="slide" id="slide-{i+1}" aria-label="Slide {i+1}"><header>RECALL <span>{escape(s["kicker"])}</span></header><h1>{escape(s["title"]).replace(chr(10), "<br>")}</h1><p class="subtitle">{escape(s["subtitle"])}</p>{body}<div class="band">{escape(s["band"])}</div><footer>{escape(s["foot"])}<b>{i+1} / 5</b></footer></section>')
    css = '''*{box-sizing:border-box} :root{--ink:#17324D;--paper:#F3F7FB;--blue:#275DAD;--teal:#087F8C;--muted:#52677B;--line:#CCDCE9} body{margin:0;background:var(--paper);color:var(--ink);font-family:Calibri,"Segoe UI",Arial,sans-serif} .slide{max-width:1440px;min-height:100vh;margin:auto;padding:4vh 5vw;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid var(--line)} header{font-weight:800;letter-spacing:.17em;color:var(--blue);display:flex;justify-content:space-between;font-size:14px}header span{color:var(--muted);font-weight:500}h1{font-family:Georgia,serif;font-size:clamp(36px,4.2vw,64px);font-weight:400;line-height:1.08;letter-spacing:-.03em;margin:3vh 0 1.5vh}.subtitle{font-size:clamp(17px,1.5vw,24px);margin:0 0 3vh;color:var(--muted)}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}article{background:white;border-top:5px solid var(--teal);padding:24px;min-height:195px}small{font-size:12px;font-weight:bold;letter-spacing:.07em;color:var(--teal)}h2{font-size:clamp(20px,1.9vw,29px);line-height:1.12;font-weight:600;margin:19px 0 13px}article p{font-size:clamp(17px,1.4vw,22px);line-height:1.4;margin:0;color:var(--muted)}.band{margin-top:24px;background:var(--ink);color:white;padding:19px 23px;font-size:clamp(17px,1.5vw,23px)}footer{font-size:12px;line-height:1.4;display:flex;gap:24px;justify-content:space-between;margin-top:20px;color:var(--muted)}footer b{white-space:nowrap}nav{position:fixed;bottom:12px;right:18px;display:flex;gap:6px}button{border:1px solid var(--line);background:white;color:var(--ink);padding:9px 15px;cursor:pointer;border-radius:5px}button:focus-visible{outline:3px solid var(--teal)}body.presenting .slide{display:none}body.presenting .slide.active{display:flex}#notes{position:fixed;inset:auto 5vw 65px;background:white;border:2px solid var(--teal);padding:22px;max-height:35vh;overflow:auto;box-shadow:0 8px 30px #17324d33;line-height:1.6} @media(max-width:700px){.slide{padding:35px 22px;min-height:100vh}.cards{grid-template-columns:1fr}article{min-height:0}header{gap:20px;font-size:11px}h1{margin-top:30px}.band{margin-top:15px}footer{padding-bottom:40px}}@media print{@page{size:landscape;margin:0}.slide,body.presenting .slide{display:flex!important;height:100vh;min-height:0;break-after:page;padding:25px 40px}.slide:last-of-type{break-after:auto}h1{font-size:40px}article{min-height:170px;padding:18px}article p{font-size:16px}h2{font-size:22px}nav,#notes{display:none!important}.band{font-size:18px}footer{font-size:10px}}'''
    css += '''.architecture svg{width:100%;height:auto;display:block}.architecture text{font-family:Calibri,"Segoe UI",Arial,sans-serif;text-anchor:middle;fill:#17324D}.architecture .diagram-label{font-size:12px;font-weight:700;letter-spacing:.4px}.architecture .diagram-title{font-size:18px;font-weight:600}.architecture .diagram-copy{font-size:12px;fill:#52677B}.architecture .agent-label{fill:#087F8C}.architecture .inverse{fill:white}.architecture-mobile{display:none}@media screen and (max-width:700px){.architecture svg{display:none}.architecture-mobile{display:block;padding-left:25px;line-height:1.7}.architecture-mobile li{padding:7px 0}}@media print{.architecture svg{display:block;max-height:270px}.architecture-mobile{display:none}}'''
    css += identity_css()
    css += '#slide-1 h1{font-size:48px;margin:16px 0 10px}#slide-1 .subtitle{margin-bottom:4px}#slide-1 article{padding:18px;min-height:170px}#slide-1 article h2{font-size:24px;margin:12px 0}#slide-1 article p{font-size:18px}#slide-1 .band{margin-top:16px}@media print{#slide-1 h1{font-size:36px}#slide-1 article p{font-size:15px}#slide-1 article h2{font-size:20px}#slide-1 .recall-persona{margin:8px 0 12px;padding:8px 14px}}'
    scripts = json.dumps([s['script'] for s in SLIDES])
    js = '''const slides=[...document.querySelectorAll('.slide')];let index=0;const notes=document.querySelector('#notes');function show(n){index=Math.max(0,Math.min(slides.length-1,n));document.body.classList.add('presenting');slides.forEach((s,i)=>s.classList.toggle('active',i===index));notes.textContent=scripts[index];document.querySelector('#prev').disabled=index===0;document.querySelector('#next').disabled=index===slides.length-1;}document.querySelector('#prev').onclick=()=>show(index-1);document.querySelector('#next').onclick=()=>show(index+1);document.querySelector('#toggle').onclick=()=>{notes.hidden=!notes.hidden;notes.textContent=scripts[index]};document.querySelector('#all').onclick=()=>{document.body.classList.remove('presenting');notes.hidden=true};document.addEventListener('keydown',e=>{if(e.target.tagName==='BUTTON')return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(index+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(index-1)}if(e.key.toLowerCase()==='n')document.querySelector('#toggle').click();if(e.key==='Escape')document.querySelector('#all').click()});show(0);'''
    (OUT/'recall-pitch.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Recall — Consent has an undo button</title><style>'+css+'</style><main>'+''.join(sections)+'</main><aside id="notes" hidden aria-live="polite"></aside><nav aria-label="Presentation controls"><button id="prev" aria-label="Previous slide">←</button><button id="next" aria-label="Next slide">→</button><button id="toggle">Script (N)</button><button id="all">All slides</button></nav><script>const scripts='+scripts+';'+js+'</script></html>')


def build_script():
    words=sum(len(slide['script'].split()) for slide in SLIDES)
    content=(f'# Recall — two-minute recording script\n\n{words} spoken words. '
             'Budget 110 seconds for narration and 10 seconds for slide changes. '
             'Use the quoted narration as a conversational guide, not text to recite mechanically. Pause at the story beats; the delivery cues are not spoken.\n')
    elapsed = 0
    def clock(seconds):
        return f'{seconds // 60}:{seconds % 60:02d}'
    for i, slide in enumerate(SLIDES):
        start = round(elapsed)
        elapsed += 110 * len(slide['script'].split()) / words + 2
        end = round(elapsed)
        title = slide['title'].replace('\n', ' ')
        content += (f'\n## Slide {i+1} · {clock(start)}–{clock(end)} · {title}\n\n'
                    f"**Delivery cue:** {slide['cue']}\n\n> {slide['script']}\n")
    existing = (OUT/'speaker-script.md').read_text() if (OUT/'speaker-script.md').exists() else ''
    if '## Presenter checks' in existing:
        content += '\n## Presenter checks' + existing.split('## Presenter checks', 1)[1]
    (OUT/'speaker-script.md').write_text(content)


def build_pdf():
    """Optional local Chromium export; install requirements-browser.txt first."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            page.goto((OUT / 'recall-pitch.html').as_uri())
            page.pdf(path=str(OUT / 'recall-pitch-deck.pdf'),
                     print_background=True, prefer_css_page_size=True)
        finally:
            browser.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true', help='Also export PDF using local Playwright Chromium.')
    args = parser.parse_args()
    build_html();build_script()
    if args.pdf:
        build_pdf()
    print('Built 5-slide HTML deck and timed speaker script' + (' and PDF.' if args.pdf else '.'))
