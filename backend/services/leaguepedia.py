import requests
import unicodedata


LEAGUEPEDIA_API_URL = (
    "https://lol.fandom.com/api.php"
)

REQUEST_TIMEOUT = 10

def normalize_text(value):
    """
    Normaliza texto para comparações.

    Exemplos:
        titaN -> titan
        TitaN -> titan
        Céos -> ceos
    """
    value = unicodedata.normalize(
        "NFKD",
        value or ""
    )

    return "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    ).lower().strip()


def cargo_query(
    tables,
    fields,
    where=None,
    join_on=None,
    limit=20
):
    """
    Executa uma consulta Cargo na API da Leaguepedia.

    Retorna uma lista de dicionários.
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
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": (
                "LeaguepediaInterviewScraper/1.0 "
                "(GitHub personal project)"
            )
        }
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("cargoquery", [])

    return [
        item.get("title", {})
        for item in results
    ]


def search_player(player_name):
    """
    Procura um jogador pelo IGN.

    Retorna:
        {
            "id": "...",
            "wiki": "...",
            "team": "...",
            "role": "..."
        }

    ou None caso não encontre.
    """

    if not player_name:
        return None

    player_name = player_name.strip()

    # Escapar aspas simples para a consulta Cargo.
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

    # Primeiro tentamos encontrar uma correspondência
    # exata após normalização.
    normalized_search = normalize_text(
        player_name
    )

    selected = None

    for result in results:

        player_id = normalize_text(
            result.get("ID", "")
        )

        if player_id == normalized_search:
            selected = result
            break

    # Se não houver match exato,
    # usamos o primeiro resultado.
    if not selected:
        selected = results[0]

    return {
        "id": selected.get("ID", ""),
        "wiki": (
            selected.get("Player")
            or selected.get("OverviewPage")
            or selected.get("ID", "")
        ),
        "team": selected.get("Team", ""),
        "teams": selected.get(
            "CurrentTeams",
            ""
        ),
    }


def get_current_player(player_name):
    """
    Busca informações atuais do jogador.

    Usa a tabela ListplayerCurrent,
    que possui informações como:
    ID, Link, Name, Role e Team.
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
            result.get("ID", "")
        ) == normalized_search:
            selected = result
            break

    if not selected:
        selected = results[0]

    return {
        "id": selected.get("ID", ""),
        "wiki": (
            selected.get("Link")
            or selected.get("ID", "")
        ),
        "name": selected.get("Name", ""),
        "role": selected.get("Role", ""),
        "team": selected.get("Team", ""),
    }


def resolve_player(player_name):
    """
    Função principal recomendada para o scraper.

    Primeiro tenta obter os dados atuais
    do jogador.

    Caso não encontre, tenta a tabela
    geral Players.

    Retorna None caso o jogador não seja
    encontrado.
    """

    player = get_current_player(
        player_name
    )

    if player:
        return player

    return search_player(
        player_name
    )


def get_tournament_players(tournament_name):
    """
    Busca jogadores registrados em um torneio.

    Retorna um dicionário no formato:

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
        .replace("'", "\\'")
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
            result.get("Player")
            or ""
        ).strip()

        if not player_name:
            continue

        player_key = normalize_text(
            player_name
        )

        players[player_key] = {
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

    return players
