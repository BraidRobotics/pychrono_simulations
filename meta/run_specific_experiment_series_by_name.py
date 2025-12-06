import sys
import time

from database.session import get_session, close_global_session
from database.models import ExperimentSeries
from experiments.run_experiments import run_experiments

EXPERIMENT_SERIES_NAMES = [
    "test_run_specific_script",
]

SLEEP_BETWEEN_SERIES_SECONDS = 90

def main():
    if not EXPERIMENT_SERIES_NAMES:
        print("ERROR: EXPERIMENT_SERIES_NAMES is empty!")
        print("Please edit this file and add experiment series names to the array.")
        sys.exit(1)

    session = get_session()

    # Fetch all requested series
    series_list = session.query(ExperimentSeries).filter(
        ExperimentSeries.experiment_series_name.in_(EXPERIMENT_SERIES_NAMES)
    ).all()

    # Check for missing series
    found_names = {s.experiment_series_name for s in series_list}
    missing_names = set(EXPERIMENT_SERIES_NAMES) - found_names

    if missing_names:
        print(f"WARNING: Could not find the following experiment series:")
        for name in sorted(missing_names):
            print(f"  - {name}")
        print()

    if not series_list:
        print("ERROR: No valid experiment series found!")
        close_global_session()
        sys.exit(1)

    print(f"Found {len(series_list)} experiment series to run:")
    for s in series_list:
        print(f"  - {s.experiment_series_name}")
    print()

    # Run each series
    for i, series in enumerate(series_list, 1):
        print(f"\n{'='*60}")
        print(f"Running series {i}/{len(series_list)}: {series.experiment_series_name}")
        print(f"{'='*60}\n")

        run_experiments(series)

        print(f"\n⏸️  Sleeping for {SLEEP_BETWEEN_SERIES_SECONDS} seconds before next series...\n")
        time.sleep(SLEEP_BETWEEN_SERIES_SECONDS)

    close_global_session()
    print(f"\n✅ All {len(series_list)} series completed!")


if __name__ == '__main__':
    main()
