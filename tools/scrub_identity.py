#!/usr/bin/env python3
"""Cloudflare Pages 사본에서 개인 식별 정보(계정명·저장소 링크)를 지운다.

  scrub_identity.py <deploy_dir> <public_url>
"""
import re
import sys
from pathlib import Path

GH_PAGES = "https://kimhs950627.github.io/ecg-echo"
REPO_LINK = '<a href="https://github.com/kimhs950627/ecg-echo">github.com/kimhs950627/ecg-echo</a>'
REPO_TEXT = "github.com/kimhs950627/ecg-echo"

d = Path(sys.argv[1])
base = sys.argv[2].rstrip("/")

edits = 0
for f in list(d.rglob("*.html")) + list(d.rglob("*.xml")) + list(d.rglob("*.txt")) + list(d.rglob("*.json")) + list(d.rglob("*.js")):
    t = f.read_text(encoding="utf-8")
    o = t
    t = t.replace(REPO_LINK, "익명 공개 · 코드 비공개")
    t = t.replace(REPO_TEXT, "익명 공개")
    t = t.replace(GH_PAGES, base)
    t = re.sub(r"kimhs950627", "anon", t)
    if t != o:
        f.write_text(t, encoding="utf-8")
        edits += 1

# 남은 게 있으면 알린다
left = [str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and p.suffix in {".html", ".xml", ".txt", ".json", ".js"} and "kimhs950627" in p.read_text(encoding="utf-8", errors="ignore")]
print(f"scrubbed {edits} files | residuals: {left if left else 'none'}")
