#!/usr/bin/env python3
"""
generate_projects.py — tarik semua repo GitHub lalu render kartu proyek
ke dalam index.html di antara marker <!-- PROJECTS:START --> dan <!-- PROJECTS:END -->.

Pakai:
    python3 generate_projects.py                 # semua repo (public + private)
    python3 generate_projects.py --public-only   # hanya repo public
    python3 generate_projects.py --user lain     # user/org lain

Token diambil otomatis dari `gh auth token`, atau env GITHUB_TOKEN / GH_TOKEN.
Tanpa token: hanya repo public, rate limit 60/jam.
"""

import argparse
import html
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
SKIP_REPOS = {"Rickyyy9.github.io"}  # jangan tampilkan repo portofolio itu sendiri


def get_token() -> str | None:
    for env in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(env):
            return os.environ[env]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return None


def api(url: str, token: str | None):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "portfolio-generator",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_repos(user: str, token: str | None, public_only: bool) -> list[dict]:
    if public_only or not token:
        return api(f"https://api.github.com/users/{user}/repos?per_page=100&sort=pushed", token)
    return api("https://api.github.com/user/repos?affiliation=owner&per_page=100&sort=pushed", token)


def placeholder_svg(name: str) -> str:
    label = html.escape(name[:28])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%" stop-color="#2c3e50"/><stop offset="100%" stop-color="#3498db"/>'
        "</linearGradient></defs>"
        '<rect width="600" height="400" fill="url(#g)"/>'
        f'<text x="300" y="210" font-family="sans-serif" font-size="34" fill="#ffffff" '
        f'text-anchor="middle">{label}</text>'
        "</svg>"
    )
    from urllib.parse import quote
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


def render_card(repo: dict) -> str:
    name = html.escape(repo["name"])
    desc = repo.get("description") or "Belum ada deskripsi."
    desc = html.escape(desc)
    lang = repo.get("language") or "—"
    private = repo.get("private", False)
    url = repo["html_url"]
    full = repo["full_name"]

    img = placeholder_svg(repo["name"]) if private else f"https://opengraph.githubassets.com/1/{full}"
    badge = '<span class="badge private">Private</span>' if private else f'<span class="badge">{html.escape(lang)}</span>'
    action = (
        '<span class="btn disabled">Repo Privat</span>'
        if private
        else f'<a href="{url}" class="btn" target="_blank" rel="noopener">Lihat di GitHub</a>'
    )

    return f"""                <div class="project-card">
                    <img src="{img}" alt="{name}" loading="lazy">
                    {badge}
                    <h3>{name}</h3>
                    <p>{desc}</p>
                    {action}
                </div>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="Rickyyy9")
    ap.add_argument("--public-only", action="store_true")
    args = ap.parse_args()

    token = get_token()
    try:
        repos = fetch_repos(args.user, token, args.public_only)
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code}: {e.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Koneksi gagal: {e.reason}", file=sys.stderr)
        return 1

    repos = [r for r in repos if r["name"] not in SKIP_REPOS]
    repos.sort(key=lambda r: (r.get("pushed_at") or ""), reverse=True)

    cards = "\n".join(render_card(r) for r in repos) or "                <p>Belum ada repository.</p>"

    page = INDEX.read_text(encoding="utf-8")
    if START not in page or END not in page:
        print(f"Marker {START} / {END} tidak ditemukan di {INDEX}", file=sys.stderr)
        return 1
    head, rest = page.split(START, 1)
    _, tail = rest.split(END, 1)
    INDEX.write_text(f"{head}{START}\n{cards}\n                {END}{tail}", encoding="utf-8")

    pub = sum(1 for r in repos if not r.get("private"))
    print(f"OK: {len(repos)} repo dirender ({pub} public, {len(repos)-pub} private) -> {INDEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
