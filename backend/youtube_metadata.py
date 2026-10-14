import os
import re
import requests


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def extract_youtube_id(url):
    if not isinstance(url, str):
        return None
    patterns = [
        r"(?:youtube\.com/watch\?v=)([^&?/]+)",
        r"(?:youtu\.be/)([^&?/]+)",
        r"(?:youtube\.com/embed/)([^&?/]+)",
        r"(?:youtube\.com/shorts/)([^&?/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match and re.fullmatch(r"[A-Za-z0-9_-]{6,20}", match.group(1)):
            return match.group(1)

    return None


def get_youtube_metadata(url):
    video_id = extract_youtube_id(url)

    if not video_id:
        return {
            "error": "URL do YouTube inválida"
        }

    if not YOUTUBE_API_KEY:
        return {
            "error": "YOUTUBE_API_KEY não configurada"
        }

    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,contentDetails,statistics",
                    "id": video_id,
                    "key": YOUTUBE_API_KEY
                },
                timeout=15
            )
            response.raise_for_status()
    except requests.RequestException:
        # Do not chain: the original message includes the request URL and key.
        raise requests.RequestException(
            "Erro ao consultar metadados do YouTube."
        ) from None

    data = response.json()

    if not data.get("items"):
        return {
            "error": "Vídeo não encontrado"
        }

    video = data["items"][0]

    snippet = video.get("snippet", {})
    content = video.get("contentDetails", {})
    statistics = video.get("statistics", {})

    return {
        "platform": "YouTube",
        "url": url,
        "video_id": video_id,

        "title": snippet.get("title"),
        "description": snippet.get("description"),

        "channel": snippet.get("channelTitle"),
        "channel_id": snippet.get("channelId"),

        "published_at": snippet.get("publishedAt"),
        "tags": snippet.get("tags", []),

        "duration": content.get("duration"),
        "captions_available": content.get("caption") == "true",

        "view_count": statistics.get("viewCount"),
        "like_count": statistics.get("likeCount"),

        "isvideo": True
    }
