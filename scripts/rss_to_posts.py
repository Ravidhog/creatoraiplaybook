import json, datetime, pathlib, sys
try:
    import feedparser   # installed by the workflow
except Exception:
    feedparser = None

SITE_TITLE = "AI Biz Playbook"  # change to "Creator AI Playbook" in that repo
OUT_DIR = pathlib.Path("posts")
OUT_DIR.mkdir(exist_ok=True)
MANIFEST = OUT_DIR / "manifest.json"

FEEDS = [
    "https://openai.com/blog/rss/",
    "https://github.blog/changelog/feed/"
]

def read_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posts": []}

def write_manifest(data):
    MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")

def fetch_items():
    if not feedparser:
        return []
    items = []
    for url in FEEDS:
        try:
            d = feedparser.parse(url)
            src = getattr(d, "feed", {}).get("title", url)
            for e in (getattr(d, "entries", []) or [])[:10]:
                items.append({
                    "title": e.get("title","(no title)"),
                    "link": e.get("link","#"),
                    "summary": e.get("summary",""),
                    "published": e.get("published",""),
                    "source": src
                })
        except Exception:
            continue
    items.sort(key=lambda x: x.get("published") or "", reverse=True)
    return items[:25]

def make_post_html(title, items):
    body = [f"<h2>{title}</h2>"]
    for it in items:
        body.append(
            f'<div class="post"><h3><a href="{it.get("link","#")}" target="_blank" rel="noopener">{it.get("title","(no title)")}</a></h3>'
            f'<p>{it.get("summary","")}</p>'
            f'<p class="meta">{it.get("source","")}</p></div>'
        )
    content = "\n".join(body)
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — {SITE_TITLE}</title><link rel="stylesheet" href="../styles.css"></head>
<body>
<header><h1><a href="../index.html" style="text-decoration:none;color:inherit;">{SITE_TITLE}</a></h1></header>
<main>{content}</main>
<footer><p>&copy; {datetime.datetime.utcnow().year} {SITE_TITLE}</p></footer>
</body></html>"""

def main():
    items = fetch_items()
    today = datetime.date.today().isoformat()
    title = f"Daily Roundup — {today}"

    if not items:
        items = [{
            "title": "Welcome post",
            "link": "#",
            "summary": "The auto-publisher ran but found no feed items. Edit FEEDS in scripts/rss_to_posts.py and re-run the workflow.",
            "source": "Publisher"
        }]

    html = make_post_html(title, items)
    fname = f"{today}-roundup.html"
    (OUT_DIR / fname).write_text(html, encoding="utf-8")

    manifest = read_manifest()
    if not any(p.get("filename")==fname for p in manifest["posts"]):
        manifest["posts"].insert(0, {"filename": fname, "title": title, "date": today})
    write_manifest(manifest)
    print("Wrote", fname)
    return 0

if __name__ == "__main__":
    sys.exit(main())
