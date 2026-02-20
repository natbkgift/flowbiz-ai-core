from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _iter_repo_files() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        output = subprocess.check_output(
            ["git", "ls-files"], cwd=repo_root, text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        # Fallback: scan the most likely directories (keeps the test fast)
        candidates = []
        for base in ("docs", "scripts", ".github"):
            base_path = repo_root / base
            if base_path.exists():
                candidates.extend([p for p in base_path.rglob("*") if p.is_file()])
        return candidates

    paths: list[Path] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        path = repo_root / line
        if path.is_file():
            paths.append(path)
    return paths


@pytest.mark.parametrize(
    "bad_substring",
    [
        "\u0e41" + "ssh",
        "~/" + "\u0e41" + "ssh",
        "\\" + "\u0e41" + "ssh",
        "\u0e41" + ".ssh",
        "\u0e41" + "\\.ssh",
    ],
)
def test_repo_does_not_contain_thai_ssh_typo(bad_substring: str) -> None:
    """
    Prevent the common typo where `.ssh` becomes `\u0e41ssh` when the '.' key is typed
    while a Thai keyboard layout is active.
    """
    offenders: list[str] = []
    for path in _iter_repo_files():
        # Avoid scanning huge or binary-ish files.
        try:
            if path.stat().st_size > 2_000_000:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if bad_substring in content:
            offenders.append(str(path))

    assert offenders == [], f"Found '{bad_substring}' in: {', '.join(offenders)}"

