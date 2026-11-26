"""Build the standalone offline HTML app AND the fast web/PWA dist/ bundle from the official English PDFs."""
import base64
import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#162236"/>
  <rect x="28" y="28" width="456" height="456" rx="72" fill="none" stroke="#ffd881" stroke-width="18"/>
  <text x="256" y="268" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="188" font-weight="700" fill="#f9fbff">TW</text>
  <path d="M128 344h256l-36 44H164z" fill="#ffd881"/>
</svg>
"""


def render_svg_png(svg_text, size, dest):
    import pymupdf as pdf
    doc = pdf.open(stream=svg_text.encode('utf-8'), filetype='svg')
    page = doc[0]
    scale = size / page.rect.width
    pix = page.get_pixmap(matrix=pdf.Matrix(scale, scale), alpha=True)
    pix.save(str(dest))
    doc.close()


def build_web_dist(banks, template):
    if DIST.exists():
        shutil.rmtree(DIST)
    data_dir = DIST / 'data'
    img_dir = DIST / 'assets' / 'img'
    data_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    prefix = 'data:image/png;base64,'
    img_count = 0
    for track_name, questions in banks.items():
        web_rows = []
        for q in questions:
            item = dict(q)
            web_imgs = []
            for idx, data_uri in enumerate(q['images']):
                assert data_uri.startswith(prefix), (track_name, q['id'], idx)
                raw = base64.b64decode(data_uri[len(prefix):])
                fname = f'{track_name}-{q["id"]}-{idx + 1}.png'
                (img_dir / fname).write_bytes(raw)
                web_imgs.append(f'assets/img/{fname}')
                img_count += 1
            item['images'] = web_imgs
            web_rows.append(item)
        (data_dir / f'{track_name}.json').write_text(
            json.dumps(web_rows, separators=(',', ':')), encoding='utf-8'
        )

    # Custom wayfinding icons (zero official government emblems)
    (DIST / 'favicon.svg').write_text(FAVICON_SVG, encoding='utf-8')
    render_svg_png(FAVICON_SVG, 192, DIST / 'icon-192.png')
    render_svg_png(FAVICON_SVG, 512, DIST / 'icon-512.png')

    web_head = (
        '<link rel="icon" type="image/svg+xml" href="./favicon.svg">\n'
        '<link rel="apple-touch-icon" href="./icon-192.png">\n'
        '<link rel="manifest" href="./manifest.json">'
    )
    web_html = (
        template
        .replace('<!--__WEB_HEAD__-->', web_head)
        .replace('__QUESTION_BANKS__', 'null')
    )
    (DIST / 'index.html').write_text(web_html, encoding='utf-8')

    manifest = {
        'name': 'Taiwan Driving Practice — English Foreigner Guide',
        'short_name': 'TW Driving',
        'description': 'Free 100% English study app and foreigner guide for Taiwan’s 2026 scooter and car driving tests.',
        'start_url': './',
        'scope': './',
        'display': 'standalone',
        'background_color': '#eef1f5',
        'theme_color': '#162236',
        'icons': [
            {'src': './icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': './icon-512.png', 'sizes': '512x512', 'type': 'image/png'}
        ]
    }
    (DIST / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    version = hashlib.sha256(
        (web_html + (data_dir / 'scooter.json').read_text(encoding='utf-8')).encode('utf-8')
    ).hexdigest()[:10]
    sw_js = f"""const CACHE = 'tw-driving-{version}';
const CORE = [
  './',
  './index.html',
  './manifest.json',
  './favicon.svg',
  './icon-192.png',
  './data/scooter.json',
  './data/car.json'
];

self.addEventListener('install', event => {{
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
}});

self.addEventListener('activate', event => {{
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener('fetch', event => {{
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  event.respondWith(
    caches.match(req).then(cached => cached || fetch(req).then(res => {{
      if (res.ok) {{
        const copy = res.clone();
        caches.open(CACHE).then(cache => cache.put(req, copy));
      }}
      return res;
    }}))
  );
}});
"""
    (DIST / 'sw.js').write_text(sw_js, encoding='utf-8')

    headers = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/data/*
  Cache-Control: public, max-age=86400

/sw.js
  Cache-Control: no-cache
"""
    (DIST / '_headers').write_text(headers, encoding='utf-8')
    (DIST / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
    print(f'dist/ web build ready: index.html ({len(web_html)//1024} KB), 2 JSON banks, {img_count} PNG illustrations, PWA icons & sw.js')


def import_bank(name, expected):
    import pymupdf as pdf

    rows = []
    current = None
    topic = 'Road rules and safety'
    with pdf.open(ROOT / (name + '.pdf')) as source:
        for page in source:
            previous = current
            anchors = []
            lines = [line.strip() for line in page.get_text().splitlines() if line.strip()]
            i = 0
            while i < len(lines):
                line = lines[i]
                i += 1
                if line.startswith('▸'):
                    topic = line[1:].strip()
                    continue
                if re.match(r'^(?:Automobile Written Exam|—\s*\d+\s*—|SECTION |Section \d|No\.|Ans$|An$|s$|Question(?: Content)?$)', line):
                    continue
                if line.isdecimal() and i < len(lines):
                    answer = re.fullmatch(r'\(?([123])\)?', lines[i])
                    if answer and int(line) == len(rows) + 1:
                        current = dict(id=int(line), answer=int(answer[1])-1, page=page.number+1,
                                       topic=topic, lines=[], images=[])
                        rows.append(current)
                        anchors.append(current)
                        i += 1
                        continue
                if current:
                    current['lines'].append(line)

            if not page.get_image_info():
                continue
            words = page.get_text('words')
            number_x = (75, 105) if name == 'scooter' else (60, 85)
            separators = sorted(set(
                draw['rect'].y0 for draw in page.get_drawings()
                if draw['rect'].width > 380 and draw['rect'].height < 1
                and (140 < draw['rect'].x0 < 144 if name == 'scooter' else 127 < draw['rect'].x0 < 130)
            ))
            for info in page.get_image_info():
                box = pdf.Rect(info['bbox'])
                mid = (box.y0 + box.y1) / 2
                low = max((y for y in separators if y < mid), default=0)
                high = min((y for y in separators if y > mid), default=page.rect.y1)
                ids = {int(word[4]) for word in words if number_x[0] < word[0] < number_x[1]
                       and low < (word[1]+word[3])/2 < high and word[4].isdecimal()}
                matches = [row for row in anchors if row['id'] in ids]
                if not matches and not ids and previous and anchors:
                    first_y = min((word[1] for word in words
                                   if word[4] == str(anchors[0]['id']) and number_x[0] < word[0] < number_x[1]),
                                  default=0)
                    if box.y1 < first_y:
                        matches = [previous]
                if len(matches) != 1:
                    raise ValueError((name, page.number+1, tuple(box), ids, low, high))
                picture = page.get_pixmap(matrix=pdf.Matrix(2, 2), clip=box)
                matches[0]['images'].append('data:image/png;base64,' +
                                             base64.b64encode(picture.tobytes()).decode())

    assert len(rows) == expected, (name, len(rows))
    return [parse_choices(row, name) for row in rows]


def clean_text(text):
    text = unicodedata.normalize('NFKC', text)
    # Remove Markdown escape backslashes from the official English scooter PDF (e.g., driver\'s, NT\$300, incorrect?\)
    text = re.sub(r'\\([\'\"$.,?!()\-])', r'\1', text)
    text = text.replace('\\', ' ')
    # Remove leftover Chinese parenthetical terms and full-width Chinese periods
    text = text.replace('(牽引)', '(being towed or pulled)')
    text = text.replace('。', '.')
    # Rejoin words split across PDF lines with a hyphen (e.g., "two- stage" -> "two-stage")
    text = re.sub(r'([A-Za-z]+)-\s+([a-z]+)', r'\1-\2', text)
    # Clean stray double periods and stray spaces inside quotes
    text = re.sub(r'\.\.(?!\.)', '.', text)
    text = re.sub(r'"\s+([^"]+?)\s+"', r'"\1"', text)
    text = re.sub(r'([A-Za-z0-9,])\s+"', r'\1"', text)
    text = ' '.join(text.split())
    return text


def classify_scooter_topic(prompt, choices, has_images):
    if has_images:
        return 'Traffic Signs & Road Markings'
    text = (prompt + ' ' + ' '.join(choices)).lower()
    if any(k in text for k in (
        'first aid', 'cpr', 'bleeding', 'fracture', 'burn', 'unconscious', 'breathing',
        'ambulance', 'rescue', 'injured', 'injury', 'patient', 'victim', 'accident', 'crash',
        'fire extinguisher', 'aed', 'shock', 'heartbeat', 'wound', 'emergency button'
    )):
        return 'Accidents, Emergencies & First Aid'
    if any(k in text for k in (
        'alcohol', 'drunk', 'breathalyzer', 'drug', 'intoxicated', 'mobile phone', 'cell phone',
        'texting', 'red light', 'fine', 'penalty', 'penalties', 'revoked', 'suspended', 'suspension',
        'revocation', 'violation', 'ticket', 'impound', 'demerit', 'points', 'criminal', 'drag racing',
        'dangerous driving', 'noise', 'illegal', 'prohibited'
    )):
        return 'Penalties, DUI & Prohibited Conduct'
    if any(k in text for k in (
        'license', 'licence', 'registration', 'plate', 'insurance', 'compulsory', 'inspection',
        'exam', 'written test', 'road test', 'lecture', 'age', 'renew', 'transfer', 'scrap',
        'ownership', 'address', 'change of', 'exhaust emission', 'certificate'
    )):
        return 'Licensing, Registration & Insurance'
    if any(k in text for k in (
        'helmet', 'cargo', 'carried', 'carrying', 'weight limit', 'width', 'height', 'passenger',
        'tire', 'tyre', 'brake', 'oil', 'chain', 'battery', 'headlight', 'taillight', 'turn signal',
        'horn', 'mirror', 'muffler', 'engine', 'fuel', 'eco-driving', 'maintenance', 'equipment',
        'shoe', 'clothing', 'reflective', 'lamp', 'light'
    )):
        return 'Helmets, Cargo & Bike Maintenance'
    if any(k in text for k in (
        'railway', 'railroad', 'level crossing', 'train', 'tunnel', 'bridge', 'freeway',
        'expressway', 'mountain', 'slope', 'curve', 'rain', 'fog', 'waterlogged', 'slippery',
        'night', 'wind', 'typhoon', 'flood', 'underpass', 'overpass', 'construction', 'gravel'
    )):
        return 'Weather, Railways & Special Roads'
    if any(k in text for k in (
        'intersection', 'two-stage', 'left turn', 'right turn', 'u-turn', 'turn', 'yield',
        'pedestrian', 'crosswalk', 'zebra', 'right-of-way', 'right of way', 'roundabout',
        'lane', 'overtake', 'overtaking', 'passing', 'parking', 'park', 'stop line', 'curb',
        'bus', 'school', 'blind spot', 'inner radius', 'large vehicle', 'truck', 'signal',
        'flashing', 'traffic light', 'sign', 'marking', 'sidewalk', 'alley'
    )):
        return 'Intersections, Turns & Right-of-Way'
    return 'Safe Riding & Road Rules'


def parse_choices(row, name):
    content = clean_text(' '.join(row.pop('lines')))
    options = re.search(r'^(.*?)\(\s*1\s*\)\s*(.*?)\(\s*2\s*\)\s*(.*?)\(\s*3\s*\)\s*(.*)$', content)
    if not options:
        raise ValueError((name, row['id'], content))
    row['prompt'] = clean_text(options[1])
    row['choices'] = [clean_text(options[i]) for i in (2, 3, 4)]
    if not row['prompt']:
        assert row['images'], (name, row['id'])
        row['prompt'] = 'What does this sign or illustration show?'
    assert all(row['choices']) or (not any(row['choices']) and len(row['images']) == 3), (name, row['id'])
    if name == 'scooter' and not row.get('video'):
        row['topic'] = classify_scooter_topic(row['prompt'], row['choices'], bool(row['images']))
    return row


def import_hazards(name, expected):
    import pymupdf as pdf

    rows, links = [], {}
    current = None
    with pdf.open(ROOT / (name + '-hazard.pdf')) as source:
        for page in source:
            for item in page.get_links():
                label = page.get_textbox(item['from']).strip()
                url = item.get('uri', '')
                if label.isdecimal() and url.startswith('https://space2.thb.gov.tw/'):
                    links[label] = url
            lines = [line.strip() for line in page.get_text().splitlines() if line.strip()]
            i = 0
            while i < len(lines):
                line = lines[i]
                i += 1
                number = len(rows) + 1
                width = 3 if name == 'scooter' else 2
                if line == str(number).zfill(width) and i < len(lines):
                    answer = re.fullmatch(r'\(?([123])\)?', lines[i])
                    if answer:
                        current = dict(id='video-' + str(number), answer=int(answer[1])-1,
                                       page=page.number+1, topic='Hazard perception videos', lines=[], images=[])
                        rows.append(current)
                        i += 1
                        continue
                if line in links:
                    assert current is not None and 'video' not in current, (name, line)
                    current['video'] = links[line]
                elif current and line not in {'Questi', 'on', 'Number', 'Answer', 'Question', 'Video'}:
                    if not (i == 1 and line == str(page.number+1)):
                        current['lines'].append(line)
    assert len(rows) == len(links) == expected, (name, len(rows), len(links))
    assert all('video' in row for row in rows), name
    return [parse_choices(row, name) for row in rows]


if __name__ == '__main__':
    banks = {name: import_bank(name, count) for name, count in [('scooter', 806), ('car', 1090)]}
    for name, bank in banks.items():
        print(name, len(bank), sum(bool(row['images']) for row in bank), 'illustrated')
    for name, count in [('scooter', 126), ('car', 10)]:
        banks[name].extend(import_hazards(name, count))
        print(name, count, 'linked hazard questions')
    template = (ROOT / 'app.html').read_text(encoding='utf-8')
    # 1. Standalone single-file offline HTML (double-click anywhere)
    inline_icon = '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + FAVICON_SVG.replace('\n', '').replace('#', '%23').replace('"', "'") + '">'
    payload = json.dumps(banks, separators=(',', ':')).replace('<', r'\u003c')
    standalone = template.replace('<!--__WEB_HEAD__-->', inline_icon).replace('__QUESTION_BANKS__', payload)
    (ROOT / 'Taiwan Driving Practice.html').write_text(standalone, encoding='utf-8')
    # 2. Fast production web + PWA bundle in dist/ (for Cloudflare Pages / GitHub Pages)
    build_web_dist(banks, template)

