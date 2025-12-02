#!/usr/bin/env python3
"""Run all material_thickness experiment series with 90-second sleep between each."""

import os
import sys
import time
from pathlib import Path

# Change to project root directory (two levels up from this script)
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

from database.session import SessionLocal
from database.models import ExperimentSeries
from experiments.run_experiments import run_experiments

def main():
    session = SessionLocal()

    # Get all material_thickness series, ordered by name
    series_list = session.query(ExperimentSeries).filter(
        ExperimentSeries.group_name == 'material_thickness'
    ).order_by(ExperimentSeries.experiment_series_name).all()

    print(f"Found {len(series_list)} material_thickness experiment series to run\n")

    for i, series in enumerate(series_list, 1):
        print(f"\n{'='*60}")
        print(f"Running series {i}/{len(series_list)}: {series.experiment_series_name}")
        print(f"{'='*60}\n")

        run_experiments(series)

        # Sleep between series (except after the last one)
        if i < len(series_list):
            print(f"\n⏸️  Sleeping for 90 seconds before next series...\n")
            time.sleep(90)

    session.close()
    print(f"\n✅ All {len(series_list)} material_thickness series completed!")

if __name__ == '__main__':
    main()
