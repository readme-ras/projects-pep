"""
predict.py  –  Load a trained model and predict house prices.

Usage:
    python predict.py                        # interactive prompt
    python predict.py --model GradientBoosting_Tuned
"""

import sys, os, argparse
import pandas as pd
import joblib

sys.path.insert(0, os.path.dirname(__file__))
from utils.helpers import add_features

MODELS_DIR = "models"
DEFAULT    = "GradientBoosting_Tuned"

FEATURE_COLS = [
    'area', 'bedrooms', 'bathrooms', 'age',
    'distance_to_city', 'garage', 'pool', 'school_rating',
    'area_per_bedroom', 'bath_bed_ratio', 'age_distance',
    'area_school', 'total_rooms', 'is_new', 'is_close', 'luxury_score'
]


def load_model(name: str):
    path = os.path.join(MODELS_DIR, f"{name}.joblib")
    if not os.path.exists(path):
        # fallback to base models
        path = os.path.join(MODELS_DIR, f"Gradient_Boosting.joblib")
    return joblib.load(path)


def predict_one(model, home: dict) -> float:
    df  = pd.DataFrame([home])
    df  = add_features(df)
    return float(model.predict(df[FEATURE_COLS])[0])


def interactive(model):
    print("\n" + "="*50)
    print("  🏠  House Price Predictor")
    print("="*50)
    try:
        home = {
            "area"             : float(input("  Area (sq ft)          : ")),
            "bedrooms"         : int(input(  "  Bedrooms              : ")),
            "bathrooms"        : float(input("  Bathrooms             : ")),
            "age"              : float(input("  Age of house (years)  : ")),
            "distance_to_city" : float(input("  Distance to city (km) : ")),
            "garage"           : int(input(  "  Garage spaces (0/1/2) : ")),
            "pool"             : int(input(  "  Pool? (0=No, 1=Yes)   : ")),
            "school_rating"    : float(input("  School rating (3-10)  : ")),
        }
        price = predict_one(model, home)
        print(f"\n  💰  Estimated Price: ${price:>12,.0f}")
        print("="*50 + "\n")
    except KeyboardInterrupt:
        print("\n  Goodbye!")


def batch_demo(model):
    """Show predictions for a batch of sample homes."""
    homes = [
        {"area":1200,"bedrooms":2,"bathrooms":1.0,"age":20,"distance_to_city":15,"garage":0,"pool":0,"school_rating":6.0},
        {"area":1800,"bedrooms":3,"bathrooms":2.0,"age":8, "distance_to_city":8, "garage":1,"pool":0,"school_rating":7.5},
        {"area":2500,"bedrooms":4,"bathrooms":2.5,"age":3, "distance_to_city":5, "garage":2,"pool":0,"school_rating":8.5},
        {"area":3500,"bedrooms":5,"bathrooms":3.5,"age":1, "distance_to_city":2, "garage":2,"pool":1,"school_rating":9.5},
        {"area":700, "bedrooms":1,"bathrooms":1.0,"age":50,"distance_to_city":30,"garage":0,"pool":0,"school_rating":4.0},
    ]
    labels = ["Starter Home", "Family Home", "Nice Home", "Luxury Home", "Budget Apt"]
    print(f"\n  {'Home':<20} {'Area':>6}  {'Bed/Bath':<9} {'Age':>5} {'Dist':>5} {'Predicted':>14}")
    print(f"  {'─'*20} {'─'*6}  {'─'*9} {'─'*5} {'─'*5} {'─'*14}")
    for label, h in zip(labels, homes):
        price = predict_one(model, h)
        bb    = f"{h['bedrooms']}b/{h['bathrooms']}ba"
        print(f"  {label:<20} {h['area']:>6,}  {bb:<9} {h['age']:>5.0f} {h['distance_to_city']:>5.1f} ${price:>13,.0f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default=DEFAULT, help='Model name (without .joblib)')
    parser.add_argument('--demo',  action='store_true', help='Run batch demo predictions')
    args = parser.parse_args()

    available = [f.replace('.joblib','') for f in os.listdir(MODELS_DIR) if f.endswith('.joblib')]
    print(f"\n  📦  Available models: {available}")
    print(f"  🔄  Loading model   : {args.model}")

    try:
        model = load_model(args.model)
    except Exception:
        print(f"  ⚠️  Could not load '{args.model}', trying first available…")
        model = load_model(available[0])

    if args.demo:
        batch_demo(model)
    else:
        batch_demo(model)
        interactive(model)
