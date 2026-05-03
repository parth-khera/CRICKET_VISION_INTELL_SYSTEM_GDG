import cv2
import numpy as np
import os
import random

def process_image(image_path: str):
    """
    Simulates a vision agent extracting features from an image.
    Uses basic OpenCV to generate an edge map and detects a simulated ball.
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Save edge map for preview
        edge_filename = f"edge_{os.path.basename(image_path)}"
        edge_path = os.path.join("static/uploads", edge_filename)
        cv2.imwrite(edge_path, edges)
        
        # Simulate ball detection (In a real system, we'd use HoughCircles or a YOLO model)
        # We will intelligently simulate detection here based on some heuristics or random logic for the prototype
        
        # For prototype purposes, let's randomly pick if detection was clear
        detection_status = random.choice(["clear", "unclear", "clear", "clear"])
        
        ball_pos = None
        if detection_status == "clear":
            height, width = img.shape[:2]
            # Simulate a realistic position of a ball
            ball_pos = {
                "x": random.randint(int(width * 0.4), int(width * 0.6)),
                "y": random.randint(int(height * 0.5), int(height * 0.8))
            }

        return {
            "status": "success",
            "edge_map_url": f"/static/uploads/{edge_filename}",
            "detection": detection_status,
            "ball_position": ball_pos,
            "estimated_trajectory": "towards_off_stump" if random.random() > 0.5 else "towards_leg_stump"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
