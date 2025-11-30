import os
import base64
import io
from typing import Dict, Any

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Main labels your system understands
GSCHOOL_LABELS = [
    "explicit_nudity",
    "partial_nudity",
    "suggestive",
    "violence",
    "weapon",
    "self_harm",
    "other",
]


def _extract_image_input(image_data_url_or_bytes: Any) -> Dict[str, Any]:
    """
    Build the 'input' field for OpenAI moderation.

    If you are passing an image URL from the extension, you can send:
      { "type": "image_url", "image_url": { "url": "https://..." } }

    If you're passing a data URL (data:image/png;base64,...), we
    can strip the header and send as base64.

    Here we assume the extension is sending a data URL string.
    """
    if isinstance(image_data_url_or_bytes, str):
        # Expect something like: "data:image/png;base64,AAAA..."
        if "," in image_data_url_or_bytes:
            header, b64 = image_data_url_or_bytes.split(",", 1)
        else:
            # Already just base64
            b64 = image_data_url_or_bytes

        # You can either send as bytes or use image_url w/ base64:
        # The moderation API example in your docs mainly shows image_url with URL.
        # For safety & clarity, let's use image_url with a "data:" URL.
        data_url = f"data:image/png;base64,{b64}"
        return {
            "type": "image_url",
            "image_url": {
                "url": data_url
            }
        }

    # If you somehow get raw bytes, you could also encode them:
    if isinstance(image_data_url_or_bytes, (bytes, bytearray)):
        b64 = base64.b64encode(image_data_url_or_bytes).decode("ascii")
        data_url = f"data:image/png;base64,{b64}"
        return {
            "type": "image_url",
            "image_url": {
                "url": data_url
            }
        }

    # Fallback – no image
    return None


def _map_openai_scores_to_gschool(scores: Dict[str, float]) -> Dict[str, float]:
    sexual = float(scores.get("sexual", 0.0) or 0.0)
    self_harm_raw = max(
        float(scores.get("self-harm", 0.0) or 0.0),
        float(scores.get("self-harm/intent", 0.0) or 0.0),
        float(scores.get("self-harm/instructions", 0.0) or 0.0),
    )
    violence = float(scores.get("violence", 0.0) or 0.0)
    graphic = float(scores.get("violence/graphic", 0.0) or 0.0)

    explicit_nudity = sexual
    partial_nudity = min(1.0, sexual * 0.9)
    suggestive = min(1.0, sexual * 0.8)
    violence_score = max(violence, graphic)
    weapon_score = violence_score  # approx; can refine later

    out = {
        "explicit_nudity": explicit_nudity,
        "partial_nudity": partial_nudity,
        "suggestive": suggestive,
        "violence": violence_score,
        "weapon": weapon_score,
        "self_harm": self_harm_raw,
        "other": 0.0,
    }

    # Ensure all labels exist
    for k in GSCHOOL_LABELS:
        out.setdefault(k, 0.0)

    return out


def classify_image_with_openai(
    image_data_url_or_bytes: Any,
    *,
    page_url: str = "",
    src_url: str = "",
    block_threshold: float = 0.3,
) -> Dict[str, Any]:
    """
    Call OpenAI omni-moderation-latest on an image (and optional text context),
    map its scores to G-School categories, and return a suggested action.
    """
    img_input = _extract_image_input(image_data_url_or_bytes)
    if not img_input:
        # No image – allow by default but mark other slightly
        scores = {k: 0.0 for k in GSCHOOL_LABELS}
        scores["other"] = 0.01
        return {
            "ok": True,
            "action": "allow",
            "scores": scores,
            "reason": "no_image",
        }

    # Build combined input: optional text context + the image
    inputs = []
    text_ctx = (page_url or "") + " " + (src_url or "")
    if text_ctx.strip():
        inputs.append({"type": "text", "text": text_ctx.strip()})
    inputs.append(img_input)

    try:
        resp = client.moderations.create(
            model="omni-moderation-latest",
            input=inputs,
        )
    except Exception as e:
        # If the moderation API fails, fail-open or fail-closed depending on your preference.
        # In school context it's safer to fail CLOSED (block) for suspicious sources.
        scores = {k: 0.0 for k in GSCHOOL_LABELS}
        return {
            "ok": False,
            "action": "block",
            "scores": scores,
            "reason": f"openai_error: {e}",
        }

    if not resp or not getattr(resp, "results", None):
        scores = {k: 0.0 for k in GSCHOOL_LABELS}
        return {
            "ok": False,
            "action": "block",
            "scores": scores,
            "reason": "openai_no_results",
        }

    r0 = resp.results[0]
    raw_scores = dict(r0.category_scores or {})
    mapped = _map_openai_scores_to_gschool(raw_scores)

    max_label = max(mapped, key=lambda k: mapped[k])
    max_val = mapped[max_label]

    action = "block" if max_val >= float(block_threshold) else "allow"

    reason = f"openai: {max_label}={max_val:.3f}"

    return {
        "ok": True,
        "action": action,
        "scores": mapped,
        "reason": reason,
        "openai_flagged": bool(r0.flagged),
    }
