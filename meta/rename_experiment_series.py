from pathlib import Path
from database.session import SessionLocal
from database.models.experiment_series_model import ExperimentSeries
from database.models.experiment_model import Experiment
from sqlalchemy.exc import SQLAlchemyError


# "old_experiment_series_name": "new_experiment_series_name",
RENAME_MAPPINGS = {
    "strand_thickness_experiment__00": "strand_thickness_experiment__01",
    "strand_thickness_experiment__01": "strand_thickness_experiment__02",
    "strand_thickness_experiment__02": "strand_thickness_experiment__03",
    "strand_thickness_experiment__03": "strand_thickness_experiment__04",
    "strand_thickness_experiment__04": "strand_thickness_experiment__05",
    "strand_thickness_experiment__05": "strand_thickness_experiment__06",
    "number_of_strands__00": "number_of_strands__02",
    "number_of_strands__01": "number_of_strands__03",
    "number_of_strands__02": "number_of_strands__04",
    "number_of_strands__03": "number_of_strands__05",
    "number_of_strands__04": "number_of_strands__06",
    "number_of_strands__05": "number_of_strands__07",
    "number_of_strands__06": "number_of_strands__08",
    "number_of_layers__00": "number_of_layers__02",
    "number_of_layers__01": "number_of_layers__03",
    "number_of_layers__02": "number_of_layers__04",
    "number_of_layers__03": "number_of_layers__05",
    "number_of_layers__04": "number_of_layers__06",
    "number_of_layers__05": "number_of_layers__07",
    "number_of_layers__06": "number_of_layers__08",
}


def rename_experiment_series_graphs(old_name, new_name):
    """Rename graph files associated with an experiment series"""
    graphs_dir = Path(__file__).parent.parent / "experiments_server" / "assets" / "graphs"

    if not graphs_dir.exists():
        print(f"! Graphs directory does not exist: {graphs_dir}")
        return

    # Safe names (replacing slashes and spaces with underscores)
    old_safe_name = old_name.replace('/', '_').replace(' ', '_')
    new_safe_name = new_name.replace('/', '_').replace(' ', '_')

    graph_types = ['force', 'height', 'elastic_recovery']
    renamed_count = 0

    for graph_type in graph_types:
        old_file = graphs_dir / f"series_{old_safe_name}_{graph_type}.html"
        new_file = graphs_dir / f"series_{new_safe_name}_{graph_type}.html"

        if old_file.exists():
            old_file.rename(new_file)
            print(f"Renamed graph: {old_file.name} -> {new_file.name}")
            renamed_count += 1
        else:
            print(f"- Graph not found (skipping): {old_file.name}")

    if renamed_count == 0:
        print(f"- No graphs found to rename")

    return renamed_count


def rename_experiment_series(session, old_name, new_name):
    """
    Rename an experiment series and all its associated experiments.

    Args:
        session: Database session
        old_name: Current experiment series name
        new_name: New experiment series name

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if old series exists
        old_series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=old_name
        ).first()

        if not old_series:
            print(f"Experiment series '{old_name}' not found")
            return False

        # Check if new name already exists
        existing_series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=new_name
        ).first()

        if existing_series:
            print(f"Experiment series '{new_name}' already exists")
            return False

        print(f"\nRenaming: '{old_name}' → '{new_name}'")

        # Get all attributes from old series
        old_attrs = {key: value for key, value in old_series.__dict__.items()
                     if key != "_sa_instance_state" and key != "experiment_series_name"}

        # Step 1: Create new series with new name (this must exist before we update experiments due to foreign key)
        new_series = ExperimentSeries(experiment_series_name=new_name, **old_attrs)
        session.add(new_series)
        session.flush()  # Flush to make new series available for foreign key references
        print(f"  ✓ Created new series '{new_name}'")

        # Step 2: Update all experiments to reference the new series
        experiments = session.query(Experiment).filter_by(
            experiment_series_name=old_name
        ).all()

        print(f"  Updating {len(experiments)} experiment(s)...")
        for experiment in experiments:
            experiment.experiment_series_name = new_name
        session.flush()
        print(f"  ✓ Updated {len(experiments)} experiment(s)")

        # Step 3: Delete old series (safe now since no experiments reference it)
        session.delete(old_series)
        print(f"  ✓ Deleted old series '{old_name}'")

        # Commit all changes
        session.commit()
        print(f"  ✓ Database update complete")

        # Rename graph files
        print(f"  Renaming graph files...")
        rename_experiment_series_graphs(old_name, new_name)

        return True

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return False
    except Exception as e:
        session.rollback()
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main function to rename experiment series based on RENAME_MAPPINGS"""

    if not RENAME_MAPPINGS:
        print("No rename mappings defined. Please update RENAME_MAPPINGS in the script.")
        print("\nExample usage:")
        print('RENAME_MAPPINGS = {')
        print('    "old_name_1": "new_name_1",')
        print('    "old_name_2": "new_name_2",')
        print('}')
        return

    print(f"Starting rename operation for {len(RENAME_MAPPINGS)} series...\n")
    print("=" * 70)

    session = SessionLocal()
    success_count = 0
    failure_count = 0

    try:
        # Phase 1: Rename to temporary names to avoid conflicts
        print("\nPhase 1: Renaming to temporary names...")
        print("-" * 70)
        temp_mappings = {}
        phase1_failures = 0
        for old_name, new_name in RENAME_MAPPINGS.items():
            temp_name = f"__TEMP_RENAME__{old_name}"
            temp_mappings[old_name] = (temp_name, new_name)
            if rename_experiment_series(session, old_name, temp_name):
                pass  # Success message already printed by rename_experiment_series
            else:
                phase1_failures += 1

        # Phase 2: Rename from temporary names to final names
        print("\nPhase 2: Renaming to final names...")
        print("-" * 70)
        for old_name, (temp_name, new_name) in temp_mappings.items():
            if rename_experiment_series(session, temp_name, new_name):
                success_count += 1
            else:
                failure_count += 1

        failure_count += phase1_failures
    finally:
        session.close()

    print("\n" + "=" * 70)
    print(f"\nRename Summary:")
    print(f" Successful: {success_count}")
    print(f" Failed: {failure_count}")
    print(f" Total: {len(RENAME_MAPPINGS)}")

    if success_count > 0:
        print("\nNote: You may want to regenerate graphs with: make generate_graphs")


if __name__ == "__main__":
    main()
