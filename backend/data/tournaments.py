TOURNAMENT_CALENDAR = {
    2026: [
        {
            "name": "CBLOL Cup 2026",
            "start": "2026-01-17",
            "end": "2026-03-01"
        },
        {
            "name": "CBLOL 2026 Split 1",
            "start": "2026-03-28",
            "end": "2026-06-06"
        },
        {
            "name": "CBLOL 2026 Split 2",
            "start": "2026-07-25",
            "end": "2026-10-03"
        },
    ]
}


TOURNAMENT_PATTERNS = {
    "cblol": {
        "cup": [
            r"cblol\s*(?:cup|copa)\s*{year}",
        ],
        "split1": [
            r"cblol\s*{year}\s*split\s*1",
            r"cblol\s*(?:1|1a|1ª|primeira)\s*etapa",
        ],
        "split2": [
            r"cblol\s*{year}\s*split\s*2",
            r"cblol\s*(?:2|2a|2ª|segunda)\s*etapa",
        ],
    }
}
