from scipy.stats import poisson

def get_most_likely_score(exp_home: float, exp_away: float, prob_home: float, prob_draw: float, prob_away: float) -> tuple[int, int]:
        # For deterministic mode: find the most likely scoreline consistent with the predicted outcome, rather than just rounding.
        from scipy.stats import poisson

        # Get most likely outcome from classifier
        predicted_outcome = max(
            {'home_win': prob_home, 'draw': prob_draw, 'away_win': prob_away},
            key=lambda k: {'home_win': prob_home, 'draw': prob_draw, 'away_win': prob_away}[k]
        )

        # Find most probable scoreline matching that outcome
        best_score  = (1, 1)
        best_prob = 0.0

        for h in range(6):
            for a in range(6):
                # Probability of this exact scoreline
                score_prob = (poisson.pmf(h, exp_home) * poisson.pmf(a, exp_away))

                if predicted_outcome == 'home_win' and h <= a:
                    continue
                elif predicted_outcome == 'away_win' and a <= h:
                    continue
                elif predicted_outcome == 'draw' and h != a:
                    continue

                if score_prob > best_prob:
                    best_prob = score_prob
                    best_score = (h, a)

        return best_score