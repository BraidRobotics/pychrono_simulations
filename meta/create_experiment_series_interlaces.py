from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import SessionLocal

num_experiment_series = 7
num_experiments = 48
base_name = "strand_thickness_"

# Create all 7 series with evenly spaced thickness values
initial_thickness = 0.002  # 2mm
final_thickness = 0.008     # 8mm

session = SessionLocal()

for i in range(num_experiment_series):
    # Calculate thickness for this series
    thickness = initial_thickness + (final_thickness - initial_thickness) * i / (num_experiment_series - 1)

    # Create series name: strand_thickness__002, strand_thickness__003, etc.
    thickness_mm = int(thickness * 1000)
    series_name = f"{base_name}_{thickness_mm:03d}"

    model = ExperimentSeries(
        experiment_series_name=series_name,
        group_name="strand_thickness",
        num_experiments=num_experiments,
        strand_radius=thickness,
        initial_force_applied_in_y_direction=0.0,
        final_force_in_y_direction=-4.0,
    )

    insert_experiment_series(session, model)
    print(f"Created: {series_name} with thickness {thickness*1000:.1f}mm")

session.commit()
session.close()
print(f"\nSuccessfully created {num_experiment_series} material thickness experiment series!")
