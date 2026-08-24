TOURNAMENT_CALENDAR = {
    2025: [
        {
            "name": "LTA South 2025 Split 1",
            "start": "2025-01-25",
            "end": "2025-02-09"
        },
        {
            "name": "LTA 2025 Split 1 Playoffs",
            "start": "2025-02-15",
            "end": "2025-02-23"
        },
        {
            "name": "LTA South 2025 Split 2",
            "start": "2025-04-05",
            "end": "2025-05-18"
        },
        {
            "name": "LTA South 2025 Split 2 Playoffs",
            "start": "2025-05-24",
            "end": "2025-06-15"
        },
        {
            "name": "MSI 2025",
            "start": "2025-06-27",
            "end": "2025-07-12"
        },
        {
            "name": "Esports World Cup 2025",
            "start": "2025-07-16",
            "end": "2025-07-20"
        },
        {
            "name": "LTA South 2025 Split 3",
            "start": "2025-07-26",
            "end": "2025-09-07"
        },
        {
            "name": "LTA 2025 Championship",
            "start": "2025-09-13",
            "end": "2025-09-28"
        },
    ],

    2026: [
        {
            "name": "CBLOL Cup 2026",
            "start": "2026-01-17",
            "end": "2026-03-01"
        },
        {
            "name": "Americas Cup 2026",
            "start": "2026-03-04",
            "end": "2026-03-08"
        },
        {
            "name": "CBLOL 2026 Split 1",
            "start": "2026-03-28",
            "end": "2026-06-06"
        },
        {
            "name": "MSI 2026",
            "start": "2026-06-28",
            "end": "2026-07-12"
        },
        {
            "name": "Esports World Cup 2026",
            "start": "2026-07-15",
            "end": "2026-07-19"
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
            r"(?:cup|copa)\s*cblol\s*{year}",
        ],

        "split1": [
            r"cblol\s*{year}\s*split\s*1",
            r"cblol\s*split\s*1\s*{year}",
            r"cblol\s*(?:1|1a|1ª|primeira)\s*etapa",
            r"cblol\s*{year}\s*(?:1|1a|1ª|primeira)\s*etapa",
        ],

        "split2": [
            r"cblol\s*{year}\s*split\s*2",
            r"cblol\s*split\s*2\s*{year}",
            r"cblol\s*(?:2|2a|2ª|segunda)\s*etapa",
            r"cblol\s*{year}\s*(?:2|2a|2ª|segunda)\s*etapa",
        ],
    },

    "lta_south": {
        "split1": [
            r"lta\s*(?:south|sul)\s*{year}\s*split\s*1",
            r"lta\s*(?:south|sul)\s*split\s*1\s*{year}",
            r"lta\s*(?:south|sul)\s*(?:1|1a|1ª|primeiro)\s*split",
        ],

        # Playoffs antes do Split normal para evitar
        # correspondência parcial.
        "split2_playoffs": [
            r"lta\s*(?:south|sul)\s*{year}\s*split\s*2\s*playoffs",
            r"lta\s*(?:south|sul)\s*split\s*2\s*playoffs\s*{year}",
            r"playoffs\s*lta\s*(?:south|sul)\s*{year}\s*split\s*2",
        ],

        "split2": [
            r"lta\s*(?:south|sul)\s*{year}\s*split\s*2",
            r"lta\s*(?:south|sul)\s*split\s*2\s*{year}",
            r"lta\s*(?:south|sul)\s*(?:2|2a|2ª|segundo)\s*split",
        ],

        "split3": [
            r"lta\s*(?:south|sul)\s*{year}\s*split\s*3",
            r"lta\s*(?:south|sul)\s*split\s*3\s*{year}",
            r"lta\s*(?:south|sul)\s*(?:3|3a|3ª|terceiro)\s*split",
        ],
    },

    "lta": {
        "split1_playoffs": [
            r"lta\s*{year}\s*split\s*1\s*playoffs",
            r"lta\s*split\s*1\s*playoffs\s*{year}",
        ],

        "championship": [
            r"lta\s*{year}\s*championship",
            r"lta\s*championship\s*{year}",
            r"lta\s*americas\s*{year}\s*championship",
            r"lta\s*americas\s*championship\s*{year}",
        ],
    },

    "americas_cup": {
        "main": [
            r"americas\s*cup\s*{year}",
            r"copa\s*americas\s*{year}",
            r"copa\s*das\s*americas\s*{year}",
        ],
    },

    "msi": {
        "main": [
            r"msi\s*{year}",
            r"mid[\s-]*season\s*invitational\s*{year}",
            r"midseason\s*invitational\s*{year}",
        ],
    },

    "ewc": {
        "main": [
            r"esports\s*world\s*cup\s*{year}",
            r"ewc\s*{year}",
        ],
    },
}


TOURNAMENT_NAMES = {
    "cblol": {
        "cup": "CBLOL Cup {year}",
        "split1": "CBLOL {year} Split 1",
        "split2": "CBLOL {year} Split 2",
    },

    "lta_south": {
        "split1": "LTA South {year} Split 1",
        "split2": "LTA South {year} Split 2",
        "split2_playoffs": "LTA South {year} Split 2 Playoffs",
        "split3": "LTA South {year} Split 3",
    },

    "lta": {
        "split1_playoffs": "LTA {year} Split 1 Playoffs",
        "championship": "LTA {year} Championship",
    },

    "americas_cup": {
        "main": "Americas Cup {year}",
    },

    "msi": {
        "main": "MSI {year}",
    },

    "ewc": {
        "main": "Esports World Cup {year}",
    },
}
