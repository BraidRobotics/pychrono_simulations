from experiments import run_non_experiment
from database.queries.experiment_series_queries import select_all_experiment_series
from database.session import SessionLocal

if __name__ == '__main__':
    print("Generating model images for all experiment series...\n")
    print("=" * 70)

    session = SessionLocal()
    success_count = 0
    failure_count = 0

    try:
        all_experiment_series = select_all_experiment_series(session)
        total = len(all_experiment_series)

        print(f"Found {total} experiment series\n")

        for i, experiment_series in enumerate(all_experiment_series, 1):
            series_name = experiment_series.experiment_series_name
            print(f"[{i}/{total}] Generating model image for '{series_name}'...")

            try:
                run_non_experiment(experiment_series, will_visualize=False)
                print(f"  Success: assets/{series_name}/model.jpg")
                success_count += 1
            except Exception as e:
                print(f"  Failed: {e}")
                failure_count += 1

            print()
    finally:
        session.close()

    print("=" * 70)
    print(f"\nGeneration Summary:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failure_count}")
    print(f"  Total: {success_count + failure_count}")

    if success_count > 0:
        print(f"\nModel images saved to: assets/<experiment_series_name>/model.jpg")
