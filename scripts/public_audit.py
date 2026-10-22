#!/usr/bin/env python3
"""Run lightweight checks before publishing this historical CTF archive."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "THIRD_PARTY_NOTICES.md",
}
JUNK_NAMES = {".DS_Store", ".gdb_history"}
JUNK_SUFFIXES = {".id0", ".id1", ".id2", ".i64", ".nam", ".til"}
SECRET_PATTERNS = {
    "private key": re.compile(rb"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY"),
    "GitHub token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    "GitHub fine-grained token": re.compile(rb"github_pat_[A-Za-z0-9_]{40,}"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "Slack token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]


def main() -> int:
    files = tracked_files()
    errors: list[str] = []
    warnings: list[str] = []

    for required in sorted(REQUIRED):
        if not (ROOT / required).is_file():
            errors.append(f"missing public repository file: {required}")

    for path in files:
        rel = path.relative_to(ROOT)
        # 爬取的第三方文章归档：正文与代码块为原文内容，链接不是仓库导航，跳过内容审计
        if rel.parts[:2] == ("2023夏季ctf小学期PPT", "CTF文章"):
            continue
        if path.name in JUNK_NAMES or "__pycache__" in rel.parts or path.suffix in JUNK_SUFFIXES:
            errors.append(f"tracked generated/editor artifact: {rel}")
        if path.stat().st_size > 600 * 1024 * 1024:  # 归档含赛题大附件，上限从 25MiB 调整
            errors.append(f"file exceeds 600 MiB publication limit: {rel}")
        elif path.stat().st_size > 50 * 1024 * 1024:
            warnings.append(f"large historical artifact (>50 MiB): {rel}")

        if path.suffix.lower() not in {".md", ".py", ".sh", ".yml", ".yaml", ".json", ".txt"}:
            continue
        data = path.read_bytes()
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                errors.append(f"possible {label}: {rel}")

        if path.suffix.lower() != ".md":
            continue
        text = data.decode("utf-8", errors="replace")
        for target in MARKDOWN_LINK.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            candidate = (path.parent / unquote(target)).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"link escapes repository: {rel} -> {target}")
                continue
            try:
                link_ok = candidate.exists()
            except OSError as exc:
                errors.append(f"unreadable link target ({exc.strerror}): {rel} -> {target[:80]}")
                continue
            if not link_ok:
                errors.append(f"broken relative link: {rel} -> {target}")

    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    print(f"audited {len(files)} tracked files: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
