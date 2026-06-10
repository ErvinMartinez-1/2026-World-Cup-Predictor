class ThirdPlaceQualifier:
    """
    Determines which 8 of the 12 third-place teams advance
    to the Round of 32, per FIFA rules.

    Comparison order: Points → GD → GF → Random
    """

    def get_qualifiers(self, standings: dict) -> list[str]:
        third_place = []

        for group, group_standings in standings.items():
            if len(group_standings) >= 3:
                third = group_standings[2]
                third_place.append({
                    'team':        third.team,
                    'group':       group,
                    'points':      third.points,
                    'goal_diff':   third.goal_diff,
                    'goals_for':   third.goals_for,
                })

        # Sort all third-place teams
        third_place.sort(
            key=lambda x: (x['points'], x['goal_diff'], x['goals_for']),
            reverse=True
        )

        # Top 8 advance
        qualifiers = [t['team'] for t in third_place[:8]]
        return qualifiers