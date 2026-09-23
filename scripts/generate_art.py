#!/usr/bin/env python3
"""Generate light/dark profile art using live contribution data from gh CLI."""

from __future__ import annotations

import json
import math
import subprocess
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
QUERY = '''query {
  user(login: "divyanshchandhok") {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}'''


def nameplate(dark: bool) -> str:
    bg = "#0d1117" if dark else "#ffffff"
    ink = "#f1f3f5" if dark else "#24292f"
    muted = "#9da7b3" if dark else "#66717d"
    edge = "#30363d" if dark else "#d8dee4"
    coral = "#f97355"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="220" viewBox="0 0 840 220" role="img" aria-label="Divyansh Chandhok — engineer by instinct, building with AI">
<rect x="1" y="1" width="838" height="218" rx="15" fill="{bg}" stroke="{edge}"/>
<path d="M21 17h72" stroke="{coral}" stroke-width="3" stroke-linecap="round"/>
<circle cx="39" cy="41" r="4" fill="{coral}"/><circle cx="55" cy="41" r="4" fill="{edge}"/><circle cx="71" cy="41" r="4" fill="{edge}"/>
<text x="102" y="46" fill="{muted}" font-size="12" letter-spacing="2" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">~/divyansh</text>
<text x="38" y="127" fill="{ink}" font-size="65" font-weight="700" letter-spacing="-5" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">divyansh<tspan fill="{coral}">.</tspan></text>
<text x="42" y="169" fill="{muted}" font-size="15" letter-spacing="1.1" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">ENGINEER BY INSTINCT  /  BUILDING WITH AI</text>
<path d="M645 57l76 43-76 43-76-43z" fill="none" stroke="{edge}" stroke-width="2"/>
<path d="M645 57v86M569 100v37l76 43 76-43v-37M645 143v37" fill="none" stroke="{edge}" stroke-width="2"/>
<path d="M645 75l47 26-47 27-47-27z" fill="{coral}" fill-opacity=".12" stroke="{coral}" stroke-width="2"/>
<circle cx="645" cy="101" r="6" fill="{coral}"/>
<path d="M755 38h48M755 46h31M755 54h42" stroke="{edge}" stroke-width="2" stroke-linecap="round"/>
<text x="754" y="181" fill="{coral}" font-size="15" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">01</text>
</svg>'''


def polygon(points: list[tuple[float, float]], fill: str, stroke: str = "none") -> str:
    points_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{points_text}" fill="{fill}" stroke="{stroke}" stroke-width=".7"/>'


def calendar(dark: bool, days: list[dict]) -> str:
    bg = "#0d1117" if dark else "#ffffff"
    ink = "#e6edf3" if dark else "#24292f"
    muted = "#8b949e" if dark else "#6e7781"
    edge = "#30363d" if dark else "#d8dee4"
    empty = "#20262d" if dark else "#e9edf0"
    coral = "#f97355"
    shades = [empty, "#803b35", "#af4c3e", "#d65e49", coral]
    if not dark:
        shades = [empty, "#f9d5c9", "#f5a58d", "#ec795b", "#d9563d"]
    start, end = date.fromisoformat(days[0]["date"]), date.fromisoformat(days[-1]["date"])
    counts = sorted(d["contributionCount"] for d in days if d["contributionCount"] > 0)
    high = counts[int((len(counts) - 1) * .85)] if counts else 1
    title = f'{start.strftime("%b").upper()}—{end.strftime("%b %Y").upper()}'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="840" height="335" viewBox="0 0 840 335" role="img" aria-label="Isometric calendar of GitHub contributions from {start} to {end}">',
             f'<rect x="1" y="1" width="838" height="333" rx="15" fill="{bg}" stroke="{edge}"/>',
             f'<text x="35" y="43" fill="{ink}" font-size="18" font-weight="700" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">commit geometry<tspan fill="{coral}">.</tspan></text>',
             f'<text x="805" y="42" text-anchor="end" fill="{muted}" font-size="12" letter-spacing="1" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">{escape(title)}</text>']
    first_sunday = start - timedelta(days=(start.weekday() + 1) % 7)
    tiles = []
    for d in days:
        day = date.fromisoformat(d["date"])
        week = (day - first_sunday).days // 7
        dow = (day.weekday() + 1) % 7
        count = d["contributionCount"]
        level = min(4, max(1, math.ceil(count / max(1, high) * 4))) if count else 0
        height = 2 + min(23, math.sqrt(count) * 4) if count else 2
        x = 121 + week * 21.5 - dow * 12
        y = 93 + week * 5.7 + dow * 8.5
        tiles.append((week + dow, x, y, height, shades[level]))
    for _, x, y, h, color in sorted(tiles):
        top = [(x, y-h), (x+11, y+5.5-h), (x, y+11-h), (x-11, y+5.5-h)]
        left = [(x-11, y+5.5-h), (x, y+11-h), (x, y+11), (x-11, y+5.5)]
        right = [(x, y+11-h), (x+11, y+5.5-h), (x+11, y+5.5), (x, y+11)]
        parts.extend([polygon(left, color, bg), polygon(right, color, bg), polygon(top, color, bg)])
    parts += [f'<text x="35" y="307" fill="{muted}" font-size="11" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">GITHUB CONTRIBUTIONS · SNAPSHOT {end.isoformat()}</text>',
              f'<text x="805" y="307" text-anchor="end" fill="{muted}" font-size="11" font-family="ui-monospace,SFMono-Regular,Consolas,monospace">inspired by lowlighter/metrics</text>', '</svg>']
    return "\n".join(parts)


def main() -> None:
    result = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={QUERY}"], text=True)
    data = json.loads(result)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [day for week in weeks for day in week["contributionDays"]]
    end = date.today()
    days = [day for day in days if end - timedelta(days=179) <= date.fromisoformat(day["date"]) <= end]
    for dark in (True, False):
        theme = "dark" if dark else "light"
        (ASSETS / f"nameplate-{theme}.svg").write_text(nameplate(dark))
        (ASSETS / f"isocalendar-{theme}.svg").write_text(calendar(dark, days))


if __name__ == "__main__":
    main()
