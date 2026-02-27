"""
train.py  –  Train & evaluate 7 regression algorithms on the House Price dataset.

Models:
  1. Linear Regression
  2. Ridge Regression
  3. Lasso Regression
  4. Polynomial Regression (degree=2)
  5. Decision Tree Regressor
  6. Random Forest Regressor
  7. Gradient Boosting Regressor

Outputs:
  • models/  – saved .joblib model files
  • plots/   – EDA + evaluation PNG charts
  • model_comparison.csv
"""

import os, sys, warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing   import StandardScaler, PolynomialFeatures
from sklearn.pipeline        import Pipeline
from sklearn.linear_model    import LinearRegression, Ridge, Lasso
from sklearn.tree            import DecisionTreeRegressor
from sklearn.ensemble        import RandomForestRegressor, GradientBoostingRegressor
from sklearn.inspection      import permutation_importance

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))
from utils.helpers import add_features, regression_report, print_report, compare_models

# ── Style ─────────────────────────────────────────────────────────────────────
plt.style.use('dark_background')
PALETTE = ['#6C63FF', '#43B89C', '#FC5C65', '#F7B731', '#4ECDC4', '#FF6B9D', '#A8DADC']
sns.set_palette(PALETTE)


# ─────────────────────────────────────────────────────────────────────────────
# 1.  LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("   🏠  House Price Regression  –  ML Pipeline")
print("="*55)

df_raw = pd.read_csv('data/house_prices.csv')
df     = add_features(df_raw)

print(f"\n📦  Dataset shape  : {df.shape}")
print(f"📊  Price range    : ${df['price'].min():,.0f}  –  ${df['price'].max():,.0f}")
print(f"📈  Price mean     : ${df['price'].mean():,.0f}  (std=${df['price'].std():,.0f})")


# ─────────────────────────────────────────────────────────────────────────────
# 2.  EDA PLOTS
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs('plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

# 2a  Distribution of target
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Target Distribution  –  House Price', fontsize=14, color='white', y=1.01)

axes[0].hist(df['price'], bins=50, color=PALETTE[0], edgecolor='none', alpha=0.85)
axes[0].set_title('Raw Price Distribution', color='white')
axes[0].set_xlabel('Price (USD)', color='white')
axes[0].set_ylabel('Frequency', color='white')
axes[0].axvline(df['price'].median(), color=PALETTE[1], lw=2, label=f'Median ${df["price"].median():,.0f}')
axes[0].legend()

axes[1].hist(np.log1p(df['price']), bins=50, color=PALETTE[2], edgecolor='none', alpha=0.85)
axes[1].set_title('Log-Transformed Price', color='white')
axes[1].set_xlabel('log(Price + 1)', color='white')

plt.tight_layout()
plt.savefig('plots/01_price_distribution.png', dpi=150, bbox_inches='tight',
            facecolor='#0A0B0F')
plt.close()
print("✅  plots/01_price_distribution.png")

# 2b  Correlation heatmap
fig, ax = plt.subplots(figsize=(13, 10))
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, ax=ax, linewidths=0.5, annot_kws={"size": 8})
ax.set_title('Feature Correlation Matrix', fontsize=14, color='white', pad=12)
plt.tight_layout()
plt.savefig('plots/02_correlation_heatmap.png', dpi=150, bbox_inches='tight',
            facecolor='#0A0B0F')
plt.close()
print("✅  plots/02_correlation_heatmap.png")

# 2c  Feature vs Price scatter grid
features = ['area', 'age', 'distance_to_city', 'school_rating',
            'bedrooms', 'bathrooms', 'garage', 'pool']
fig, axes = plt.subplots(2, 4, figsize=(18, 8))
fig.suptitle('Features vs House Price', fontsize=14, color='white')
for ax, feat in zip(axes.flat, features):
    ax.scatter(df[feat], df['price'], alpha=0.3, s=10, color=PALETTE[0])
    ax.set_xlabel(feat, color='white', fontsize=9)
    ax.set_ylabel('Price', color='white', fontsize=9)
    ax.set_title(f'{feat}', color=PALETTE[1], fontsize=10)
plt.tight_layout()
plt.savefig('plots/03_feature_scatter.png', dpi=150, bbox_inches='tight',
            facecolor='#0A0B0F')
plt.close()
print("✅  plots/03_feature_scatter.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3.  TRAIN / TEST SPLIT
# ─────────────────────────────────────────────────────────────────────────────
FEATURE_COLS = [c for c in df.columns if c != 'price']
X = df[FEATURE_COLS]
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

print(f"\n🔀  Train size : {len(X_train):,}   |   Test size : {len(X_test):,}")
print(f"📋  Features   : {FEATURE_COLS}")


# ─────────────────────────────────────────────────────────────────────────────
# 4.  DEFINE MODELS
# ─────────────────────────────────────────────────────────────────────────────
models = {
    "Linear Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  LinearRegression())
    ]),
    "Ridge Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  Ridge(alpha=100))
    ]),
    "Lasso Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  Lasso(alpha=500, max_iter=10000))
    ]),
    "Polynomial Regression (d=2)": Pipeline([
        ("scaler", StandardScaler()),
        ("poly",   PolynomialFeatures(degree=2, include_bias=False, interaction_only=False)),
        ("model",  Ridge(alpha=10))          # Ridge on top to avoid overfitting
    ]),
    "Decision Tree": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  DecisionTreeRegressor(max_depth=8, min_samples_leaf=10, random_state=42))
    ]),
    "Random Forest": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  RandomForestRegressor(n_estimators=200, max_depth=12,
                                          min_samples_leaf=5, random_state=42, n_jobs=-1))
    ]),
    "Gradient Boosting": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  GradientBoostingRegressor(n_estimators=300, learning_rate=0.05,
                                              max_depth=5, subsample=0.8, random_state=42))
    ]),
}


# ─────────────────────────────────────────────────────────────────────────────
# 5.  TRAIN, EVALUATE & CROSS-VALIDATE
# ─────────────────────────────────────────────────────────────────────────────
kf       = KFold(n_splits=5, shuffle=True, random_state=42)
results  = []
cv_scores= {}

print("\n" + "="*55)
print("  Training & Evaluating Models …")
print("="*55)

for name, pipeline in models.items():
    # Train
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # Metrics
    m = regression_report(y_test, y_pred, name)
    print_report(m)
    results.append(m)

    # Cross-validation R²
    cv = cross_val_score(pipeline, X, y, cv=kf, scoring='r2', n_jobs=-1)
    cv_scores[name] = cv
    print(f"  CV R² : {cv.mean():.4f} ± {cv.std():.4f}")

    # Save model
    safe_name = name.replace(' ', '_').replace('(', '').replace(')', '').replace('=', '')
    joblib.dump(pipeline, f'models/{safe_name}.joblib')


# ─────────────────────────────────────────────────────────────────────────────
# 6.  COMPARISON TABLE
# ─────────────────────────────────────────────────────────────────────────────
comparison = compare_models(results)
comparison.to_csv('model_comparison.csv')
print("\n\n📋  Model Comparison (sorted by R²):\n")
print(comparison.to_string())


# ─────────────────────────────────────────────────────────────────────────────
# 7.  PLOTS – EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

# 7a  Model comparison bar chart
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Model Comparison', fontsize=15, color='white')
metrics_plot = ['R²', 'RMSE', 'MAPE %']
ylabels      = ['R² Score (higher=better)', 'RMSE $ (lower=better)', 'MAPE % (lower=better)']
for ax, metric, ylabel in zip(axes, metrics_plot, ylabels):
    vals   = comparison[metric]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(vals))]
    bars   = ax.barh(vals.index, vals.values, color=colors, edgecolor='none', height=0.6)
    ax.set_xlabel(ylabel, color='white')
    ax.set_title(metric, color='white', fontsize=12)
    ax.tick_params(colors='white')
    for bar, val in zip(bars, vals.values):
        ax.text(bar.get_width() * 0.98, bar.get_y() + bar.get_height()/2,
                f'{val:,.2f}', va='center', ha='right', fontsize=8, color='white')
plt.tight_layout()
plt.savefig('plots/04_model_comparison.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("\n✅  plots/04_model_comparison.png")

# 7b  Cross-validation box plots
fig, ax = plt.subplots(figsize=(14, 6))
cv_data  = [cv_scores[n] for n in comparison.index]
short    = [n.replace(' Regression','').replace(' (d=2)','') for n in comparison.index]
bplot = ax.boxplot(cv_data, patch_artist=True, notch=True, labels=short)
for patch, color in zip(bplot['boxes'], PALETTE):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
ax.set_title('5-Fold Cross-Validation R² Scores', fontsize=13, color='white')
ax.set_ylabel('R²', color='white')
ax.tick_params(colors='white', axis='both')
plt.xticks(rotation=25, ha='right')
plt.tight_layout()
plt.savefig('plots/05_cross_validation.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("✅  plots/05_cross_validation.png")

# 7c  Actual vs Predicted for best model
best_name = comparison.index[0]
best_pipe = models[best_name]
y_pred_best = best_pipe.predict(X_test)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(f'Best Model: {best_name}', fontsize=14, color='white')

# Actual vs Predicted scatter
axes[0].scatter(y_test, y_pred_best, alpha=0.4, s=12, color=PALETTE[0])
lims = [min(y_test.min(), y_pred_best.min()), max(y_test.max(), y_pred_best.max())]
axes[0].plot(lims, lims, 'r--', lw=1.5, label='Perfect Prediction')
axes[0].set_xlabel('Actual Price', color='white')
axes[0].set_ylabel('Predicted Price', color='white')
axes[0].set_title('Actual vs Predicted', color='white')
axes[0].legend()

# Residuals
residuals = y_test - y_pred_best
axes[1].scatter(y_pred_best, residuals, alpha=0.4, s=12, color=PALETTE[2])
axes[1].axhline(0, color='white', lw=1.5, linestyle='--')
axes[1].set_xlabel('Predicted Price', color='white')
axes[1].set_ylabel('Residuals', color='white')
axes[1].set_title('Residual Plot', color='white')
plt.tight_layout()
plt.savefig('plots/06_actual_vs_predicted.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("✅  plots/06_actual_vs_predicted.png")

# 7d  Residual distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Residual Analysis', fontsize=13, color='white')
axes[0].hist(residuals, bins=50, color=PALETTE[1], edgecolor='none', alpha=0.85)
axes[0].axvline(residuals.mean(), color='red', lw=2, label=f'Mean={residuals.mean():.0f}')
axes[0].set_title('Residual Distribution', color='white')
axes[0].set_xlabel('Residual ($)', color='white')
axes[0].legend()

from scipy import stats
stats.probplot(residuals, dist='norm', plot=axes[1])
axes[1].set_title('Q-Q Plot (Normality Check)', color='white')
axes[1].get_lines()[0].set(markerfacecolor=PALETTE[0], alpha=0.5, markersize=4)
axes[1].get_lines()[1].set(color='red', lw=2)
plt.tight_layout()
plt.savefig('plots/07_residual_analysis.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("✅  plots/07_residual_analysis.png")

# 7e  Feature Importance (Random Forest)
rf_pipe     = models["Random Forest"]
rf_model    = rf_pipe.named_steps['model']
importances = rf_model.feature_importances_
feat_imp    = pd.Series(importances, index=FEATURE_COLS).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
colors = [PALETTE[i % len(PALETTE)] for i in range(len(feat_imp))]
feat_imp.plot(kind='barh', ax=ax, color=colors, edgecolor='none')
ax.set_title('Feature Importance  –  Random Forest', fontsize=13, color='white')
ax.set_xlabel('Importance Score', color='white')
ax.tick_params(colors='white')
plt.tight_layout()
plt.savefig('plots/08_feature_importance.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("✅  plots/08_feature_importance.png")

# 7f  Learning curves (best model)
from sklearn.model_selection import learning_curve
train_sizes, train_scores, val_scores = learning_curve(
    best_pipe, X, y, cv=5, scoring='r2',
    train_sizes=np.linspace(0.1, 1.0, 15), n_jobs=-1)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(train_sizes, train_scores.mean(axis=1), 'o-', color=PALETTE[0], label='Train R²')
ax.fill_between(train_sizes,
                train_scores.mean(1) - train_scores.std(1),
                train_scores.mean(1) + train_scores.std(1), alpha=0.15, color=PALETTE[0])
ax.plot(train_sizes, val_scores.mean(axis=1), 'o-', color=PALETTE[1], label='Validation R²')
ax.fill_between(train_sizes,
                val_scores.mean(1) - val_scores.std(1),
                val_scores.mean(1) + val_scores.std(1), alpha=0.15, color=PALETTE[1])
ax.set_title(f'Learning Curves  –  {best_name}', fontsize=13, color='white')
ax.set_xlabel('Training Set Size', color='white')
ax.set_ylabel('R² Score', color='white')
ax.legend()
ax.tick_params(colors='white')
plt.tight_layout()
plt.savefig('plots/09_learning_curves.png', dpi=150, bbox_inches='tight', facecolor='#0A0B0F')
plt.close()
print("✅  plots/09_learning_curves.png")


# ─────────────────────────────────────────────────────────────────────────────
# 8.  PREDICTION DEMO
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  🏠  Sample Predictions  (Best Model)")
print("="*55)

sample_homes = pd.DataFrame([
    {"area": 1500, "bedrooms": 3, "bathrooms": 2,   "age": 10, "distance_to_city": 8,  "garage": 1, "pool": 0, "school_rating": 7.5},
    {"area": 3000, "bedrooms": 5, "bathrooms": 3.5, "age": 2,  "distance_to_city": 3,  "garage": 2, "pool": 1, "school_rating": 9.2},
    {"area": 800,  "bedrooms": 2, "bathrooms": 1,   "age": 35, "distance_to_city": 25, "garage": 0, "pool": 0, "school_rating": 5.0},
    {"area": 2200, "bedrooms": 4, "bathrooms": 2.5, "age": 8,  "distance_to_city": 12, "garage": 2, "pool": 0, "school_rating": 8.0},
])

sample_eng  = add_features(sample_homes)
predictions = best_pipe.predict(sample_eng[FEATURE_COLS])

print(f"\n  Using model: {best_name}\n")
for i, (_, row) in enumerate(sample_homes.iterrows()):
    print(f"  Home {i+1}: {row['area']}sqft, {int(row['bedrooms'])}bed/{row['bathrooms']}bath, "
          f"age={row['age']}y, dist={row['distance_to_city']}km  "
          f"→  Predicted: ${predictions[i]:>10,.0f}")


print("\n" + "="*55)
print("  ✅  All done!  Check plots/ and models/ folders.")
print("="*55 + "\n")
