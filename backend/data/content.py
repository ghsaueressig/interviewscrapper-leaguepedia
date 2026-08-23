import re


STOPWORDS = [
    'Diz', 'Sobre', 'Para', 'Com', 'Pelo', 'Pela', 'Das', 'Dos',
    'Nas', 'Nos', 'Uma', 'Gente', 'Apos', 'Nada', 'Hoje', 'Isso',
    'Esta', 'Tava', 'Tudo', 'Mais', 'Seu', 'Sua', 'Como', 'Pode',
    'Sido', 'Erro', 'Parte', 'Dessa', 'Troca', 'Acho', 'Seja',
    'Por', 'Vitoria', 'Seguida', 'Decima', 'Derrota', 'Momento',
    'Bastidores', 'Turbulento', 'Confira', 'Completa', 'Coletiva',
    'Desabafo', 'Criticas', 'Estilo', 'Ninguem', 'Mundo', 'Cansado',
    'Narrativa', 'Ontem', 'Talvez', 'Minha', 'Sentir', 'Tempo',
    'Preparacao', 'Outros', 'Pensam', 'Mudar', 'Renovar', 'Pior',
    'Liga', 'Unido', 'Querer', 'Fazer', 'Acontecer', 'Lugar',
    'Cabeca', 'Cinco', 'Nenhum'
]


INTERVIEW_TITLE_MARKERS = (
    "diz",
    "afirma",
    "fala",
    "conta",
    "revela",
    "comenta",
    "explica",
    "avalia",
    "detalha",
    "admite",
    "destaca",
    "comenta sobre"
)


ARTICLE_TITLE_MARKERS = (
    "confira",
    "resultado",
    "classificação",
    "tabela",
    "calendário",
    "anuncia",
    "anunciado",
    "contrata",
    "contratação",
    "escalação",
    "line-up",
    "roster",
    "mercado",
    "rumor"
)


TRANSLATOR_PATTERNS = [
    re.compile(
        r"(?:tradu[cç][aã]o|traduzido|traduzida|translator|translation)"
        r"\s*(?:por|by|:)?\s*([A-ZÀ-Ý][^.!?\n]{1,80})",
        re.I
    ),
]


YOUTUBE_INTERVIEW_PATTERNS = [
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


YOUTUBE_ARTICLE_PATTERNS = [
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
