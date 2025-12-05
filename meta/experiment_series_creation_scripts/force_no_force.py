from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import SessionLocal

# Factorial design: 3 strand values × 3 layer values = 9 experiment series
num_experiments = 46
interlaced_experiment_series_name = "force_no_force_"
group_name = "force_no_force"

# Define factorial grid
strand_values = [4, 6, 8]  # All divisible by 2
layer_values = [3, 5, 7]   # Low, medium, high
strand_radius = 0.007  # Constant

session = SessionLocal()

# Create all combinations
series_index = 0
for num_strands in strand_values:
    for num_layers in layer_values:
        model = ExperimentSeries(
            experiment_series_name=f"{interlaced_experiment_series_name}{series_index:02d}",
            group_name=group_name,
            num_experiments=num_experiments,
            num_strands=num_strands,
            num_layers=num_layers,
            strand_radius=strand_radius,
            initial_force_applied_in_y_direction=0.0,
            final_force_in_y_direction=-3.0,
            max_simulation_time=20.0,
            reset_force_after_seconds=10.0
        )
        insert_experiment_series(session, model)
        series_index += 1
