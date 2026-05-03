import random

class StatsTracker:
    def __init__(self):
        self.total_balls = 0
        self.shot_distribution = {}
        self.total_runs = 0
        self.aggressive_shots = 0
        self.runs_per_over = {}   # over -> runs scored in that over
        self.current_over = 0
        self.pressure_history = []  # track pressure level per ball
        self.wickets = 0

    def update_stats(self, insights: dict, context: dict = None, event: dict = None):
        if "error" in insights:
            return

        self.total_balls += 1

        # Track shots
        shot_type = insights.get("shot_type", "Unknown")
        self.shot_distribution[shot_type] = self.shot_distribution.get(shot_type, 0) + 1

        # Track aggression
        intent = insights.get("intent", "").lower()
        if "aggressive" in intent:
            self.aggressive_shots += 1

        # Track runs
        runs = event.get("runs", 0) if event else random.randint(0, 4)
        self.total_runs += runs

        # Track runs per over
        over = event.get("over", self.current_over) if event else self.current_over
        self.current_over = over
        if over not in self.runs_per_over:
            self.runs_per_over[over] = 0
        self.runs_per_over[over] += runs

        # Track pressure level
        pressure = insights.get("pressure_level", "medium").lower()
        self.pressure_history.append(pressure)

        # Simulate wickets if context available
        if context:
            self.wickets = context.get("wickets", self.wickets)

    def get_stats(self) -> dict:
        aggression_index = 0
        if self.total_balls > 0:
            aggression_index = round((self.aggressive_shots / self.total_balls) * 100, 1)

        # Build run rate over-by-over
        sorted_overs = sorted(self.runs_per_over.keys())
        run_rate_labels = [f"Ov {o}" for o in sorted_overs]
        run_rate_data = [self.runs_per_over[o] for o in sorted_overs]

        # Cumulative score for worm
        cumulative = []
        total = 0
        for r in run_rate_data:
            total += r
            cumulative.append(total)

        # Pressure distribution
        pressure_counts = {"low": 0, "medium": 0, "high": 0}
        for p in self.pressure_history:
            if p in pressure_counts:
                pressure_counts[p] += 1

        # Strike rate
        strike_rate = round((self.total_runs / self.total_balls) * 100, 1) if self.total_balls > 0 else 0.0

        return {
            "total_balls_processed": self.total_balls,
            "total_runs": self.total_runs,
            "wickets": self.wickets,
            "shot_distribution": self.shot_distribution,
            "aggression_index": f"{aggression_index}%",
            "strike_rate": strike_rate,
            "run_rate_chart": {
                "labels": run_rate_labels,
                "data": run_rate_data,
                "cumulative": cumulative
            },
            "pressure_distribution": pressure_counts
        }

# Singleton instance
stats_tracker = StatsTracker()
