"""
orchestrator/pipeline.py  –  Master Pipeline Orchestrator

Wires all 7 stages into a single executable pipeline with:
  • Stage dependency tracking
  • Per-stage timing & metrics
  • Graceful error handling & partial recovery
  • Run manifest saved as JSON

Run:
    python orchestrator/pipeline.py
    python orchestrator/pipeline.py --stages ingest quality transform   # partial run
    python orchestrator/pipeline.py --skip-ml                           # skip ML training
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import argparse
import json
from datetime import datetime
from pathlib import Path

from utils.logger  import get_logger
from utils.metrics import PipelineMetrics

log = get_logger("orchestrator")


# ─────────────────────────────────────────────────────────────────────────────
# Stage Registry
# ─────────────────────────────────────────────────────────────────────────────
STAGE_ORDER = [
    "ingest",
    "quality",
    "transform",
    "warehouse",
    "analytics",
    "ml",
    "report",
]

STAGE_LABELS = {
    "ingest"    : "Stage 1 — Ingestion",
    "quality"   : "Stage 2 — Data Quality",
    "transform" : "Stage 3 — Transformation",
    "warehouse" : "Stage 4 — Data Warehouse",
    "analytics" : "Stage 5 — Analytics",
    "ml"        : "Stage 6 — ML Forecasting",
    "report"    : "Stage 7 — Reporting",
}


def run_pipeline(stages: list[str] | None = None, skip_ml: bool = False):
    run_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
    pm      = PipelineMetrics(run_id)

    active  = stages or STAGE_ORDER
    if skip_ml and "ml" in active:
        active = [s for s in active if s != "ml"]

    log.info("=" * 60)
    log.info(f"  HEALTH ANALYTICS PIPELINE  —  Run ID: {run_id}")
    log.info(f"  Stages to execute: {active}")
    log.info("=" * 60)

    # State bag passed between stages
    state = {}

    for stage in active:
        if stage not in STAGE_ORDER:
            log.warning(f"Unknown stage '{stage}', skipping"); continue

        label = STAGE_LABELS[stage]
        log.info(f"\n{'▶'*3}  {label}")

        try:
            # ── 1. Ingest ──────────────────────────────────────────────────
            if stage == "ingest":
                from ingestion.ingestor import run as ingest_run
                state["raw_df"], state["ingest_meta"] = ingest_run(pm)

            # ── 2. Quality ─────────────────────────────────────────────────
            elif stage == "quality":
                if "raw_df" not in state:
                    raise RuntimeError("'quality' requires 'ingest' to have run first")
                from processing.quality import run as quality_run
                state["clean_df"], state["quality_report"] = quality_run(state["raw_df"], pm)

            # ── 3. Transform ───────────────────────────────────────────────
            elif stage == "transform":
                src = state.get("clean_df", state.get("raw_df"))
                if src is None:
                    raise RuntimeError("'transform' requires a dataframe in state")
                from processing.transformer import run as transform_run
                state["feat_df"], state["transform_meta"] = transform_run(src, pm)

            # ── 4. Warehouse ───────────────────────────────────────────────
            elif stage == "warehouse":
                if "feat_df" not in state:
                    raise RuntimeError("'warehouse' requires 'transform' to have run first")
                from storage.warehouse import run as warehouse_run
                state["conn"], state["wh_meta"] = warehouse_run(state["feat_df"], pm)

            # ── 5. Analytics ───────────────────────────────────────────────
            elif stage == "analytics":
                if "conn" not in state:
                    # Try to reconnect if DB exists
                    import sqlite3
                    from config import DB_PATH
                    if DB_PATH.exists():
                        state["conn"] = sqlite3.connect(str(DB_PATH))
                    else:
                        raise RuntimeError("'analytics' requires 'warehouse' to have run first")
                from analytics.analyzer import run as analytics_run
                state["analytics"] = analytics_run(state["conn"], pm)

            # ── 6. ML ──────────────────────────────────────────────────────
            elif stage == "ml":
                if "feat_df" not in state:
                    import pandas as pd
                    from config import DATA_PROCESSED
                    csv = DATA_PROCESSED / "covid_processed.csv"
                    if csv.exists():
                        state["feat_df"] = pd.read_csv(csv, parse_dates=["date"])
                    else:
                        raise RuntimeError("'ml' requires 'transform' to have run first")
                from ml.forecaster import run as ml_run
                state["ml_results"] = ml_run(state["feat_df"], pm)

            # ── 7. Report ──────────────────────────────────────────────────
            elif stage == "report":
                df = state.get("feat_df")
                if df is None:
                    import pandas as pd
                    from config import DATA_PROCESSED
                    df = pd.read_csv(DATA_PROCESSED / "covid_processed.csv",
                                     parse_dates=["date"])

                analytics  = state.get("analytics", {})
                ml_results = state.get("ml_results", {})
                from reporting.reporter import run as report_run
                state["report"] = report_run(df, analytics, ml_results, pm, pm)

        except Exception as e:
            log.error(f"Stage '{stage}' FAILED: {e}")
            pm.fail_stage(f"{STAGE_ORDER.index(stage)+1}_{stage}", str(e))
            # Continue to next stage where possible
            continue

    # ── Finalise ─────────────────────────────────────────────────────────────
    manifest_path = pm.save(Path(__file__).parent.parent / "logs")
    log.info(f"\nRun manifest saved → {manifest_path}")
    log.info(pm.summary())

    return state, pm


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health Analytics Data Pipeline")
    parser.add_argument("--stages",   nargs="+", choices=STAGE_ORDER,
                        help="Run only these stages (in order)")
    parser.add_argument("--skip-ml",  action="store_true",
                        help="Skip the ML forecasting stage")
    args = parser.parse_args()

    state, metrics = run_pipeline(
        stages  = args.stages,
        skip_ml = args.skip_ml,
    )

    print("\n  Pipeline finished. Check:")
    print("  • plots/          — all visualisation charts")
    print("  • PIPELINE_REPORT.txt — full analytics report")
    print("  • data/warehouse/health_dw.db — SQLite data warehouse")
    print("  • logs/           — structured execution logs")
