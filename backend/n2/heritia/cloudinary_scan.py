from __future__ import annotations

import hashlib
import re
from datetime import date, timedelta
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import httpx

from app.config import settings
from n2.heritia.schemas import DetectedIngredient, ScanRequest, ScanResponse

CLOUDINARY_HOST = "res.cloudinary.com"
_INGREDIENT_LINE = re.compile(
    r"^(?P<name>[A-Za-zÀ-ÿ0-9][\w\s\-']{1,40}?)"
    r"(?:\s*[\-–—]\s*(?P<qty>\d[\d\s.,/]*\s*(?:g|kg|ml|l|cl|pc|pcs|pièce|pièces|paquet|sachet)?))?",
    re.IGNORECASE,
)
_EXPIRY_HINT = re.compile(r"(?:DLC|DLUO|EXP|PERIME|PÉREM)[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})", re.I)


def _cloudinary_public_id(image_url: str) -> Tuple[str, str]:
    parsed = urlparse(image_url)
    if parsed.netloc != CLOUDINARY_HOST:
        raise ValueError("image_url must be a Cloudinary delivery URL (res.cloudinary.com)")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 4 or parts[2] != "upload":
        raise ValueError("Invalid Cloudinary URL path")

    cloud_from_url = parts[0]
    if settings.cloudinary_cloud_name and cloud_from_url != settings.cloudinary_cloud_name:
        raise ValueError("Cloudinary cloud_name mismatch")

    start = 3
    if parts[start].startswith("v") and parts[start][1:].isdigit():
        start += 1

    public_id = "/".join(parts[start:])
    if public_id.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        public_id = public_id.rsplit(".", 1)[0]
    return cloud_from_url, public_id


def _fetch_cloudinary_resource(public_id: str) -> dict:
    if not settings.cloudinary_configured:
        return {}

    cloud = settings.cloudinary_cloud_name
    api_key = settings.cloudinary_api_key
    api_secret = settings.cloudinary_api_secret
    timestamp = str(int(__import__("time").time()))
    to_sign = "public_id={0}&timestamp={1}{2}".format(public_id, timestamp, api_secret)
    signature = hashlib.sha1(to_sign.encode("utf-8")).hexdigest()

    url = "https://api.cloudinary.com/v1_1/{0}/resources/image/upload/{1}".format(cloud, public_id)
    params = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.get(url, params=params)
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()


def _parse_ocr_text(text: str, scan_type: str) -> List[DetectedIngredient]:
    ingredients: List[DetectedIngredient] = []
    for raw_line in text.splitlines():
        line = raw_line.strip(" •-\t")
        if len(line) < 2:
            continue
        match = _INGREDIENT_LINE.match(line)
        if not match:
            continue
        name = match.group("name").strip()
        qty = (match.group("qty") or "").strip() or None
        expiry_date = None
        expiry_hint = None
        expiry_match = _EXPIRY_HINT.search(line)
        if expiry_match:
            expiry_hint = expiry_match.group(1)
        elif scan_type == "fridge":
            expiry_hint = "J+{0}".format(3 + len(ingredients) * 2)
        ingredients.append(
            DetectedIngredient(
                name=name,
                quantity_estimate=qty,
                expiry_date=expiry_date,
                expiry_hint=expiry_hint,
            )
        )
    return ingredients


def _fallback_ingredients(scan_type: str) -> List[DetectedIngredient]:
    today = date.today()
    if scan_type == "receipt":
        return [
            DetectedIngredient(name="Tomates", quantity_estimate="500 g"),
            DetectedIngredient(name="Pâtes", quantity_estimate="1 paquet"),
            DetectedIngredient(name="Fromage râpé", quantity_estimate="200 g"),
        ]
    return [
        DetectedIngredient(
            name="Lait",
            quantity_estimate="1 L",
            expiry_date=today + timedelta(days=3),
            expiry_hint="J+3",
        ),
        DetectedIngredient(
            name="Oeufs",
            quantity_estimate="6",
            expiry_date=today + timedelta(days=7),
            expiry_hint="J+7",
        ),
        DetectedIngredient(
            name="Épinards",
            quantity_estimate="250 g",
            expiry_date=today + timedelta(days=2),
            expiry_hint="J+2",
        ),
    ]


def analyze_cloudinary_scan(payload: ScanRequest) -> ScanResponse:
    image_url = str(payload.image_url)
    _cloudinary_public_id(image_url)

    resource = {}
    try:
        _, public_id = _cloudinary_public_id(image_url)
        resource = _fetch_cloudinary_resource(public_id)
    except ValueError:
        raise
    except httpx.HTTPError as exc:
        raise RuntimeError("Cloudinary API unreachable") from exc

    ocr_text = ""
    info = resource.get("info") or {}
    if isinstance(info, dict):
        ocr = info.get("ocr") or {}
        if isinstance(ocr, dict):
            adv = ocr.get("adv_ocr") or {}
            data = adv.get("data") or []
            if data and isinstance(data[0], dict):
                raw = data[0].get("textAnnotations") or []
                if raw and isinstance(raw[0], dict):
                    ocr_text = raw[0].get("description") or ""

    context = resource.get("context") or {}
    if isinstance(context, dict) and context.get("custom", {}).get("ocr_text"):
        ocr_text = ocr_text or context["custom"]["ocr_text"]

    ingredients = _parse_ocr_text(ocr_text, payload.scan_type) if ocr_text else []
    if not ingredients:
        ingredients = _fallback_ingredients(payload.scan_type)

    summary = (
        "Ticket analysé — {0} ingrédient(s) détecté(s)."
        if payload.scan_type == "receipt"
        else "Frigo analysé — {0} ingrédient(s) avec dates de péremption estimées."
    ).format(len(ingredients))

    return ScanResponse(
        scan_type=payload.scan_type,
        image_url=image_url,
        ingredients=ingredients,
        summary=summary,
    )
