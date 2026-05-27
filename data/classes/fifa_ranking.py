import json, asyncio, os
import pandas as pd
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Page, Response, TimeoutError as PlaywrightTimeout


class FIFARanking:
    RANKING_PAGE = os.getenv("RANKING_PAGE")
    RANKINGS_API = os.getenv("RANKINGS_API")
    async def goto(self, page: Page, url: str):
        """Navigate and dismiss the OneTrust cookie banner."""
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await self.dismiss_banner(page)
        await page.wait_for_timeout(2000)

    async def dismiss_banner(self, page: Page):
        """Dismiss OneTrust consent banner if present."""
        selectors = [
            "#onetrust-accept-btn-handler",
            "#accept-recommended-btn-handler",
            "button:has-text('Accept All')",
            "button:has-text('Accept Cookies')",
            "button:has-text('Agree')",
        ]
        for sel in selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=2000):
                    await btn.click()
                    print("  ✅ Cookie banner dismissed")
                    await page.wait_for_timeout(1500)
                    return
            except Exception:
                continue
        print("No cookie banner detected")


    async def get_schedule_ids(self, page: Page) -> list[dict]:
        """
        Pulls all available ranking snapshot dates from __NEXT_DATA__.
        Path confirmed by diagnostic:
          props → pageProps → pageData → ranking → allAvailableDates

        Each entry looks like:
          {"id": "FRS_Male_Football_20260119", "text": "19 Jan 2026"}
        """
        await self.goto(page, self.RANKING_PAGE)

        next_data_raw = await page.evaluate("""
            () => {
                const el = document.getElementById('__NEXT_DATA__');
                return el ? el.textContent : null;
            }
        """)

        if not next_data_raw:
            raise ValueError("__NEXT_DATA__ not found on page.")

        data = json.loads(next_data_raw)

        # Path confirmed by diagnostic output
        ranking_data = (
            data["props"]["pageProps"]["pageData"]["ranking"]
        )

        # Try allAvailableDates first, fall back to dates
        dates = ranking_data.get("allAvailableDates") \
             or ranking_data.get("dates")

        if not dates:
            raise ValueError(
                f"No dates found. Available keys under 'ranking': "
                f"{list(ranking_data.keys())}"
            )

        print(f"  Found {len(dates)} ranking snapshots")
        return dates

    async def fetch_rankings_for_schedule(
        self, schedule_id: str, page: Page
    ) -> list[dict]:
        all_results = []
        continuation_token = None
        page_num = 1

        while True:
            captured = {}

            async def handle_response(response: Response):
                if "rankingsbyschedule" in response.url \
                        and response.status == 200:
                    try:
                        body = await response.json()
                        if "Results" in body:
                            captured["data"] = body
                    except Exception:
                        pass

            page.on("response", handle_response)

            # Build URL — append continuation token for pages 2+
            url = self.RANKING_PAGE
            if continuation_token:
                url += f"?scheduleId={schedule_id}&token={continuation_token}"
            else:
                url += f"?dateId={schedule_id}"

            # Navigate to trigger the API call with the right schedule ID
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=45000
            )
            await page.wait_for_timeout(3000)
            page.remove_listener("response", handle_response)

            if not captured.get("data"):
                break

            body = captured["data"]
            results = body.get("Results", [])
            all_results.extend(results)

            # Check for more pages
            continuation_token = body.get("ContinuationToken")
            if not continuation_token:
                break

            page_num += 1

        return all_results

    def parse_results(
        self, results: list[dict], date_str: str
    ) -> list[dict]:
        """
        Parse entries from the confirmed API response shape:
          {"Results": [...], "ContinuationToken": ..., "ContinuationHash": ...}

        We don't yet know the exact field names inside Results —
        they'll be printed on first run and we can adjust.
        """
        try:
            clean = date_str.replace("Sept", "Sep")
            try:
                dt = datetime.strptime(clean, "%d %b %Y")
            except ValueError:
                dt = datetime.strptime(clean, "%d %B %Y")
        except Exception:
            dt = datetime.now()

        records = []
        for i, entry in enumerate(results):
            # Print structure on first entry so we can verify field names
            if i == 0:
                print(f"    API Result keys: {list(entry.keys())}")

            # Field names based on FIFA v3 API conventions
            # Adjust these if the first-run print shows different names
            records.append({
                "rank_date": dt.strftime("%Y-%m-%d"),
                "rank": entry.get("Rank")
                        or entry.get("rank")
                        or entry.get("RankPosition"),
                "country_full": self.extract_country_name(entry),
                "country_code": entry.get("CountryCode")
                                or entry.get("IsoCode")
                                or entry.get("Code"),
                "total_points": entry.get("Points")
                                or entry.get("TotalPoints")
                                or entry.get("RankingPoints"),
                "previous_points": entry.get("PreviousPoints")
                                   or entry.get("PointsBefore"),
                "previous_rank": entry.get("PreviousRank")
                                 or entry.get("RankBefore"),
                "confederation": entry.get("Confederation")
                                 or entry.get("ConfederationCode")
                                 or "",
            })

        return records

    #Fallback: scrape rendered DOM table

    async def scrape_from_dom(
        self, page: Page, date_str: str
    ) -> list[dict]:
        """
        Direct DOM scrape of the rendered ranking table.
        Used when API interception fails.
        Diagnostic confirmed table renders with 11 rows including header.
        """
        print("    Falling back to DOM scrape...")

        # Wait for rows beyond the header
        try:
            await page.wait_for_selector(
                "table tbody tr", timeout=10000
            )
        except PlaywrightTimeout:
            pass

        rows = await page.evaluate("""
            () => {
                const rows = document.querySelectorAll('table tbody tr');
                return Array.from(rows).map(row => {
                    const cells = row.querySelectorAll('td');
                    return {
                        rank:          cells[0]?.innerText?.trim(),
                        country_full:  cells[1]?.innerText?.trim(),
                        total_points:  cells[4]?.innerText?.trim(),
                    };
                }).filter(r => r.rank && r.country_full);
            }
        """)

        try:
            clean = date_str.replace("Sept", "Sep")
            try:
                dt = datetime.strptime(clean, "%d %b %Y")
            except ValueError:
                dt = datetime.strptime(clean, "%d %B %Y")
        except Exception:
            dt = datetime.now()

        records = []
        for r in rows:
            try:
                records.append({
                    "rank_date":       dt.strftime("%Y-%m-%d"),
                    "rank":            int(r["rank"]) if str(r["rank"]).isdigit() else None,
                    "country_full":    r["country_full"],
                    "country_code":    None,
                    "total_points":    float(r["total_points"].replace(",", ""))
                                       if r["total_points"] else None,
                    "previous_points": None,
                    "previous_rank":   None,
                    "confederation":   "",
                })
            except (ValueError, KeyError):
                continue

        return records

    def filter_dates(self, schedule_ids: list[dict], start_year: int, end_year: int) -> list[dict]:
        """
        Filter snapshots to only include dates within [start_year, end_year).
        Parses date from both the text field and the schedule ID suffix.
        """
        filtered = []
        seen_ids = set()  # Prevent duplicate schedule IDs

        for entry in schedule_ids:
            sid  = entry.get("id") or entry.get("Id") or ""
            text = entry.get("text") or entry.get("Text") or ""

            # Skip if we've already added this schedule ID
            if sid in seen_ids:
                continue

            dt = None

            # Try parsing from text field first
            if text:
                clean = text.replace("Sept", "Sep")
                for fmt in ("%d %b %Y", "%d %B %Y"):
                    try:
                        dt = datetime.strptime(clean, fmt)
                        break
                    except ValueError:
                        continue

            # Fall back to parsing from ID suffix e.g. FRS_Male_Football_20260119
            if dt is None and sid:
                try:
                    date_part = sid.split("_")[-1]  # "20260119"
                    dt = datetime.strptime(date_part, "%Y%m%d")
                except Exception:
                    continue

            if dt is None:
                continue

            if start_year <= dt.year < end_year:
                filtered.append(entry)
                seen_ids.add(sid)

        return filtered

    # ── Main entry point ──────────────────────────────────────────────────

    async def scrape(self,
        start_year: int = 2021,
        end_year: int = 2026,
        delay_seconds: float = 2.5,
        save_path: Path | None = None,
        headless: bool = True,
    ) -> pd.DataFrame:

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=headless)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
                locale="en-US",
            )
            page = await context.new_page()

            # ── Step 1: Get all schedule IDs ──
            print("Step 1: Fetching available ranking snapshots...")
            schedule_ids = await self.get_schedule_ids(page)
            filtered = self.filter_dates(
                schedule_ids,
                start_year=start_year,
                end_year=end_year,   # new param
            )
            print(f"  Scraping {len(filtered)} snapshots from {start_year}+\n")

            # ── Step 2: Fetch each snapshot ──
            all_records = []
            for i, entry in enumerate(filtered):
                sid      = entry.get("id") or entry.get("Id") or ""
                text     = entry.get("text") or entry.get("Text") or sid

                print(f"  [{i+1}/{len(filtered)}] {text}...")
                try:
                    # Primary: intercept the API call
                    results = await self.fetch_rankings_for_schedule(sid, page)

                    if results:
                        records = self.parse_results(results, text)
                    else:
                        # Fallback: DOM scrape
                        records = await self.scrape_from_dom(page, text)

                    all_records.extend(records)
                    print(f"    ✅ {len(records)} teams captured")

                except Exception as e:
                    print(f"    ❌ Failed: {e}")

                await asyncio.sleep(delay_seconds)

            await browser.close()

        if not all_records:
            raise RuntimeError(
                "No records scraped. Run with headless=False to debug."
            )
        print(all_records[0])
        print(type(all_records[0]["rank_date"]))
        print(type(all_records[0]["country_full"]))

        for r in all_records:
            if isinstance(r.get("country_full"), list):
                print("FOUND LIST:", r)
                break

        df = (
            pd.DataFrame(all_records)
            .assign(rank_date=lambda d: pd.to_datetime(d["rank_date"]))
            # Drop duplicate team+date combinations keeping first occurrence
            .drop_duplicates(subset=["rank_date", "country_full"], keep="first")
            .sort_values(["rank_date", "rank"])
            .reset_index(drop=True)
        )

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(save_path, index=False)
            print(f"\n✅ Saved {len(df):,} rows → {save_path}")

        return df

    async def scrape_latest(self, headless: bool = True) -> pd.DataFrame:
        """Fetch only the most recent snapshot."""
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=headless)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            schedule_ids = await self.get_schedule_ids(page)
            latest = schedule_ids[0]
            sid = latest.get("id") or latest.get("Id") or ""
            text = latest.get("text") or latest.get("Text") or sid
            print(f"Fetching latest snapshot: {text}")
            results      = await self.fetch_rankings_for_schedule(sid, page)
            if not results:
                results_parsed = await self.scrape_from_dom(page, text)
            else:
                results_parsed = self.parse_results(results, text)
            await browser.close()

        return pd.DataFrame(results_parsed)
    
    def extract_country_name(self, entry):
        raw = (
            entry.get("Name")
            or entry.get("TeamName")
            or entry.get("CountryName")
        )

        if isinstance(raw, list) and raw:
            return raw[0].get("Description")
        
        if isinstance(raw, dict):
            return raw.get("Description")

        return raw