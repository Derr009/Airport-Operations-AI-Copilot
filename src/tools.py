import pandas as pd
from typing import Dict, Any
from pathlib import Path
from src.config import BASE_DIR

DATA_PATH = BASE_DIR / "data" / "airport_metrics.csv"


def get_airport_metrics(airport_code: str) -> Dict[str, Any]:
    """
    Fetches real-time operational metrics for a specific airport.
    
    Args:
        airport_code: The 3-letter IATA airport code (e.g., 'SFO', 'LAX', 'JFK').
        
    Returns:
        Dictionary containing completion_rate, average_eta, active_drivers,
        driver_cancellation_rate, queue_size, surge_multiplier, request_volume, and timestamp.
    """
    code = airport_code.strip().upper()
    valid_codes = ["SFO", "LAX", "JFK"]
    
    if code not in valid_codes:
        return {"error": f"Invalid airport code '{airport_code}'. Supported airports: {valid_codes}"}
    
    if not DATA_PATH.exists():
        return {"error": f"Telemetry dataset not found at {DATA_PATH}"}
    
    df = pd.read_csv(DATA_PATH)
    row = df[df["airport_code"] == code]
    
    if row.empty:
        return {"error": f"No telemetry data available for {code}."}
    
    metrics = row.iloc[0].to_dict()
    return metrics


def calculate_driver_incentive(driver_count: int, severity_level: str) -> Dict[str, Any]:
    """
    Calculates driver incentive payout structure based on issue severity and affected drivers.
    
    Args:
        driver_count: Number of active drivers eligible for the incentive.
        severity_level: 'low' (completion rate 75-84%) or 'high' (completion rate <75%).
        
    Returns:
        Recommended per-trip bonus rate, estimated total cost, and policy status.
    """
    if driver_count <= 0:
        return {"error": "driver_count must be greater than 0."}
    
    severity = severity_level.strip().lower()
    if severity == "low":
        per_trip_bonus = 5.0
    elif severity == "high":
        per_trip_bonus = 10.0
    else:
        return {"error": "Invalid severity_level. Must be 'low' or 'high'."}
    
    total_estimated_cost = driver_count * per_trip_bonus
    max_budget_limit = 500.0
    
    requires_director_approval = total_estimated_cost > max_budget_limit
    
    return {
        "per_trip_bonus": per_trip_bonus,
        "eligible_drivers": driver_count,
        "total_cost": total_estimated_cost,
        "max_budget_limit": max_budget_limit,
        "requires_director_approval": requires_director_approval,
        "status": "APPROVED" if not requires_director_approval else "NEEDS_EXECUTIVE_APPROVAL"
    }


def trigger_surge_override(airport_code: str, new_multiplier: float, reason: str) -> Dict[str, Any]:
    """
    Prepares a surge multiplier override action for an airport.
    
    Args:
        airport_code: The 3-letter IATA airport code (e.g., 'SFO', 'LAX', 'JFK').
        new_multiplier: Target surge multiplier (e.g., 1.5).
        reason: Operational justification for increasing/decreasing surge.
        
    Returns:
        Dict outlining the requested surge update and validation status.
    """
    code = airport_code.strip().upper()
    valid_codes = ["SFO", "LAX", "JFK"]
    
    if code not in valid_codes:
        return {"error": f"Invalid airport code '{airport_code}'. Supported airports: {valid_codes}"}
    
    if new_multiplier < 1.0 or new_multiplier > 2.5:
        return {"error": f"Surge multiplier {new_multiplier} is out of realistic operational boundaries (1.0x - 2.5x)."}
    
    return {
        "airport_code": code,
        "requested_multiplier": new_multiplier,
        "reason": reason,
        "status": "PENDING_VALDATION"
    }


if __name__ == "__main__":
    print("\n--- Testing Tools Standalone ---")
    print("Metrics Tool SFO:", get_airport_metrics("SFO"))
    print("Incentive Tool High Severity:", calculate_driver_incentive(30, "high"))
    print("Surge Override Tool:", trigger_surge_override("SFO", 1.5, "Low completion rate"))