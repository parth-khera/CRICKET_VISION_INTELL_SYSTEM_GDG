class StatsTracker:
    def __init__(self):
        self.total_balls = 0
        self.shot_distribution = {}
        self.total_runs = 0
        self.aggressive_shots = 0

    def update_stats(self, insights: dict):
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

    def get_stats(self) -> dict:
        aggression_index = 0
        if self.total_balls > 0:
            aggression_index = round((self.aggressive_shots / self.total_balls) * 100, 1)
            
        return {
            "total_balls_processed": self.total_balls,
            "shot_distribution": self.shot_distribution,
            "aggression_index": f"{aggression_index}%"
        }

# Singleton instance
stats_tracker = StatsTracker()
