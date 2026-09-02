"""Phase 2: perform a genuine reverse-image search and save evidence."""

import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, SERPAPI_API_KEY
from .reverse_image_search import search_image

OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RESULT_PATH = OUTPUT_DIR / "phase2_result.json"


def run_phase2(image_path: str) -> dict[str, Any]:
    """Run Google Lens through SerpApi and persist returned search evidence."""
    print("[1/3] Loading image...")
    image_file = Path(image_path)
    if not image_file.is_file():
        raise FileNotFoundError(f"Input image does not exist: {image_path}")
    image_file.read_bytes()
    print("      OK Image loaded")

    print("[2/3] Running genuine reverse-image search...")
    results = search_image(image_path, SERPAPI_API_KEY)
    print("      OK Google Lens search completed")

    print("[3/3] Processing search results...")
    social_media_match = next(
        (result for result in results if result["is_social_media"]), None
    )
    result = {
        "phase": 2,
        "search_performed": True,
        "search_engine": "Google Lens via SerpApi",
        "input_image": image_path,
        "result_count": len(results),
        "social_media_match_found": social_media_match is not None,
        "results": results,
    }
    if social_media_match is not None:
        result["social_media_match"] = {
            field: social_media_match[field]
            for field in ("title", "url", "domain")
            if field in social_media_match
        }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("      OK Results processed")
    print(f"\nSearch engine    : Google Lens via SerpApi")
    print(f"Results found    : {len(results)}")
    print(f"Social match     : {'YES' if social_media_match is not None else 'NO'}")
    if social_media_match is not None:
        print("\nSocial result:")
        print(f"Title            : {social_media_match.get('title', '(untitled)')}")
        print(f"URL              : {social_media_match['url']}")
        print(f"Domain           : {social_media_match['domain']}")
    print("\n------------------------------------------------------------")
    print("PHASE 2 COMPLETE")
    print("------------------------------------------------------------")
    print("\nResult saved     : data/output/phase2_result.json")
    return result
