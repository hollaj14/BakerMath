import numpy as np

def validate_percentage(value):
    """Validate if a percentage is between 0 and 200"""
    try:
        value = float(value)
        return 0 <= value <= 200
    except (ValueError, TypeError):
        return False

def calculate_ingredient_weight(flour_weight, percentage):
    """Calculate ingredient weight based on flour weight and percentage"""
    try:
        return round(float(flour_weight) * float(percentage) / 100)
    except (ValueError, TypeError):
        return None

def format_weight(weight):
    """Format weight to whole numbers"""
    if weight is None:
        return "Invalid input"
    return f"{round(weight):,} g"

def calculate_flour_weight_from_portions(portion_count, portion_weight, total_percentage):
    """Calculate flour weight based on desired portion count and weight"""
    try:
        total_dough_weight = float(portion_count) * float(portion_weight)
        # Since total_percentage includes 100% flour plus all other ingredients
        flour_weight = (total_dough_weight * 100) / total_percentage
        return round(flour_weight)
    except (ValueError, TypeError, ZeroDivisionError):
        return None
