import json
import os
import unicodedata

import requests


# ==================================================
# CONFIGURAÇÃO
# ==================================================

LEAGUEPEDIA_API_URL = (
    "https://lol.fandom.com/api.php"
)

REQUEST_TIMEOUT = 5

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PLAYER_CACHE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "player_cache.json"
)

REQUEST_HEADERS = {
    "User-Agent": (
        "LeaguepediaInterviewScraper/1.0 "
        "(GitHub personal project)"
    )
}


# ==================================================
# NORMALIZAÇÃO
# ==================================================

def normalize_player_key(value):
    """
    Normaliza nomes para uso como chave.

    Exemplos:
        titaN -> titan
        Céos -> ceos
        Robo -> robo
    """

    value = unicodedata.normalize(
        "NFKD",
        value or ""
    )

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    return value.lower().strip()


def normalize_text(value):
    """
    Alias para normalização de texto.
    """

    return normalize_player_key(value)


# ==================================================
# PLAYER CACHE
# ==================================================

def load_player_cache():
    """
    Carrega o cache local de jogadores.
    """

    if not os.path.exists(
        PLAYER_CACHE_PATH
    ):
        return {}

    try:
        with open(
            PLAYER_CACHE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):
                return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    return {}


def save_player_cache(cache):
    """
    Salva o cache local.
    """

    try:
        os.makedirs(
            os.path.dirname(
                PLAYER_CACHE_PATH
            ),
            exist_ok=True
        )

        with open(
            PLAYER_CACHE_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                cache,
                file,
                ensure_ascii=False,
                indent=2
            )

    except OSError as exc:
        print(
            f"Erro ao salvar player cache: {exc}"
        )


def get_cached_player(player_name):
    """
    Procura um jogador no cache.
    """

    if not player_name:
        return None

    cache = load_player_cache()

    player_key = normalize_player_key(
        player_name
    )

    return cache.get(player_key)


def cache_player(player_name, player_data):
    """
    Adiciona ou atualiza um jogador no cache.

    player_data esperado:

    {
        "id": "...",
        "wiki": "...",
        "team": "...",
        "role": "..."
    }
    """

    if not player_name or not player_data:
        return None

    player_key = normalize_player_key(
        player_name
    )

    cache = load_player_cache()

    cache[player_key] = {
        "id": player_data.get(
            "id",
            ""
        ),
        "wiki": player_data.get(
            "wiki",
            ""
        ),
        "team": player_data.get(
            "team",
            ""
        ),
        "role": player_data.get(
            "role",
            ""
        ),
    }

    save_player_cache(cache)

    return cache[player_key]


# ==================================================
# LEAGUEPEDIA CARGO API
# ==================================================

def cargo_query(
    tables,
    fields,
    where=None,
    join_on=None,
    limit=20
):
    """
    Executa uma consulta Cargo
    na API da Leaguepedia.
    """

    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": tables,
        "fields": fields,
        "limit": limit,
    }

    if where:
        params["where"] = where

    if join_on:
        params["join_on"] = join_on

    response = requests.get(
        LEAGUEPEDIA_API_URL,
        params=params,
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT
)

    response.raise_for_status()
    data = response.json()
    results = data.get(
        "cargoquery",
        []
    )

    return [
        item.get("title", {})
        for item in results
    ]


# ==================================================
# BUSCA GERAL DE JOGADOR
# ==================================================

def search_player(player_name):
    """
    Procura um jogador na tabela Players.
    """

    if not player_name:
        return None

    player_name = player_name.strip()

    escaped_name = player_name.replace(
        "'",
        "\\'"
    )

    try:

        results = cargo_query(
            tables="Players",
            fields=(
                "ID,"
                "OverviewPage,"
                "Player,"
                "Team,"
                "CurrentTeams"
            ),
            where=f'ID="{escaped_name}"',
            limit=10
        )

    except requests.RequestException:
        return None

    if not results:
        return None

    normalized_search = normalize_text(
        player_name
    )

    selected = None

    for result in results:

        player_id = normalize_text(
            result.get(
                "ID",
                ""
            )
        )

        if player_id == normalized_search:
            selected = result
            break

    if not selected:
        selected = results[0]

    return {
        "id": selected.get(
            "ID",
            ""
        ),
        "wiki": (
            selected.get(
                "Player"
            )
            or selected.get(
                "OverviewPage"
            )
            or selected.get(
                "ID",
                ""
            )
        ),
        "team": selected.get(
            "Team",
            ""
        ),
        "role": "",
    }


# ==================================================
# BUSCA ATUAL DE JOGADOR
# ==================================================

def get_current_player(player_name):
    """
    Busca informações atuais do jogador
    na tabela ListplayerCurrent.
    """

    if not player_name:
        return None

    player_name = player_name.strip()

    escaped_name = player_name.replace(
        "'",
        "\\'"
    )

    try:

        results = cargo_query(
            tables="ListplayerCurrent",
            fields=(
                "ID,"
                "Link,"
                "Name,"
                "Role,"
                "Team"
            ),
            where=f'ID="{escaped_name}"',
            limit=10
        )

    except requests.RequestException:
        return None

    if not results:
        return None

    normalized_search = normalize_text(
        player_name
    )

    selected = None

    for result in results:

        if normalize_text(
            result.get(
                "ID",
                ""
            )
        ) == normalized_search:

            selected = result
            break

    if not selected:
        selected = results[0]

    return {
        "id": selected.get(
            "ID",
            ""
        ),
        "wiki": (
            selected.get(
                "Link"
            )
            or selected.get(
                "Name"
            )
            or selected.get(
                "ID",
                ""
            )
        ),
        "team": selected.get(
            "Team",
            ""
        ),
        "role": selected.get(
            "Role",
            ""
        ),
    }


# ==================================================
# RESOLUÇÃO DE JOGADOR
# ==================================================

def resolve_player(player_name):
    """
    Resolve um jogador automaticamente.

    Ordem:

    1. Cache local
    2. Lista atual da Leaguepedia
    3. Tabela geral Players
    4. Salva resultado no cache
    """

    if not player_name:
        return None

    # ----------------------------------------------
    # 1. CACHE
    # ----------------------------------------------

    cached_player = get_cached_player(
        player_name
    )

    if cached_player:
        return cached_player

    # ----------------------------------------------
    # 2. LEAGUEPEDIA ATUAL
    # ----------------------------------------------

    player = get_current_player(
        player_name
    )

    # ----------------------------------------------
    # 3. LEAGUEPEDIA GERAL
    # ----------------------------------------------

    if not player:
        player = search_player(
            player_name
        )

    # ----------------------------------------------
    # 4. NÃO ENCONTROU
    # ----------------------------------------------

    if not player:
        return None

    # ----------------------------------------------
    # 5. SALVA NO CACHE
    # ----------------------------------------------

    cache_player(
        player_name,
        player
    )

    return player


# ==================================================
# JOGADORES DE UM TORNEIO
# ==================================================

def get_tournament_players(tournament_name):
    """
    Busca jogadores registrados em um torneio.

    Retorna:

    {
        "titan": {
            "wiki": "titaN",
            "team": "paiN Gaming",
            "role": "Bot"
        }
    }
    """

    if not tournament_name:
        return {}

    escaped_tournament = (
        tournament_name
        .replace(
            "'",
            "\\'"
        )
    )

    try:

        results = cargo_query(
            tables="TournamentPlayers",
            fields=(
                "Player,"
                "Team,"
                "Role,"
                "OverviewPage"
            ),
            where=(
                f'OverviewPage="{escaped_tournament}"'
            ),
            limit=500
        )

    except requests.RequestException:
        return {}

    players = {}

    for result in results:

        player_name = (
            result.get(
                "Player",
                ""
            )
            or ""
        ).strip()

        if not player_name:
            continue

        player_key = normalize_text(
            player_name
        )

        player_data = {
            "id": player_name,
            "wiki": player_name,
            "team": result.get(
                "Team",
                ""
            ),
            "role": result.get(
                "Role",
                ""
            ),
        }

        players[player_key] = player_data

        # Também aproveitamos para popular o cache.
        cache_player(
            player_name,
            player_data
        )

    return players
