"""Local Command Center ops dashboard — stdlib only.

Reads command-center markdown + vault paths, serves HTML at 127.0.0.1.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import webbrowser
from dataclasses import dataclass
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from vault_paths import COMMAND_CENTER, CONTENT_DIR, RAW_DIR, REPO_ROOT, VAULT_ROOT, WIKI_DIR

GITHUB_URL = "https://github.com/jockthompsongit/ms_ai_cc"
COURSE_PREFIX = "AI 5100"
MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


@dataclass
class FocusItem:
    done: bool
    text: str


@dataclass
class CalendarRow:
    week_label: str
    week_num: int | None
    dates: str
    theme: str
    sync: str
    async_: str
    start: date | None
    end: date | None
    is_current: bool = False


@dataclass
class CaptureStatus:
    week: int
    content: bool
    sessions: bool
    raw: bool
    lecture: bool


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def section_body(md: str, heading: str) -> str:
    """Return markdown body under ## heading until next ## or EOF."""
    pattern = rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)"
    m = re.search(pattern, md)
    return m.group(1).strip() if m else ""


def parse_checklist(md_section: str) -> list[FocusItem]:
    items: list[FocusItem] = []
    for line in md_section.splitlines():
        m = re.match(r"^-\s+\[([ xX])\]\s+(.*)$", line.strip())
        if not m:
            continue
        items.append(FocusItem(done=m.group(1).lower() == "x", text=m.group(2).strip()))
    return items


def parse_pipe_table(md: str) -> tuple[list[str], list[list[str]]]:
    lines = [ln.strip() for ln in md.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return [], []

    def cells(line: str) -> list[str]:
        parts = [c.strip() for c in line.strip("|").split("|")]
        return parts

    headers = cells(lines[0])
    rows: list[list[str]] = []
    for line in lines[1:]:
        if re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", line):
            continue
        row = cells(line)
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))
        rows.append(row[: len(headers)])
    return headers, rows


def _parse_month_day(token: str, default_year: int) -> date | None:
    token = token.strip().replace(",", "")
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2})(?:\s+(\d{4}))?$", token)
    if not m:
        return None
    month = MONTHS.get(m.group(1).lower())
    if not month:
        return None
    day = int(m.group(2))
    year = int(m.group(3)) if m.group(3) else default_year
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_date_range(text: str, default_year: int = 2026) -> tuple[date | None, date | None]:
    """Parse ranges like 'Aug 24–28', 'Aug 31–Sep 4', 'Oct 12–16'."""
    text = (text or "").strip()
    if not text:
        return None, None
    text = text.replace("–", "-").replace("—", "-")
    m = re.match(
        r"^([A-Za-z]+)\s+(\d{1,2})\s*-\s*(?:([A-Za-z]+)\s+)?(\d{1,2})(?:\s*,?\s*(\d{4}))?$",
        text,
    )
    if not m:
        single = _parse_month_day(text, default_year)
        return single, single
    month1 = MONTHS.get(m.group(1).lower())
    day1 = int(m.group(2))
    month2 = MONTHS.get(m.group(3).lower()) if m.group(3) else month1
    day2 = int(m.group(4))
    year = int(m.group(5)) if m.group(5) else default_year
    if not month1 or not month2:
        return None, None
    try:
        start = date(year, month1, day1)
        end_year = year if month2 >= month1 else year + 1
        end = date(end_year, month2, day2)
        return start, end
    except ValueError:
        return None, None


def week_num_from_label(label: str) -> int | None:
    m = re.match(r"^(\d+)$", label.strip())
    return int(m.group(1)) if m else None


def parse_calendar(md: str, today: date) -> list[CalendarRow]:
    body = section_body(md, "Academic calendar — AI 5100 Fall 2026")
    # Table may sit right under intro lines; parse whole file tables if section empty
    source = body if "|" in body else md
    headers, rows = parse_pipe_table(source)
    if not headers:
        return []
    # Expect Week | Dates | Theme | Sync | Async
    out: list[CalendarRow] = []
    for row in rows:
        label = row[0] if row else ""
        dates = row[1] if len(row) > 1 else ""
        theme = row[2] if len(row) > 2 else ""
        sync = row[3] if len(row) > 3 else ""
        async_ = row[4] if len(row) > 4 else ""
        start, end = parse_date_range(dates)
        out.append(
            CalendarRow(
                week_label=label,
                week_num=week_num_from_label(label),
                dates=dates,
                theme=theme,
                sync=sync,
                async_=async_,
                start=start,
                end=end,
            )
        )

    # Mark current week: date range containing today; else next numbered week after last ended week
    for row in out:
        if row.start and row.end and row.start <= today <= row.end:
            row.is_current = True
            break
    else:
        past_nums = [
            row.week_num
            for row in out
            if row.week_num is not None and row.end is not None and row.end < today
        ]
        next_num = (max(past_nums) + 1) if past_nums else None
        if next_num is not None:
            for row in out:
                if row.week_num == next_num:
                    row.is_current = True
                    break
        if not any(r.is_current for r in out):
            weeks = discover_content_weeks()
            pick = max(weeks) if weeks else 1
            for row in out:
                if row.week_num == pick:
                    row.is_current = True
                    break
    return out


def discover_content_weeks() -> list[int]:
    if not CONTENT_DIR.exists():
        return []
    found: list[int] = []
    for path in CONTENT_DIR.glob(f"{COURSE_PREFIX} Week *"):
        m = re.search(r"Week\s+(\d+)$", path.name)
        if m:
            found.append(int(m.group(1)))
    return sorted(found)


def probe_capture(week: int) -> CaptureStatus:
    content = CONTENT_DIR / f"{COURSE_PREFIX} Week {week}"
    sessions_dir = content / "sessions"
    sessions_ok = False
    if sessions_dir.is_dir():
        sessions_ok = any(p.is_file() for p in sessions_dir.iterdir())
    raw = RAW_DIR / "courses" / "AI-5100" / f"week-{week:02d}"
    lecture = WIKI_DIR / "courses" / "AI-5100" / "lectures" / f"Week-{week:02d}.md"
    return CaptureStatus(
        week=week,
        content=content.is_dir() and any(content.iterdir()),
        sessions=sessions_ok,
        raw=raw.is_dir() and any(raw.rglob("*")),
        lecture=lecture.is_file(),
    )


def weeks_to_show(calendar: list[CalendarRow], today: date) -> list[int]:
    """Show current week ±1."""
    current = next((r.week_num for r in calendar if r.is_current and r.week_num), None)
    content_weeks = discover_content_weeks()
    if current is None:
        current = max(content_weeks) if content_weeks else 1
    return sorted({max(1, current - 1), current, current + 1})


def scrub_md_links(text: str) -> str:
    """Turn [label](url) into label for plain display; normalize common unicode."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return (
        text.replace("\u2192", "->")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def status_class(status: str) -> str:
    s = status.lower().strip()
    if s == "in_progress":
        return "st-progress"
    if s == "submitted":
        return "st-submitted"
    if s == "graded":
        return "st-graded"
    if s == "todo":
        return "st-todo"
    return "st-other"


def render_html(
    focus: list[FocusItem],
    hw_headers: list[str],
    hw_rows: list[list[str]],
    calendar: list[CalendarRow],
    captures: list[CaptureStatus],
    today: date,
) -> str:
    focus_open = sum(1 for i in focus if not i.done)
    focus_lis = []
    for item in focus:
        cls = "done" if item.done else "open"
        mark = "[x]" if item.done else "[ ]"
        focus_lis.append(
            f'<li class="{cls}"><span class="mark">{mark}</span> {esc(scrub_md_links(item.text))}</li>'
        )
    focus_html = "\n".join(focus_lis) if focus_lis else "<li class='muted'>No focus items in HOME.md</li>"

    if hw_headers and hw_rows:
        thead = "".join(f"<th>{esc(h)}</th>" for h in hw_headers)
        body_rows = []
        for row in hw_rows:
            cells = []
            for i, cell in enumerate(row):
                if hw_headers[i].lower() == "status":
                    cells.append(
                        f'<td><span class="badge {status_class(cell)}">{esc(cell)}</span></td>'
                    )
                else:
                    cells.append(f"<td>{esc(scrub_md_links(cell))}</td>")
            body_rows.append("<tr>" + "".join(cells) + "</tr>")
        hw_html = f"<table><thead><tr>{thead}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"
    else:
        hw_html = "<p class='muted'>No homework rows found.</p>"

    cap_rows = []
    for c in captures:
        def cell(ok: bool) -> str:
            return f'<td class="{"ok" if ok else "miss"}">{"yes" if ok else "no"}</td>'

        cap_rows.append(
            "<tr>"
            f"<td>Week {c.week}</td>"
            f"{cell(c.content)}"
            f"{cell(c.sessions)}"
            f"{cell(c.raw)}"
            f"{cell(c.lecture)}"
            "</tr>"
        )
    capture_html = (
        "<table><thead><tr>"
        "<th>Week</th><th>Content</th><th>Sessions</th><th>Raw</th><th>Lecture wiki</th>"
        "</tr></thead><tbody>"
        + "".join(cap_rows)
        + "</tbody></table>"
    )

    cal_rows = []
    for row in calendar:
        cls = ' class="current"' if row.is_current else ""
        cal_rows.append(
            f"<tr{cls}>"
            f"<td>{esc(row.week_label)}</td>"
            f"<td>{esc(row.dates)}</td>"
            f"<td>{esc(row.theme)}</td>"
            f"<td>{esc(row.sync)}</td>"
            f"<td>{esc(row.async_)}</td>"
            "</tr>"
        )
    calendar_html = (
        "<table><thead><tr>"
        "<th>Week</th><th>Dates</th><th>Theme</th><th>Sync</th><th>Async</th>"
        "</tr></thead><tbody>"
        + "".join(cal_rows)
        + "</tbody></table>"
    )

    wiki_index = WIKI_DIR / "index.md"
    links = [
        ("HOME.md", str(COMMAND_CENTER / "HOME.md")),
        ("personas.md", str(COMMAND_CENTER / "personas.md")),
        ("homework-queue.md", str(COMMAND_CENTER / "homework-queue.md")),
        ("Wiki index", str(wiki_index)),
        ("Vault root", str(VAULT_ROOT)),
        ("GitHub ms_ai_cc", GITHUB_URL),
    ]
    links_html = "".join(
        f'<li><a href="{esc(href) if href.startswith("http") else "file:///" + esc(href.replace(chr(92), "/"))}">{esc(label)}</a>'
        f'<span class="path">{esc(href)}</span></li>'
        for label, href in links
    )

    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>MS AI Command Center</title>
<style>
  :root {{
    --bg0: #0f1419;
    --bg1: #161d26;
    --ink: #e7ecf1;
    --muted: #8b98a8;
    --line: #2a3544;
    --accent: #3d9a8b;
    --accent-dim: #2a6b61;
    --warn: #c4a35a;
    --bad: #c27070;
    --ok: #5aaf7a;
    --font-display: "Segoe UI Semibold", "Segoe UI", system-ui, sans-serif;
    --font-body: "Segoe UI", system-ui, sans-serif;
    --font-mono: "Cascadia Code", "Consolas", monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    min-height: 100vh;
    color: var(--ink);
    font-family: var(--font-body);
    background:
      radial-gradient(1200px 600px at 10% -10%, #1a3a36 0%, transparent 55%),
      radial-gradient(900px 500px at 100% 0%, #1e2a3a 0%, transparent 50%),
      linear-gradient(165deg, var(--bg0), var(--bg1) 60%, #121820);
  }}
  .wrap {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
  }}
  header.hero {{
    margin-bottom: 2.25rem;
    border-bottom: 1px solid var(--line);
    padding-bottom: 1.5rem;
  }}
  .brand {{
    font-family: var(--font-display);
    font-size: clamp(1.75rem, 4vw, 2.35rem);
    letter-spacing: -0.02em;
    margin: 0 0 0.35rem;
  }}
  .brand span {{ color: var(--accent); }}
  .lede {{
    margin: 0;
    color: var(--muted);
    font-size: 1.05rem;
    max-width: 36rem;
  }}
  .meta {{
    margin-top: 0.85rem;
    font-size: 0.85rem;
    color: var(--muted);
    font-family: var(--font-mono);
  }}
  .primary {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    margin-bottom: 2.5rem;
  }}
  @media (min-width: 860px) {{
    .primary {{ grid-template-columns: 1.1fr 1fr; align-items: start; }}
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent);
    margin: 0 0 0.85rem;
    font-weight: 600;
  }}
  .count {{
    color: var(--muted);
    font-weight: 400;
    letter-spacing: 0;
    text-transform: none;
    font-size: 0.85rem;
  }}
  ul.focus {{
    list-style: none;
    margin: 0;
    padding: 0;
  }}
  ul.focus li {{
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--line);
    line-height: 1.45;
    display: flex;
    gap: 0.65rem;
  }}
  ul.focus li.done {{ color: var(--muted); text-decoration: line-through; }}
  ul.focus .mark {{
    color: var(--accent);
    font-family: var(--font-mono);
    flex-shrink: 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }}
  th, td {{
    text-align: left;
    padding: 0.5rem 0.55rem;
    border-bottom: 1px solid var(--line);
    vertical-align: top;
  }}
  th {{
    color: var(--muted);
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}
  tr.current td {{
    background: rgba(61, 154, 139, 0.12);
  }}
  tr.current td:first-child {{
    box-shadow: inset 3px 0 0 var(--accent);
  }}
  .badge {{
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    padding: 0.15rem 0.45rem;
    border: 1px solid var(--line);
  }}
  .st-progress {{ color: var(--warn); border-color: var(--warn); }}
  .st-todo {{ color: var(--muted); }}
  .st-submitted {{ color: var(--accent); border-color: var(--accent-dim); }}
  .st-graded {{ color: var(--ok); border-color: var(--ok); }}
  td.ok {{ color: var(--ok); }}
  td.miss {{ color: var(--bad); }}
  .secondary {{
    display: grid;
    gap: 2rem;
    margin-top: 0.5rem;
  }}
  @media (min-width: 860px) {{
    .secondary {{ grid-template-columns: 1.2fr 0.8fr; }}
  }}
  .links {{ list-style: none; margin: 0; padding: 0; }}
  .links li {{
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--line);
  }}
  .links a {{
    color: var(--ink);
    text-decoration: none;
    border-bottom: 1px solid var(--accent-dim);
  }}
  .links a:hover {{ color: var(--accent); }}
  .path {{
    display: block;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.2rem;
    word-break: break-all;
  }}
  .muted {{ color: var(--muted); }}
  footer {{
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
    font-size: 0.8rem;
    color: var(--muted);
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <h1 class="brand">MS AI <span>Command Center</span></h1>
      <p class="lede">Local ops view for AI 5100 — focus, homework, capture readiness. Markdown remains the source of truth.</p>
      <p class="meta">today {esc(today.isoformat())} · generated {esc(generated)} · {esc(str(REPO_ROOT))}</p>
    </header>

    <section class="primary">
      <div>
        <h2>This week focus <span class="count">{focus_open} open</span></h2>
        <ul class="focus">
          {focus_html}
        </ul>
      </div>
      <div>
        <h2>Homework queue</h2>
        {hw_html}
      </div>
    </section>

    <section class="secondary">
      <div>
        <h2>Capture checklist</h2>
        {capture_html}
        <p class="muted" style="margin-top:0.75rem;font-size:0.85rem">Sessions = any file under Content/…/sessions/. Raw = converted week folder. Lecture = wiki lectures/Week-NN.md.</p>
      </div>
      <div>
        <h2>Quick links</h2>
        <ul class="links">
          {links_html}
        </ul>
      </div>
    </section>

    <section style="margin-top:2.5rem">
      <h2>Calendar</h2>
      {calendar_html}
    </section>

    <footer>
      Refresh the page to re-read markdown and vault paths. Edit files under command-center/; do not treat this UI as authoritative storage.
    </footer>
  </div>
</body>
</html>
"""


def build_page(today: date | None = None) -> str:
    today = today or date.today()
    home_md = read_text(COMMAND_CENTER / "HOME.md")
    hw_md = read_text(COMMAND_CENTER / "homework-queue.md")
    cal_md = read_text(COMMAND_CENTER / "academic-calendar.md")

    focus = parse_checklist(section_body(home_md, "This week focus"))
    hw_headers, hw_rows = parse_pipe_table(hw_md)
    calendar = parse_calendar(cal_md, today)
    captures = [probe_capture(w) for w in weeks_to_show(calendar, today)]
    return render_html(focus, hw_headers, hw_rows, calendar, captures, today)


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in ("/", "/index.html", "/dashboard"):
            self.send_error(404, "Not found")
            return
        try:
            body = build_page().encode("utf-8")
        except Exception as exc:  # noqa: BLE001 — surface build errors to client
            msg = f"dashboard build failed: {exc}\n".encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))
        sys.stderr.flush()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve local MS AI Command Center dashboard")
    parser.add_argument("--port", type=int, default=8765, help="Port (default 8765)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default 127.0.0.1)")
    parser.add_argument("--open", action="store_true", help="Open default browser")
    parser.add_argument(
        "--print-once",
        action="store_true",
        help="Write HTML to stdout and exit (no server)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.print_once:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.write(build_page())
        return 0

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Command Center dashboard: {url}", flush=True)
    print(f"Repo:  {REPO_ROOT}", flush=True)
    print(f"Vault: {VAULT_ROOT}", flush=True)
    print("Ctrl+C to stop", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
