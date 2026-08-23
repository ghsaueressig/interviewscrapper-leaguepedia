from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_metadata import get_youtube_metadata
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import unicodedata
from collections import defaultdict

MAX_URLS_PER_REQUEST = 10

app = Flask(__name__)
CORS(app)

TEAM_MAP = {
    'pain': 'paiN Gaming',
    'los': 'LOS',
    'loud': 'LOUD',
    'furia': 'FURIA',
    'red': 'RED Canids',
    'vks': 'Vivo Keyd Stars',
    'fx': 'Fluxo W7M',
    'fluxo': 'Fluxo W7M',
    'fxw7m': 'Fluxo W7M',
    'w7m': 'Fluxo W7M',
    'lev': 'Leviatán'
}

PLAYER_DATA = {
    'zothve': {'wiki': 'Zothve', 'team': 'Fluxo W7M'},
    'peach': {'wiki': 'Peach (Lee Min-gyu)', 'team': 'Fluxo W7M'},
    'cody': {'wiki': 'Cody', 'team': 'Fluxo W7M'},
    'bao': {'wiki': 'BAO (Jeong Hyeon-woo)', 'team': 'Fluxo W7M'},
    'momochi': {'wiki': 'Momochi', 'team': 'Fluxo W7M'},
    'guchi': {'wiki': 'Guchi', 'team': 'Fluxo W7M'},
    'nothing': {'wiki': 'Nothing', 'team': 'Fluxo W7M'},
    'guigo': {'wiki': 'Guigo', 'team': 'FURIA'},
    'tatu': {'wiki': 'Tatu (Pedro Seixas)', 'team': 'FURIA'},
    'tutsz': {'wiki': 'Tutsz', 'team': 'FURIA'},
    'ayu': {'wiki': 'Ayu (Andrey Saraiva)', 'team': 'FURIA'},
    'jojo': {'wiki': 'JoJo (Gabriel Dzelme)', 'team': 'FURIA'},
    'furyz': {'wiki': 'Furyz', 'team': 'FURIA'},
    'luuukz': {'wiki': 'Luuukz', 'team': 'FURIA'},
    'lanterninho': {'wiki': 'Lanterninho', 'team': 'FURIA'},
    'devost': {'wiki': 'Devost', 'team': 'Leviatán'},
    'booki': {'wiki': 'Booki', 'team': 'Leviatán'},
    'enga': {'wiki': 'Enga', 'team': 'Leviatán'},
    'strensh': {'wiki': 'Strensh', 'team': 'Leviatán'},
    'shiku': {'wiki': 'Shiku', 'team': 'Leviatán'},
    'kouke': {'wiki': 'Kouke', 'team': 'Leviatán'},
    'lautaloval': {'wiki': 'LautaLoval', 'team': 'Leviatán'},
    'xyno': {'wiki': 'Xyno', 'team': 'LOUD'},
    'sinatra': {'wiki': 'Sinatra', 'team': 'LOUD'},
    'kaze': {'wiki': 'Kaze (Lucas Fe)', 'team': 'LOUD'},
    'rabelo': {'wiki': 'Rabelo', 'team': 'LOUD'},
    'uzent': {'wiki': 'uZent', 'team': 'LOUD'},
    'raise': {'wiki': 'Raise', 'team': 'LOUD'},
    'sephis': {'wiki': 'Sephis', 'team': 'LOUD'},
    'zest': {'wiki': 'Zest (Kim Dong-min)', 'team': 'LOS'},
    'curse': {'wiki': 'Curse (Raí Yamada)', 'team': 'LOS'},
    'feisty': {'wiki': 'Feisty', 'team': 'LOS'},
    'duduhh': {'wiki': 'Duduhh', 'team': 'LOS'},
    'ackerman': {'wiki': 'Ackerman (Gabriel Aparicio)', 'team': 'LOS'},
    'enatron': {'wiki': 'Enatron', 'team': 'LOS'},
    'invokid': {'wiki': 'Invokid', 'team': 'LOS'},
    'brandao': {'wiki': 'Brandão', 'team': 'LOS'},
    'boal': {'wiki': 'Boal', 'team': 'paiN Gaming'},
    'cariok': {'wiki': 'Cariok', 'team': 'paiN Gaming'},
    'keine': {'wiki': 'Keine', 'team': 'paiN Gaming'},
    'hena': {'wiki': 'Hena', 'team': 'paiN Gaming'},
    'ceos': {'wiki': 'Ceos', 'team': 'paiN Gaming'},
    'xero': {'wiki': 'Xero', 'team': 'paiN Gaming'},
    'sarkis': {'wiki': 'Sarkis', 'team': 'paiN Gaming'},
    'von': {'wiki': 'Von (Gabriel Barbosa)', 'team': 'paiN Gaming'},
    'zynts': {'wiki': 'Zynts', 'team': 'RED Canids'},
    'stepz': {'wiki': 'STEPZ (Eloy Rodríguez)', 'team': 'RED Canids'},
    'fuuu': {'wiki': 'Fuuu', 'team': 'RED Canids'},
    'morttheus': {'wiki': 'Morttheus', 'team': 'RED Canids'},
    'frosty': {'wiki': 'Frosty (José Eduardo)', 'team': 'RED Canids'},
    'manel': {'wiki': 'Manel', 'team': 'RED Canids'},
    'tockers': {'wiki': 'Tockers', 'team': 'RED Canids'},
    'beellzy': {'wiki': 'BeellzY', 'team': 'RED Canids'},
    'vinicin': {'wiki': 'Vinicin', 'team': 'RED Canids'},
    'zekas': {'wiki': 'zekas', 'team': 'Vivo Keyd Stars'},
    'disamis': {'wiki': 'Disamis', 'team': 'Vivo Keyd Stars'},
    'mireu': {'wiki': 'Mireu', 'team': 'Vivo Keyd Stars'},
    'jeskla': {'wiki': 'Jeskla', 'team': 'Vivo Keyd Stars'},
    'scamber': {'wiki': 'scamber', 'team': 'Vivo Keyd Stars'},
    'smiley': {'wiki': 'Smiley (Ludvig Granquist)', 'team': 'Vivo Keyd Stars'},
    'benvi': {'wiki': 'Benvi', 'team': 'Vivo Keyd Stars'}
}

STOPWORDS = [
    'Diz','Sobre','Para','Com','Pelo','Pela','Das','Dos','Nas','Nos','Uma',
    'Gente','Apos','Nada','Hoje','Isso','Esta','Tava','Tudo','Mais','Seu',
    'Sua','Como','Pode','Sido','Erro','Parte','Dessa','Troca','Acho','Seja',
    'Por','Vitoria','Seguida','Decima','Derrota','Momento','Bastidores',
    'Turbulento','Confira','Completa','Coletiva','Desabafo','Criticas',
    'Estilo','Ninguem','Mundo','Cansado','Narrativa','Ontem','Talvez',
    'Minha','Sentir','Tempo','Preparacao','Outros','Pensam','Mudar','Renovar',
    'Pior','Liga','Unido','Querer','Fazer','Acontecer','Lugar','Cabeca',
    'Cinco','Nenhum'
]

PUBLICATIONS = {
    "maisesports.com.br": "Mais Esports",
    "www.maisesports.com.br": "Mais Esports",
    "sheepesports.com": "Sheep Esports",
    "www.sheepesports.com": "Sheep Esports",
}

# Datas oficiais de 2026. Para novos anos, basta adicionar três entradas aqui.
# As margens permitem que entrevistas publicadas alguns dias depois de uma
# rodada/final ainda sejam associadas ao torneio correto.
TOURNAMENT_CALENDAR = {
    2026: [
        {"name": "CBLOL Cup 2026", "start": "2026-01-17", "end": "2026-03-01"},
        {"name": "CBLOL 2026 Split 1", "start": "2026-03-28", "end": "2026-06-06"},
        {"name": "CBLOL 2026 Split 2", "start": "2026-07-25", "end": "2026-10-03"},
    ]
}

INTERVIEW_TITLE_MARKERS = (
    "diz", "afirma", "fala", "conta", "revela", "comenta", "explica",
    "avalia", "detalha", "admite", "destaca", "comenta sobre"
)
ARTICLE_TITLE_MARKERS = (
    "confira", "resultado", "classificação", "tabela", "calendário",
    "anuncia", "anunciado", "contrata", "contratação", "escalação",
    "line-up", "roster", "mercado", "rumor"
)

TRANSLATOR_PATTERNS = [
    re.compile(r"(?:tradu[cç][aã]o|traduzido|traduzida|translator|translation)\s*(?:por|by|:)?\s*([A-ZÀ-Ý][^.!?\n]{1,80})", re.I),
]

DEFAULT_CONFIG = {
    "tournament": "",
    "publication": "",
    "type": "Interview",
    "isvideo": "No",
    "translator": ""
}

def parse_date(value):
    if not value:
        return None
    value = str(value).strip()
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None

def normalize_text(value):
    value = unicodedata.normalize('NFKD', value or '')
    return ''.join(c for c in value if not unicodedata.combining(c)).lower()

def detect_publication(url):
    hostname = urlparse(url).hostname or ''
    hostname = hostname.lower().removeprefix('www.')
    return PUBLICATIONS.get(hostname, '')

def detect_tournament(date_published, title, content_text, url):
    """Detecta o torneio por sinais explícitos e, depois, pela data."""
    text = normalize_text(f"{title} {content_text} {url}")
    year_match = re.search(r'\b(20\d{2})\b', text)
    year = int(year_match.group(1)) if year_match else (date_published.year if date_published else None)

    if year:
        explicit = [
            (rf'cblol\s*(?:cup|copa)\s*{year}', f'CBLOL Cup {year}'),
            (rf'cblol\s*{year}\s*split\s*1', f'CBLOL {year} Split 1'),
            (rf'cblol\s*{year}\s*split\s*2', f'CBLOL {year} Split 2'),
            (rf'cblol\s*(?:1|1a|1ª|primeira)\s*(?:etapa|etapa)', f'CBLOL {year} Split 1'),
            (rf'cblol\s*(?:2|2a|2ª|segunda)\s*(?:etapa|etapa)', f'CBLOL {year} Split 2'),
        ]
        for pattern, name in explicit:
            if re.search(pattern, text):
                return name

    tournaments = TOURNAMENT_CALENDAR.get(year, []) if year else []
    if date_published:
        for tournament in tournaments:
            start = datetime.fromisoformat(tournament['start'])
            end = datetime.fromisoformat(tournament['end']) + timedelta(days=7)
            if start <= date_published <= end:
                return tournament['name']

    return ''

def detect_type(title, content_text):
    title_n = normalize_text(title)
    content_n = normalize_text(content_text)

    if any(marker in title_n for marker in INTERVIEW_TITLE_MARKERS):
        return 'Interview'
    if 'entrevista' in title_n or 'interview' in title_n:
        return 'Interview'
    if re.search(r'\b(pergunta|responde|question|answer)\b', content_n):
        return 'Interview'
    if any(marker in title_n for marker in ARTICLE_TITLE_MARKERS):
        return 'Article'
    return 'Interview' if 'diz' in title_n else 'Article'

def detect_translator(content_text):
    for pattern in TRANSLATOR_PATTERNS:
        match = pattern.search(content_text)
        if match:
            name = match.group(1).strip(' -:')
            name = re.split(r'\s{2,}|\n', name)[0].strip()
            if name:
                return name
    return ''

def detect_video(url, soup):
    """Detecta vídeo priorizando a plataforma de origem.

    Regra de negócio: links do Mais Esports e Sheep Esports usados por esta
    ferramenta são considerados conteúdo escrito. Plataformas conhecidas de
    vídeo são consideradas vídeo. Outros domínios usam heurísticas do HTML.
    """
    hostname = (urlparse(url).hostname or '').lower().removeprefix('www.')

    written_publications = {'maisesports.com.br', 'sheepesports.com'}
    video_domains = {
        'youtube.com', 'youtu.be', 'youtube-nocookie.com',
        'vimeo.com', 'twitch.tv', 'kick.com', 'streamable.com'
    }

    # Regra explícita para as duas fontes principais da ferramenta.
    if hostname in written_publications:
        return 'No'

    # Regra explícita para plataformas de vídeo (inclui subdomínios).
    if any(hostname == domain or hostname.endswith('.' + domain) for domain in video_domains):
        return 'Yes'

    # Para domínios ambíguos (ex.: redes sociais), usamos os sinais da página.
    og_type = soup.find('meta', attrs={'property': 'og:type'})
    if og_type and 'video' in (og_type.get('content') or '').lower():
        return 'Yes'

    if soup.find('video'):
        return 'Yes'

    for iframe in soup.find_all('iframe'):
        src = (iframe.get('src') or '').lower()
        if any(host in src for host in (
            'youtube.com', 'youtu.be', 'youtube-nocookie.com',
            'vimeo.com', 'twitch.tv', 'player.twitch.tv', 'kick.com'
        )):
            return 'Yes'

    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or script.get_text())
            items = data.get('@graph', [data]) if isinstance(data, dict) else data
            if isinstance(items, dict):
                items = [items]
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get('@type', '')
                    if isinstance(item_type, list):
                        is_video = any(t in ('VideoObject', 'Video') for t in item_type)
                    else:
                        is_video = item_type in ('VideoObject', 'Video')
                    if is_video:
                        return 'Yes'
        except (json.JSONDecodeError, TypeError):
            pass

    return 'No'

def is_youtube_url(url):
    hostname = (urlparse(url).hostname or '').lower().removeprefix('www.')

    youtube_domains = {
        'youtube.com',
        'youtu.be',
        'youtube-nocookie.com'
    }

    return any(
        hostname == domain or hostname.endswith('.' + domain)
        for domain in youtube_domains
    )


def find_interviewee_in_text(text):
    """
    Procura padrões explícitos de entrevista antes de procurar
    simplesmente todos os jogadores mencionados.
    """

    patterns = [
        r'em entrevista ao mais esports,\s*([^,.\n]+)',
        r'em entrevista para o mais esports,\s*([^,.\n]+)',
        r'conversamos com\s*([^,.\n]+)',
        r'entrevista com\s*([^,.\n]+)',
    ]

    text_normalized = normalize_text(text)

    for pattern in patterns:
        match = re.search(pattern, text_normalized, re.IGNORECASE)

        if not match:
            continue

        possible_name = match.group(1).strip()

        possible_name = re.sub(
            r'\b(fala|falou|comenta|comentou|conta|contou|revela|revelou|diz)\b.*$',
            '',
            possible_name
        ).strip()

        possible_name_normalized = normalize_text(possible_name)

        for player_key, player_data in PLAYER_DATA.items():
            if (
                player_key == possible_name_normalized
                or player_key in possible_name_normalized.split()
            ):
                return player_key

    return None


def detect_players_from_text(text):
    """
    Fallback para encontrar jogadores conhecidos mencionados no texto.
    """
    text_normalized = normalize_text(text)
    found = []

    for player_key in PLAYER_DATA:
        pattern = rf'\b{re.escape(player_key)}\b'

        if re.search(pattern, text_normalized, re.IGNORECASE):
            found.append(player_key)

    return found

def detect_youtube_content_type(title, description):
    """
    Classifica vídeos do YouTube especificamente para uso na Leaguepedia.

    Interview:
    - Entrevistas e conversas com jogadores/pessoas do cenário.

    Article:
    - Especiais, documentários, reportagens e outros conteúdos editoriais.

    Unknown:
    - Conteúdo que não conseguimos classificar com segurança.
    """
    text = normalize_text(f"{title} {description}")
    interview_patterns = [
        "em entrevista ao",
        "em entrevista para",
        "entrevista com",
        "entrevista ao",
        "entrevistamos",
        "conversamos com",
        "conversa com",
        "bate papo com",
        "bate-papo com",
        "papo com",
    ]
    if any(pattern in text for pattern in interview_patterns):
        return "Interview"
    article_patterns = [
        "especial",
        "documentario",
        "reportagem",
        "a historia de",
        "historia de",
        "a trajetoria de",
        "trajetoria de",
        "retrospectiva",
        "bastidores",
        "por dentro",
        "como foi",
        "conheca",
        "conheça",
    ]

    if any(pattern in text for pattern in article_patterns):
        return "Article"
    return ""

def scrape_youtube(url):
    try:
        metadata = get_youtube_metadata(url)

        if metadata.get('error'):
            return {
                'url': url,
                'error': metadata['error']
            }

        title = metadata.get('title') or ''
        description = metadata.get('description') or ''
        tags = metadata.get('tags') or []

        combined_text = " ".join([
            title,
            description,
            " ".join(tags)
        ])

        date_published = parse_date(metadata.get('published_at'))

        if not date_published:
            date_published = datetime.now()

        # Primeiro tentamos identificar explicitamente o entrevistado.
        interviewee_key = find_interviewee_in_text(description)

        # Se não houver padrão explícito, procuramos jogadores no texto.
        if not interviewee_key:
            detected_players = detect_players_from_text(
                f"{title} {description}"
            )

            if len(detected_players) == 1:
                interviewee_key = detected_players[0]

        found_players = []
        found_teams = set()

    if content_type == "Interview":

    # Primeiro tentamos encontrar explicitamente o entrevistado
    interviewee_key = find_interviewee_in_text(description)

    # Fallback: procurar jogadores no título + descrição
    if not interviewee_key:
        detected_players = detect_players_from_text(
            f"{title} {description}"
        )

        # Só usamos automaticamente se houver apenas um candidato
        if len(detected_players) == 1:
            interviewee_key = detected_players[0]

    # Adicionar somente o entrevistado principal
    if interviewee_key and interviewee_key in PLAYER_DATA:
        found_players.append(
            PLAYER_DATA[interviewee_key]["wiki"]
        )

        found_teams.add(
            PLAYER_DATA[interviewee_key]["team"]
        )

    elif content_type == "Article":

    detected_players = detect_players_from_text(
        f"{title} {description}"
    )

    for player_key in detected_players:

        if player_key not in PLAYER_DATA:
            continue

        player = PLAYER_DATA[player_key]

        found_players.append(
            player["wiki"]
        )

        found_teams.add(
            player["team"]
        )

        if interviewee_key and interviewee_key in PLAYER_DATA:
            found_players.append(
                PLAYER_DATA[interviewee_key]['wiki']
            )

            found_teams.add(
                PLAYER_DATA[interviewee_key]['team']
            )

        content_type = detect_youtube_content_type(title,description)

        tournament = detect_tournament(
            date_published,
            title,
            combined_text,
            url
        )

        translator = detect_translator(description)

        return {
            'url': url,
            'title': title.replace('|', '{{!}}'),
            'players': ", ".join(found_players),
            'teams': ", ".join(sorted(found_teams)),
            'author': metadata.get('channel') or '',
            'date': date_published.strftime('%Y-%m-%d'),

            # Regra específica da Leaguepedia para vídeos.
            'publication': 'YouTube',
            'tournament': tournament,
            'type': content_type,
            'translator': translator,
            'isvideo': 'Yes',

            # Informações extras úteis para debug/futuro.
            'video_id': metadata.get('video_id'),
            'duration': metadata.get('duration'),
            'captions_available': metadata.get('captions_available')
        }

    except Exception as exc:
        return {
            'url': url,
            'error': f'Erro ao processar vídeo do YouTube: {exc}'
        }

def scrape_article(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LeaguepediaInterviewScraper/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        content_text = soup.get_text(" ", strip=True)

        title_tag = soup.find('h1')
        title = title_tag.get_text(" ", strip=True) if title_tag else ""
        title_clean = title.replace('|', '{{!}}')

        author_formatted = ""
        if "Corres" in content_text or "Fiorini" in content_text:
            author_formatted = '[[Self:Corres|Sérgio "Corres" Fiorini]]'
        elif "Ian Teixeira" in content_text:
            author_formatted = "[[Ian Teixeira]]"

        date_published = None

        script_tag = soup.find('script', type='application/ld+json')
        if script_tag and script_tag.string:
            try:
                data_json = json.loads(script_tag.string)
                graph = data_json.get('@graph', [data_json]) if isinstance(data_json, dict) else []
                for item in graph:
                    if isinstance(item, dict) and 'datePublished' in item:
                        date_published = parse_date(item['datePublished'])
                        if date_published:
                            break
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

        if not date_published:
            time_tag = soup.find('time', class_='entry-date') or soup.find('time')
            if time_tag and time_tag.get('datetime'):
                date_published = parse_date(time_tag['datetime'])

        if not date_published:
            date_published = datetime.now()

        found_players = []
        found_teams = set()
        slug_parts = url.rstrip('/').split('/')[-1].split('-')
        slug_lower = [part.lower() for part in slug_parts]

        players_in_slug = [part for part in slug_lower if part in PLAYER_DATA]

        if players_in_slug:
            for p_key in players_in_slug:
                found_players.append(PLAYER_DATA[p_key]['wiki'])
                found_teams.add(PLAYER_DATA[p_key]['team'])
        else:
            if 'diz' in slug_lower:
                idx = slug_lower.index('diz')
                for p in slug_parts[idx + 1:]:
                    if p.capitalize() not in STOPWORDS and len(p) > 2:
                        match = re.search(re.escape(p), title, re.IGNORECASE)
                        if match and match.group(0).capitalize() not in STOPWORDS:
                            found_players.append(match.group(0))

            for part in slug_lower:
                if part in TEAM_MAP:
                    found_teams.add(TEAM_MAP[part])

        publication = detect_publication(url)
        tournament = detect_tournament(date_published, title, content_text, url)
        content_type = detect_type(title, content_text)
        translator = detect_translator(content_text)
        isvideo = detect_video(url, soup)

        return {
            'url': url,
            'title': title_clean,
            'players': ", ".join(sorted(set(found_players))),
            'teams': ", ".join(sorted(found_teams)),
            'author': author_formatted,
            'date': date_published.strftime('%Y-%m-%d'),
            'tournament': tournament,
            'publication': publication,
            'type': content_type,
            'translator': translator,
            'isvideo': isvideo
        }

    except requests.RequestException as exc:
        return {'url': url, 'error': f'Erro ao acessar a página: {exc}'}
    except Exception as exc:
        return {'url': url, 'error': f'Erro ao processar a página: {exc}'}

def make_template(res):
    return (
        "{{ExternalContent/Line\n"
        f"|url={res['url']}\n"
        f"|title={res['title']}\n"
        f"|players={res['players']}\n"
        f"|teams={res['teams']}\n"
        f"|tournament={res['tournament']}\n"
        f"|publication={res['publication']}\n"
        f"|author={res['author']}\n"
        f"|translator={res['translator']}\n"
        f"|type={res['type']}\n"
        f"|isvideo={res['isvideo']}\n"
        "}}"
    )

@app.get('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route("/api/youtube-metadata", methods=["POST"])
def youtube_metadata():
    data = request.get_json()

    if not data or not data.get("url"):
        return jsonify({
            "error": "URL não informada"
        }), 400

    try:
        result = get_youtube_metadata(data["url"])
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Erro ao consultar YouTube API: {str(e)}"
        }), 500

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.post('/api/scrape')
def scrape():
    payload = request.get_json(silent=True) or {}
    urls = payload.get('urls', [])

    if not isinstance(urls, list):
        return jsonify({
            "error": "urls deve ser uma lista."
        }), 400

    # Remove URLs duplicadas e inválidas
    urls = list(dict.fromkeys(
        u.strip() for u in urls
        if isinstance(u, str)
        and u.strip().startswith(('http://', 'https://'))
    ))

    if not urls:
        return jsonify({
            "error": "Nenhuma URL válida foi enviada."
        }), 400

    # Limite de URLs por requisição
    if len(urls) > MAX_URLS_PER_REQUEST:
        return jsonify({
            "error": (
                f"O máximo permitido é "
                f"{MAX_URLS_PER_REQUEST} URLs por requisição."
            )
        }), 400

    results = []

    for url in urls:

        if is_youtube_url(url):
            result = scrape_youtube(url)
        else:
            result = scrape_article(url)

        if 'error' not in result:
            result['template'] = make_template(result)

        results.append(result)

    grouped = defaultdict(list)

    for result in results:
        if 'error' not in result:
            grouped[result['date']].append(result)

    return jsonify({
        "results": results,
        "grouped": dict(sorted(grouped.items())),
    })
