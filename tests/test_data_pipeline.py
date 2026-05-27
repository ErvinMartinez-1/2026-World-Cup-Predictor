from src.pipeline import DataPipeline

# ── Standard load (uses cache where available) ──
pipeline = DataPipeline().run()

# ── Access layers directly ──
pipeline.matches          # DataFrame
pipeline.rankings         # DataFrame
pipeline.elo              # DataFrame

# ── Convenience methods ──
pipeline.rankings_at("2024-06-01")     # snapshot closest to that date
pipeline.team_matches("Argentina")     # all Argentina fixtures
pipeline.team_elo("Brazil")            # current ELO float
pipeline.team_ranking("France")        # most recent ranking dict

# ── Summary of what loaded ──
print(pipeline.summary())

# ── Force re-scrape one layer only ──
pipeline = DataPipeline(force_reload_rankings=True).run()

# ── Force rebuild everything ──
pipeline = DataPipeline(force_reload=True).run()