#!/usr/bin/env python3
"""Run all number_of_layers experiment series with 90-second sleep between each."""

import sys
import time
sys.path.insert(0, '.')

from database.session import SessionLocal
from database.models import ExperimentSeries
from experiments.run_experiments import run_experiments

def main():
    session = SessionLocal()

    # Get all number_of_layers series, ordered by name
    series_list = session.query(ExperimentSeries).filter(
        ExperimentSeries.group_name == 'number_of_layers'
    ).order_by(ExperimentSeries.experiment_series_name).all()

    print(f"Found {len(series_list)} number_of_layers experiment series to run\n")

    for i, series in enumerate(series_list, 1):
        print(f"\n{'='*60}")
        print(f"Running series {i}/{len(series_list)}: {series.experiment_series_name}")
        print(f"{'='*60}\n")

        run_experiments(series)

        # Sleep between series (except after the last one)
        if i < len(series_list):
            print(f"\n⏸️  Sleeping for 90 seconds before next series...\n")
            time.sleep(40)

    session.close()
    print(f"\n✅ All {len(series_list)} number_of_layers series completed!")

if __name__ == '__main__':
    main()
