"""
tune.py  –  Hyperparameter tuning for the best regression models.

Uses GridSearchCV + RandomizedSearchCV to find optimal parameters.
"""

import os, sys, warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection  import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.preprocessing    import StandardScaler
from sklearn.pipeline         import Pipeline
from sklearn.ensemble         import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model     import Ridge, Lasso
from scipy.stats              import randint, uniform

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))
from utils.helpers import add_features, regression_report, print_report

print("\n" + "="*55)
print("  🔧  Hyperparameter Tuning")
print("="*55)

# ── Data ─────────────────────────────────────────────────────────────────────
df     = add_features(pd.read_csv('data/house_prices.csv'))
FEATS  = [c for c in df.columns if c != 'price']
X, y   = df[FEATS], df['price']
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

tuned_results = []


# ── 1. Ridge — GridSearchCV ───────────────────────────────────────────────────
print("\n  Tuning Ridge Regression …")
ridge_pipe = Pipeline([("scaler", StandardScaler()), ("model", Ridge())])
ridge_grid = {"model__alpha": [0.1, 1, 10, 50, 100, 500, 1000, 5000]}
gs_ridge   = GridSearchCV(ridge_pipe, ridge_grid, cv=5, scoring='r2', n_jobs=-1, verbose=0)
gs_ridge.fit(X_tr, y_tr)
print(f"  Best alpha : {gs_ridge.best_params_['model__alpha']}")
print(f"  Best CV R² : {gs_ridge.best_score_:.4f}")
m = regression_report(y_te, gs_ridge.predict(X_te), "Ridge (Tuned)")
print_report(m); tuned_results.append(m)
joblib.dump(gs_ridge.best_estimator_, 'models/Ridge_Tuned.joblib')


# ── 2. Random Forest — RandomizedSearchCV ─────────────────────────────────────
print("\n  Tuning Random Forest …")
rf_pipe  = Pipeline([("scaler", StandardScaler()), ("model", RandomForestRegressor(random_state=42, n_jobs=-1))])
rf_param = {
    "model__n_estimators"    : randint(100, 400),
    "model__max_depth"       : randint(5, 20),
    "model__min_samples_leaf": randint(2, 15),
    "model__max_features"    : ['sqrt', 'log2', 0.5, 0.7],
}
rs_rf = RandomizedSearchCV(rf_pipe, rf_param, n_iter=30, cv=5,
                           scoring='r2', n_jobs=-1, random_state=42, verbose=1)
rs_rf.fit(X_tr, y_tr)
print(f"  Best params: {rs_rf.best_params_}")
print(f"  Best CV R² : {rs_rf.best_score_:.4f}")
m = regression_report(y_te, rs_rf.predict(X_te), "Random Forest (Tuned)")
print_report(m); tuned_results.append(m)
joblib.dump(rs_rf.best_estimator_, 'models/RandomForest_Tuned.joblib')


# ── 3. Gradient Boosting — RandomizedSearchCV ─────────────────────────────────
print("\n  Tuning Gradient Boosting …")
gb_pipe  = Pipeline([("scaler", StandardScaler()), ("model", GradientBoostingRegressor(random_state=42))])
gb_param = {
    "model__n_estimators"  : randint(100, 500),
    "model__learning_rate" : uniform(0.01, 0.2),
    "model__max_depth"     : randint(3, 8),
    "model__subsample"     : uniform(0.6, 0.4),
    "model__min_samples_leaf": randint(5, 25),
}
rs_gb = RandomizedSearchCV(gb_pipe, gb_param, n_iter=30, cv=5,
                           scoring='r2', n_jobs=-1, random_state=42, verbose=1)
rs_gb.fit(X_tr, y_tr)
print(f"  Best params: {rs_gb.best_params_}")
print(f"  Best CV R² : {rs_gb.best_score_:.4f}")
m = regression_report(y_te, rs_gb.predict(X_te), "Gradient Boosting (Tuned)")
print_report(m); tuned_results.append(m)
joblib.dump(rs_gb.best_estimator_, 'models/GradientBoosting_Tuned.joblib')


# ── Tuning results plot ───────────────────────────────────────────────────────
plt.style.use('dark_background')
PALETTE = ['#6C63FF', '#43B89C', '#FC5C65']

fig, ax = plt.subplots(figsize=(9, 5))
names  = [r['model'] for r in tuned_results]
r2s    = [r['R²']    for r in tuned_results]
bars   = ax.bar(names, r2s, color=PALETTE, edgecolor='none', width=0.5)
ax.set_ylim(0.85, 1.0)
ax.set_ylabel('Test R²', color='white')
ax.set_title('Tuned Model Performance', fontsize=13, color='white')
ax.tick_params(colors='white'); plt.xticks(rotation=10)
for bar, val in zip(bars, r2s):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
            f'{val:.4f}', ha='center', va='bottom', fontsize=11, color='white', fontweight='bold')
plt.tight_layout()
plt.savefig('plots/10_tuned_models.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("\n✅  plots/10_tuned_models.png")
print("\n  ✅  Tuning complete! Best models saved to models/")
