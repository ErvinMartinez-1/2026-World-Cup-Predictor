import asyncio
from data.classes.fifa_ranking import FIFARanking

scraper = FIFARanking()

# Full history from 2021 — runs once, saves CSV
df = asyncio.run(
    scraper.scrape(
        start_year=2021,
        save_path="data/raw/fifa_rankings_scraped.csv",
        headless=True,      # set False to watch the browser
    )
)

# Or just the latest snapshot
latest = asyncio.run(scraper.scrape_latest())
print(latest.head(10))