import feedparser
import yaml
import os
from datetime import datetime, timedelta

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_links(feed_url, lookback_hours):
    print(f"DEBUG: scarico {feed_url}")
    feed = feedparser.parse(feed_url)
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
    links = []
    for entry in feed.entries[:10]:  # massimo 10 articoli per feed
        published = None
        if hasattr(entry, "published_parsed"):
            published = datetime(*entry.published_parsed[:6])
        if published and published < cutoff:
            continue
        links.append(f"- {entry.title}\n{entry.link}")
    return links

def main():
    config = load_config()
    all_text = []
    for cat in config["categories"]:
        all_text.append(f"## {cat['name']}")
        for feed in cat["feeds"]:
            try:
                links = fetch_links(feed, config.get("lookback_hours", 24))
                if links:
                    all_text.extend(links[:config.get("max_per_category", 5)])
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
