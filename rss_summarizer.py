import feedparser
import trafilatura
import yaml
import os
from datetime import datetime, timedelta

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def summarize_text(text, max_sentences=5):
    if not text:
        return "Nessun contenuto trovato."
    sentences = text.split(". ")
    return ". ".join(sentences[:max_sentences]) + "."

def fetch_and_summarize(feed_url, lookback_hours):
    print(f"DEBUG: scarico {feed_url}")
    feed = feedparser.parse(feed_url)
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
    summaries = []
    for entry in feed.entries[:5]:
        published = None
        if hasattr(entry, "published_parsed"):
            published = datetime(*entry.published_parsed[:6])
        if published and published < cutoff:
            continue
        url = entry.link
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(downloaded) if downloaded else entry.get("summary", "")
        summary = summarize_text(content)
        summaries.append(f"- {entry.title}\n{summary}\n(Link: {url})")
    return summaries

def main():
    config = load_config()
    all_text = []
    for cat in config["categories"]:
        all_text.append(f"## {cat['name']}")
        for feed in cat["feeds"]:
            try:
                summaries = fetch_and_summarize(feed, config.get("lookback_hours", 24))
                if summaries:
                    all_text.extend(summaries[:config.get("max_per_category", 3)])
                else:
                    all_text.append(f"(Nessun articolo recente da {feed})")
            except Exception as e:
                all_text.append(f"(Errore con {feed}: {e})")
    os.makedirs("output", exist_ok=True)
    fname = f"output/rassegna_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))
    print("DEBUG: file salvato", fname)

if __name__ == "__main__":
    main()
