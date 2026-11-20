"""Consulta a listagem pública de boletins diários da ANA."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlparse
from fontes_https import open_official

INDEX = 'https://www.gov.br/ana/pt-br/sala-de-situacao/sao-francisco/sao-francisco-boletim-diario'
PREFIX = '/ana/pt-br/sala-de-situacao/sao-francisco/boletins/diario/'
DATE_LABEL = re.compile(r'\d{2}[./-]\d{2}[./-]\d{4}')


class BulletinLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchor = None
        self.parts = []
        self.items = {}

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        url = urljoin(INDEX, dict(attrs).get('href') or '')
        parts = urlparse(url)
        if (parts.scheme == 'https' and parts.netloc == 'www.gov.br'
                and parts.path.startswith(PREFIX) and parts.path.endswith('.pdf')):
            self.anchor = url
            self.parts = []

    def handle_data(self, data):
        if self.anchor:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag != 'a' or not self.anchor:
            return
        label = DATE_LABEL.search(' '.join(self.parts))
        if label:
            try:
                date = datetime.strptime(re.sub(r'[/-]', '.', label.group()), '%d.%m.%Y').date()
                self.items.setdefault(date, self.anchor)
            except ValueError:
                pass
        self.anchor = None


def parse_bulletins(html):
    parser = BulletinLinks()
    parser.feed(html)
    if not parser.items:
        raise ValueError('A página da ANA não retornou links datados de boletins.')
    return sorted(parser.items.items(), reverse=True)[:5]


def fetch_bulletins():
    with open_official(INDEX, timeout=12) as response:
        html = response.read().decode('utf-8', errors='replace')
    return parse_bulletins(html), datetime.now(timezone.utc)


def saved_bulletins():
    """Lista de lançamento obtida diretamente do índice da ANA."""
    import json
    from datetime import date
    from pathlib import Path

    path = Path(__file__).resolve().parent / 'assets' / 'boletins_ana.json'
    snapshot = json.loads(path.read_text(encoding='utf-8'))
    records = [(date.fromisoformat(day), url) for day, url in snapshot['records']]
    return records, datetime.fromisoformat(snapshot['checked'])
