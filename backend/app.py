from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import unicodedata
from collections import defaultdict
from data.players import PLAYER_DATA
from data.teams import TEAM_MAP
from youtube_metadata import get_youtube_metadata
from services.leaguepedia import (
    resolve_player,
    get_cached_player,
    cache_player,
)
from data.content import (
    STOPWORDS,
    INTERVIEW_TITLE_MARKERS,
    ARTICLE_TITLE_MARKERS,
    TRANSLATOR_PATTERNS,
    YOUTUBE_INTERVIEW_PATTERNS,
    YOUTUBE_ARTICLE_PATTERNS,
)
from data.publications import (
    PUBLICATIONS,
    WRITTEN_PUBLICATIONS,
    VIDEO_DOMAINS,
)
from data.tournaments import (
    TOURNAMENT_CALENDAR,
    TOURNAMENT_PATTERNS,
    TOURNAMENT_NAMES,
)
from data.authors import AUTHOR_MAPPINGS
from data.config import MAX_URLS_PER_REQUEST

app = Flask(__name__)
CORS(app)

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
    """
    Detecta torneios priorizando:

    1. Menções explícitas no título/texto/URL.
    2. Data de publicação dentro do calendário.
    3. Margem de 7 dias após o torneio como fallback.
    """

    text = normalize_text(
        f"{title} {content_text} {url}"
    )

    # --------------------------------------------------
    # DESCOBRIR O ANO
    # --------------------------------------------------

    year_match = re.search(
        r'\b(20\d{2})\b',
        text
    )

    if year_match:
        year = int(year_match.group(1))
    elif date_published:
        year = date_published.year
    else:
        return ''

    for tournament_group, tournament_types in TOURNAMENT_PATTERNS.items():
        for tournament_type, patterns in tournament_types.items():
            for pattern in patterns:
                formatted_pattern = pattern.format(
                    year=year
                )
                if re.search(
                    formatted_pattern,
                    text,
                    re.IGNORECASE
                ):
                    name_template = (
                        TOURNAMENT_NAMES
                        .get(tournament_group, {})
                        .get(tournament_type)
                    )
                    if name_template:
                        return name_template.format(
                            year=year
                        )

    tournaments = TOURNAMENT_CALENDAR.get(
        year,
        []
    )

    if date_published:
        for tournament in tournaments:
            start = datetime.fromisoformat(
                tournament['start']
            )
            end = datetime.fromisoformat(
                tournament['end']
            )
            if start <= date_published <= end:
                return tournament['name']

    if date_published:
        for tournament in reversed(tournaments):
            end = datetime.fromisoformat(
                tournament['end']
            )
            grace_end = end + timedelta(days=7)
            if end < date_published <= grace_end:
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
    hostname = (
        urlparse(url).hostname or ''
    ).lower().removeprefix('www.')

    # Fontes principais da ferramenta são conteúdo escrito.
    if hostname in WRITTEN_PUBLICATIONS:
        return 'No'

    # Plataformas conhecidas de vídeo.
    if any(
        hostname == domain or hostname.endswith('.' + domain)
        for domain in VIDEO_DOMAINS
    ):
        return 'Yes'

    # Domínios ambíguos usam sinais da página.
    og_type = soup.find(
        'meta',
        attrs={'property': 'og:type'}
    )

    if og_type and 'video' in (
        og_type.get('content') or ''
    ).lower():
        return 'Yes'

    if soup.find('video'):
        return 'Yes'

    for iframe in soup.find_all('iframe'):
        src = (iframe.get('src') or '').lower()

        if any(
            host in src
                for host in VIDEO_DOMAINS
        ):
            return 'Yes'

    for script in soup.find_all(
        'script',
        type='application/ld+json'
    ):
        try:
            data = json.loads(
                script.string or script.get_text()
            )

            items = (
                data.get('@graph', [data])
                if isinstance(data, dict)
                else data
            )

            if isinstance(items, dict):
                items = [items]

            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue

                    item_type = item.get('@type', '')

                    if isinstance(item_type, list):
                        is_video = any(
                            t in ('VideoObject', 'Video')
                            for t in item_type
                        )
                    else:
                        is_video = item_type in (
                            'VideoObject',
                            'Video'
                        )

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
    Procura padrões explícitos que indiquem
    quem é o entrevistado.
    """

    patterns = [
        r'em entrevista ao mais esports,\s*([^,.\n]+)',
        r'em entrevista para o mais esports,\s*([^,.\n]+)',
        r'conversamos com\s*([^,.\n]+)',
        r'entrevista com\s*([^,.\n]+)',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        possible_name = match.group(1).strip()

        possible_name = re.sub(
            (
                r'\b('
                r'fala|falou|comenta|comentou|'
                r'conta|contou|revela|revelou|diz'
                r')\b.*$'
            ),
            '',
            possible_name,
            flags=re.IGNORECASE
        ).strip()

        if not possible_name:
            continue

        # Primeiro PLAYER_DATA.
        player_key = normalize_text(
            possible_name
        )

        if player_key in PLAYER_DATA:

            return {
                "wiki": PLAYER_DATA[player_key].get(
                    "wiki",
                    ""
                ),
                "team": PLAYER_DATA[player_key].get(
                    "team",
                    ""
                ),
                "role": PLAYER_DATA[player_key].get(
                    "role",
                    ""
                )
            }

        # Depois cache.
        player = get_cached_player(
            possible_name
        )

        if player:
            return player

        # Finalmente Leaguepedia.
        player = resolve_player(
            possible_name
        )

        player = resolve_player(candidate)
        return player
    return None

def detect_players_from_text(text):
    """
    Detecta jogadores conhecidos no texto.

    Primeiro procura no PLAYER_DATA local.
    Depois procura nomes candidatos no cache/Leaguepedia.
    """

    text_normalized = normalize_text(text)

    found = []

    for player_key in PLAYER_DATA:

        pattern = (
            rf'\b{re.escape(player_key)}\b'
        )

        if re.search(
            pattern,
            text_normalized,
            re.IGNORECASE
        ):
            found.append(player_key)

    return list(dict.fromkeys(found))

def resolve_players_from_text(text):
    """
    Procura jogadores mencionados no texto.

    Ordem:
    1. PLAYER_DATA local
    2. player_cache.json
    3. Leaguepedia
    """

    text_normalized = normalize_text(text)

    found_players = {}

    # ==================================================
    # 1. PROCURA JOGADORES CONHECIDOS LOCALMENTE
    # ==================================================

    for player_key, player_data in PLAYER_DATA.items():

        pattern = (
            rf'\b{re.escape(player_key)}\b'
        )

        if re.search(
            pattern,
            text_normalized,
            re.IGNORECASE
        ):
            found_players[player_key] = {
                "wiki": player_data.get("wiki", ""),
                "team": player_data.get("team", ""),
                "role": player_data.get("role", "")
            }

    # ==================================================
    # 2. EXTRAÇÃO DE POSSÍVEIS NOMES
    # ==================================================

    words = re.findall(
        r'\b[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9_-]{2,}\b',
        text
    )

    candidates = []

    for word in words:

        normalized = normalize_text(word)

        if normalized in PLAYER_DATA:
            continue

        if normalized in STOPWORDS:
            continue

        candidates.append(word)

    candidates = list(
        dict.fromkeys(candidates)
    )

    # ==================================================
    # 3. CACHE + LEAGUEPEDIA
    # ==================================================

    for candidate in candidates:

        player_key = normalize_text(candidate)

        # Evita repetir consultas.
        if player_key in found_players:
            continue

        # Primeiro verifica cache.
        player = get_cached_player(candidate)

        # Se não estiver no cache,
        # consulta a Leaguepedia.
        if not player:

            player = resolve_player(candidate)

        if not player:
            continue

        wiki_name = player.get("wiki", "")

        # Segurança:
        # só aceita se existir um nome válido.
        if not wiki_name:
            continue

        found_players[player_key] = player

    return found_players

def detect_youtube_content_type(title, description):
    """
    Classifica vídeos do YouTube para uso na Leaguepedia.

    Interview:
    Entrevistas e conversas com jogadores/pessoas do cenário.

    Article:
    Especiais, documentários, reportagens e outros
    conteúdos editoriais.

    Retorna string vazia quando não houver classificação segura.
    """

    text = normalize_text(
        f"{title} {description}"
    )

    if any(
        pattern in text
        for pattern in YOUTUBE_INTERVIEW_PATTERNS
    ):
        return "Interview"

    if any(
        pattern in text
        for pattern in YOUTUBE_ARTICLE_PATTERNS
    ):
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

        date_published = parse_date(
            metadata.get('published_at')
        )

        if not date_published:
            date_published = datetime.now()

        # ==================================================
        # DETECTA O TIPO DE CONTEÚDO
        # ==================================================

        content_type = detect_youtube_content_type(
            title,
            description
        )

        found_players = []
        found_teams = set()

        # ==================================================
        # INTERVIEW
        # ==================================================

        if content_type == "Interview":

            # Primeiro tenta identificar explicitamente
            # quem é o entrevistado.
            interviewee = find_interviewee_in_text(
                description
            )

            # Fallback:
            # procura jogadores no título + descrição.
            if not interviewee:

                detected_players = (
                    resolve_players_from_text(
                        f"{title} {description}"
                    )
                )

                # Para entrevistas, só usamos automaticamente
                # se encontrarmos exatamente um jogador.
                if len(detected_players) == 1:

                    interviewee = next(
                        iter(detected_players.values())
                    )

            # Adiciona somente o entrevistado principal.
            if interviewee:

                wiki_name = interviewee.get(
                    "wiki",
                    ""
                )

                team_name = interviewee.get(
                    "team",
                    ""
                )

                if wiki_name:
                    found_players.append(
                        wiki_name
                    )

                if team_name:
                    found_teams.add(
                        team_name
                    )

        # ==================================================
        # ARTICLE / ESPECIAL
        # ==================================================

        elif content_type == "Article":

            detected_players = (
                resolve_players_from_text(
                    f"{title} {description}"
                )
            )

            for player in detected_players.values():

                wiki_name = player.get(
                    "wiki",
                    ""
                )

                team_name = player.get(
                    "team",
                    ""
                )

                if wiki_name:
                    found_players.append(
                        wiki_name
                    )

                if team_name:
                    found_teams.add(
                        team_name
                    )

        # ==================================================
        # OUTRAS DETECÇÕES
        # ==================================================

        tournament = detect_tournament(
            date_published,
            title,
            combined_text,
            url
        )

        translator = detect_translator(
            description
        )

        # Remove possíveis duplicatas mantendo a ordem.
        found_players = list(
            dict.fromkeys(found_players)
        )

        return {
            'url': url,

            'title': title.replace(
                '|',
                '{{!}}'
            ),

            'players': ", ".join(
                found_players
            ),

            'teams': ", ".join(
                sorted(found_teams)
            ),

            'author': (
                metadata.get('channel')
                or ''
            ),

            'date': date_published.strftime(
                '%Y-%m-%d'
            ),

            # Regra específica da Leaguepedia
            # para vídeos do YouTube.
            'publication': 'YouTube',

            'tournament': tournament,

            'type': content_type,

            'translator': translator,

            'isvideo': 'Yes',

            # Informações extras úteis para debug/futuro.
            'video_id': metadata.get(
                'video_id'
            ),

            'duration': metadata.get(
                'duration'
            ),

            'captions_available': metadata.get(
                'captions_available'
            )
        }

    except Exception as exc:

        return {
            'url': url,
            'error': (
                f'Erro ao processar vídeo '
                f'do YouTube: {exc}'
            )
        }

def detect_author(content_text):
    for author in AUTHOR_MAPPINGS:
        if any(
            name.lower() in content_text.lower()
            for name in author["matches"]
        ):
            return author["wiki"]

    return ""
        
def scrape_article(url):
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 '
                '(compatible; LeaguepediaInterviewScraper/1.0)'
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            'html.parser'
        )

        content_text = soup.get_text(
            " ",
            strip=True
        )

        # ==============================
        # TÍTULO
        # ==============================

        title_tag = soup.find('h1')

        title = (
            title_tag.get_text(" ", strip=True)
            if title_tag
            else ""
        )

        title_clean = title.replace(
            '|',
            '{{!}}'
        )

        # ==============================
        # AUTOR
        # ==============================

        author_formatted = detect_author(
            content_text
        )

        # ==============================
        # DATA
        # ==============================

        date_published = None

        script_tag = soup.find(
            'script',
            type='application/ld+json'
        )

        if script_tag and script_tag.string:
            try:
                data_json = json.loads(
                    script_tag.string
                )

                graph = (
                    data_json.get(
                        '@graph',
                        [data_json]
                    )
                    if isinstance(
                        data_json,
                        dict
                    )
                    else []
                )

                for item in graph:
                    if (
                        isinstance(item, dict)
                        and 'datePublished' in item
                    ):
                        date_published = parse_date(
                            item['datePublished']
                        )

                        if date_published:
                            break

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError
            ):
                pass

        # Fallback para <time>
        if not date_published:

            time_tag = (
                soup.find(
                    'time',
                    class_='entry-date'
                )
                or soup.find('time')
            )

            if (
                time_tag
                and time_tag.get('datetime')
            ):
                date_published = parse_date(
                    time_tag['datetime']
                )

        # Último fallback
        if not date_published:
            date_published = datetime.now()

        # ==============================
        # PLAYERS / TEAMS
        # ==============================

        found_players = []
        found_teams = set()

        slug_parts = (
            url
            .rstrip('/')
            .split('/')[-1]
            .split('-')
        )

        slug_lower = [
            part.lower()
            for part in slug_parts
        ]

        players_in_slug = [
            part
            for part in slug_lower
            if part in PLAYER_DATA
        ]

        # ==========================================
        # DETECÇÃO DE JOGADORES
        # PLAYER_DATA → CACHE → LEAGUEPEDIA
        # ==========================================
        
        resolved_players = resolve_players_from_text(
            f"{title} {content_text}"
        )
        
        for player in resolved_players.values():
        
            wiki_name = player.get(
                "wiki",
                ""
            )
        
            team_name = player.get(
                "team",
                ""
            )
        
            if wiki_name:
                found_players.append(
                    wiki_name
                )
        
            if team_name:
                found_teams.add(
                    team_name
                )
        
        # ==========================================
        # DETECÇÃO DE EQUIPES
        # ==========================================
        
        for part in slug_lower:
        
            if part in TEAM_MAP:
        
                found_teams.add(
                    TEAM_MAP[part]
                )
        
        # ==============================
        # DETECÇÕES
        # ==============================

        publication = detect_publication(url)
        tournament = detect_tournament(
            date_published,
            title,
            content_text,
            url
        )
        content_type = detect_type(
            title,
            content_text
        )
        translator = detect_translator(
            content_text
        )
        isvideo = detect_video(
            url,
            soup
        )

        # ==============================
        # RESULTADO
        # ==============================

        return {
            'url': url,
            'title': title_clean,
            'players': ", ".join(
                sorted(set(found_players))
            ),
            'teams': ", ".join(
                sorted(found_teams)
            ),
            'author': author_formatted,
            'date': date_published.strftime(
                '%Y-%m-%d'
            ),
            'tournament': tournament,
            'publication': publication,
            'type': content_type,
            'translator': translator,
            'isvideo': isvideo
        }

    except requests.RequestException as exc:
        return {
            'url': url,
            'error': (
                f'Erro ao acessar a página: {exc}'
            )
        }
    except Exception as exc:
        return {
            'url': url,
            'error': (
                f'Erro ao processar a página: {exc}'
            )
        }

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
