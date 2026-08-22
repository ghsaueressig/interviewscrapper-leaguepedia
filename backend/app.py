from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from collections import defaultdict

app = Flask(__name__)
CORS(app)

TEAM_MAP = {
    'pain': 'paiN Gaming', 'los': 'LOS', 'loud': 'LOUD', 'furia': 'FURIA',
    'red': 'RED Canids', 'vks': 'Vivo Keyd Stars', 'fx': 'Fluxo W7M',
    'fluxo': 'Fluxo W7M', 'fxw7m': 'Fluxo W7M', 'w7m': 'Fluxo W7M',
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

DEFAULT_CONFIG = {
    "tournament": "CBLOL 2026 Split 2",
    "publication": "Mais Esports",
    "type": "Interview",
    "isvideo": "No",
    "translator": ""
}

def parse_date(value):
    if not value:
        return None
    value = value.strip()
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).replace(tzinfo=None)
    except ValueError:
        return None

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

        return {
            'url': url,
            'title': title_clean,
            'players': ", ".join(sorted(set(found_players))),
            'teams': ", ".join(sorted(found_teams)),
            'author': author_formatted,
            'date': date_published.strftime('%Y-%m-%d')
        }

    except requests.RequestException as exc:
        return {'url': url, 'error': f'Erro ao acessar a página: {exc}'}
    except Exception as exc:
        return {'url': url, 'error': f'Erro ao processar a página: {exc}'}

def make_template(res, config):
    return (
        "{{ExternalContent/Line\n"
        f"|url={res['url']}\n"
        f"|title={res['title']}\n"
        f"|players={res['players']}\n"
        f"|teams={res['teams']}\n"
        f"|tournament={config['tournament']}\n"
        f"|publication={config['publication']}\n"
        f"|author={res['author']}\n"
        f"|translator={config['translator']}\n"
        f"|type={config['type']}\n"
        f"|isvideo={config['isvideo']}\n"
        "}}"
    )

@app.get('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.post('/api/scrape')
def scrape():
    payload = request.get_json(silent=True) or {}
    urls = payload.get('urls', [])
    config = {**DEFAULT_CONFIG, **(payload.get('config') or {})}

    if not isinstance(urls, list):
        return jsonify({"error": "urls deve ser uma lista."}), 400

    urls = list(dict.fromkeys(
        u.strip() for u in urls
        if isinstance(u, str) and u.strip().startswith(('http://', 'https://'))
    ))

    if not urls:
        return jsonify({"error": "Nenhuma URL válida foi enviada."}), 400

    results = []
    for url in urls:
        result = scrape_article(url)
        if 'error' not in result:
            result['template'] = make_template(result, config)
        results.append(result)

    grouped = defaultdict(list)
    for result in results:
        if 'error' not in result:
            grouped[result['date']].append(result)

    return jsonify({
        "results": results,
        "grouped": dict(sorted(grouped.items())),
        "config": config
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
