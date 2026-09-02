"""Genuine reverse-image search using SerpApi Google Lens."""

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from PIL import Image
import requests

from .config import PROJECT_ROOT

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
SERPAPI_IMAGE_ENDPOINT = "https://serpapi.com/image"
SOCIAL_MEDIA_DOMAINS = {
    "instagram.com",
    "facebook.com",
    "x.com",
    "twitter.com",
    "tiktok.com",
    "linkedin.com",
    "threads.net",
}


class ReverseImageSearchError(RuntimeError):
    """Raised when reverse-image search cannot produce valid results."""


def _domain_from_url(url: str) -> str:
    hostname = urlparse(url).hostname
    if not hostname:
        return ""
    return hostname.lower().removeprefix("www.")


def _is_social_media_domain(domain: str) -> bool:
    return domain in SOCIAL_MEDIA_DOMAINS or any(
        domain.endswith(f".{social_domain}") for social_domain in SOCIAL_MEDIA_DOMAINS
    )


def _parse_result(raw_result: dict[str, Any]) -> dict[str, Any] | None:
    url = raw_result.get("link") or raw_result.get("url")
    if not isinstance(url, str) or not url:
        return None

    result: dict[str, Any] = {
        "title": raw_result["title"]
        if isinstance(raw_result.get("title"), str)
        else "",
        "url": url,
        "domain": _domain_from_url(url),
        "is_social_media": _is_social_media_domain(_domain_from_url(url)),
    }
    if not result["title"]:
        result.pop("title")
    if isinstance(raw_result.get("thumbnail"), str):
        result["thumbnail"] = raw_result["thumbnail"]
    if isinstance(raw_result.get("source"), str):
        result["source"] = raw_result["source"]
    if isinstance(raw_result.get("type"), str):
        result["type"] = raw_result["type"]
    elif isinstance(raw_result.get("category"), str):
        result["category"] = raw_result["category"]
    return result


def search_image(image_path: str, api_key: str | None = None) -> list[dict[str, Any]]:
    """Upload a local image to SerpApi Google Lens and parse returned matches."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input image does not exist: {image_path}")

    try:
        with Image.open(path) as image:
            image.verify()
    except (OSError, Image.UnidentifiedImageError) as error:
        raise ReverseImageSearchError(
            f"Could not open input image: {image_path}"
        ) from error

    key = api_key
    if not key:
        raise ReverseImageSearchError(
            "SERPAPI_API_KEY is missing. Add it to the .env file."
        )

    try:
        image_bytes = path.read_bytes()
    except OSError as error:
        raise ReverseImageSearchError(
            f"Could not read input image: {image_path}"
        ) from error

    try:
        upload_response = requests.post(
            SERPAPI_IMAGE_ENDPOINT,
            data={"api_key": key},
            files={"image": (path.name, image_bytes)},
            timeout=60,
        )
        upload_response.raise_for_status()
        upload_payload = upload_response.json()
        if not isinstance(upload_payload, dict):
            raise ReverseImageSearchError("SerpApi returned an invalid upload response")
        image_id = upload_payload.get("image_id")
        if not isinstance(image_id, str) or not image_id:
            raise ReverseImageSearchError("SerpApi did not return an image ID")

        response = requests.get(
            SERPAPI_ENDPOINT,
            params={
                "engine": "google_lens",
                "image_id": image_id,
                "api_key": key,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise ReverseImageSearchError("SerpApi request failed") from error
    except ValueError as error:
        raise ReverseImageSearchError("SerpApi returned invalid JSON") from error

    if not isinstance(payload, dict):
        raise ReverseImageSearchError("SerpApi returned an invalid response object")
    if isinstance(payload.get("error"), str):
        raise ReverseImageSearchError(f"SerpApi returned an error: {payload['error']}")
    raw_results = payload.get("visual_matches")
    if not isinstance(raw_results, list):
        raise ReverseImageSearchError("SerpApi returned invalid visual_matches data")

    return [
        parsed
        for raw_result in raw_results
        if isinstance(raw_result, dict)
        for parsed in [_parse_result(raw_result)]
        if parsed is not None
    ]
