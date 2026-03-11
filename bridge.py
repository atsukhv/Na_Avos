"""
bridge.py — Python API доступный из JS через window.pywebview.api
"""

import json
import random
import sys
from pathlib import Path


def _storage_dir() -> tuple[Path, bool]:
    """
    Возвращает (путь, была_ли_создана_сейчас).
    Windows: ~/Documents/RandomizerTemplates/
    Mac:     ~/Documents/RandomizerTemplates/
    Linux:   ~/.local/share/RandomizerTemplates/
    """
    if sys.platform in ("win32", "darwin"):
        base = Path.home() / "Documents"
    else:
        base = Path.home() / ".local" / "share"

    d = base / "RandomizerTemplates"
    just_created = not d.exists()
    d.mkdir(parents=True, exist_ok=True)
    return d, just_created


STORAGE_DIR, _JUST_CREATED = _storage_dir()
_STORAGE_PATH_STR = str(STORAGE_DIR)


class Bridge:

    def get_storage_info(self) -> str:
        """Возвращает путь к папке и флаг — была ли только что создана."""
        return json.dumps({
            "path": _STORAGE_PATH_STR,
            "just_created": _JUST_CREATED,
        }, ensure_ascii=False)

    def get_lists(self) -> str:
        result = {}
        for file in sorted(STORAGE_DIR.glob("*.json")):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    result[file.stem] = json.load(f)
            except Exception:
                pass
        return json.dumps(result, ensure_ascii=False)

    def save_list(self, name: str, items_json: str) -> str:
        try:
            name = name.strip()
            if not name:
                return json.dumps({"error": "Пустое название"})
            items = json.loads(items_json)
            with open(STORAGE_DIR / f"{name}.json", "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            return json.dumps({"ok": True})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def delete_list(self, name: str) -> str:
        try:
            path = STORAGE_DIR / f"{name}.json"
            if path.exists():
                path.unlink()
            return json.dumps({"ok": True})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def weighted_choice(self, items_json: str) -> str:
        try:
            items = json.loads(items_json)
            if not items:
                return ""
            weights = [float(item.get("weight", 1.0)) for item in items]
            return random.choices(items, weights=weights, k=1)[0]["name"]
        except Exception:
            return ""

    def coin_flip(self) -> str:
        return random.choice(["Орёл", "Решка"])