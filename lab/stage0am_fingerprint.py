"""Recompute Stage 0A-M battery fingerprints from the committed artifacts.

The battery was originally assembled by a one-shot script that lived outside the
repository. That made the manifest's fingerprints unreproducible: nothing in the
repository could regenerate them, so nothing could detect a hand-edit of a key.

This module closes that gap. It derives every fingerprint from
``batteries/anchored_v1.yaml`` and ``batteries/answers.anchored_v1.yaml`` alone,
using the original algorithm, so the manifest can be checked against the files it
claims to describe. The test suite asserts the two agree.

Nothing here dispatches, and nothing here reads a solver answer.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
BATTERY_PATH = REPO / "batteries" / "anchored_v1.yaml"
KEYS_PATH = REPO / "batteries" / "answers.anchored_v1.yaml"
MANIFEST_PATH = REPO / "experiments" / "exp004_stage0am" / "manifest.json"


def fingerprint(obj: Any) -> str:
    """The frozen fingerprint function: first 16 hex chars of a sorted-key SHA-256."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def load() -> tuple[list[dict], dict]:
    battery = yaml.safe_load(BATTERY_PATH.read_text())
    keys = yaml.safe_load(KEYS_PATH.read_text())["answers"]
    return battery["questions"], keys


def key_fingerprints(questions: list[dict], keys: dict) -> dict[str, str]:
    return {q["id"]: fingerprint(keys[q["id"]]) for q in questions}


def battery_fingerprint(questions: list[dict], keys: dict) -> str:
    """Covers both the stems and the keys, so a change to either moves it."""
    fps = key_fingerprints(questions, keys)
    return fingerprint({"q": [(q["id"], q["text"]) for q in questions], "k": fps})


def audit() -> dict:
    """Compare the manifest against the battery files it describes."""
    questions, keys = load()
    manifest = json.loads(MANIFEST_PATH.read_text())
    fps = key_fingerprints(questions, keys)
    recomputed = battery_fingerprint(questions, keys)
    drifted = [
        {"id": item["id"], "manifest": item["key_fingerprint"], "recomputed": fps[item["id"]]}
        for item in manifest["items"]
        if item["key_fingerprint"] != fps[item["id"]]
    ]
    return {
        "battery_fingerprint_recomputed": recomputed,
        "battery_fingerprint_in_manifest": manifest["battery_fingerprint"],
        "battery_fingerprint_matches": recomputed == manifest["battery_fingerprint"],
        "drifted_keys": drifted,
        "items_in_manifest": len(manifest["items"]),
        "items_in_battery": len(questions),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=1))
