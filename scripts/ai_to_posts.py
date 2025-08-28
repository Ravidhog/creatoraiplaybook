#!/usr/bin/env python3
"""
ai_to_posts.py — generates daily blog post with OpenAI
"""

import os, json, re
from pathlib import Path
from datetime import datetime, timezone
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "posts"
MANIFEST = POSTS_DIR / "manifest.json"

# Ensure dirs
POSTS_DIR.mkdir(parents=True, exist_ok=True)

def slugify(text):
    return re.sub(r'[^a-z0-9-]', '-', text.lower()).strip('-')

def load_manifest():
    if not MANIFEST.exists():
        return {"posts": []}
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except:
        return {"posts": []}

def save_manifest(data):
    data["posts"].sort(key=lambda x: x.get("date_iso", ""), reverse=True)
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def generate_post():
    prompt = """Write a ~600 word blog post for 'Creator AI Playbook'.
Audience: content creators (YouTube, TikTok, Instagram, bloggers).
Style: clear, engaging, practical tips.
Topic: One actionable AI strategy or tool that creators can apply today.
Structure: catchy headline, intro, 3–4 sections with subheadings, conclusion.
End with a 'Try this today:' bullet list."""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":"You are a professional AI blog writer."},
                  {"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content.strip()

def main():
    manifest = load_manifest()
    date = datetime.now(timezone.utc)
    date_str = date.strftime("%Y-%m-%d")

    # Generate post
    post_text = generate_post()
    title = post_text.splitlines()[0].strip("# ").strip()
    slug = slugify(title) or "ai-post"
    filename = f"{date_str}-{slug}.html"
    filepath = POSTS_DIR / filename

    # Wrap in HTML
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <article class="post">
    <h1>{title}</h1>
    <p><small>{date.strftime("%B %d, %Y")}</small></p>
    <div class="content">
      {post_text.replace("\n", "<br><br>")}
    </div>
  </article>
</body>
</html>"""

    filepath.write_text(html, encoding="utf-8")

    # Update manifest
    manifest["posts"].append({
        "id": filename,
        "title": title,
        "slug": filename,
        "path": f"posts/{filename}",
        "date_iso": date.isoformat(),
        "summary": post_text[:200] + "..."
    })
    save_manifest(manifest)

    print(f"Generated new post: {filename}")

if __name__ == "__main__":
    main()
