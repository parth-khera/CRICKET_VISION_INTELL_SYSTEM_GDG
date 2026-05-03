import random

def extract_event(vision_data: dict) -> dict:
    """
    Converts vision outputs into a structured cricket event.
    In a fully trained model, this would map coordinates/trajectories to specific labels.
    """
    if vision_data.get("status") != "success":
        return {"error": "Vision processing failed"}
        
    # Simulate structured extraction based on vision outputs
    ball_types = ["short", "yorker", "good length", "full toss"]
    lines = ["off", "leg", "middle", "wide outside off"]
    shots = ["cut", "pull", "drive", "defend", "leave", "sweep"]
    
    trajectory = vision_data.get("estimated_trajectory", "")
    
    line = "off" if "off" in trajectory else random.choice(lines)
    ball_type = random.choice(ball_types)
    
    # Simple logic mapping
    if ball_type == "short":
        shot = random.choice(["pull", "cut", "defend", "leave"])
    elif ball_type == "yorker":
        shot = random.choice(["defend", "drive"])
    else:
        shot = random.choice(shots)
        
    runs = random.choice([0, 1, 2, 3, 4, 6])
    over_approx = random.randint(1, 20)
    
    return {
        "ball_type": ball_type,
        "line": line,
        "shot": shot,
        "runs": runs,
        "over": over_approx
    }
