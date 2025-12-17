from database.session import scoped_session
from database.queries.experiment_series_queries import select_all_experiment_series
from graphs.generate_after_experiments import generate_graphs_after_experiments
from graphs.aggregate_graphs import generate_aggregate_graphs_for_group

if __name__ == "__main__":
    with scoped_session() as session:
        experiment_series_list = select_all_experiment_series(session)

        # Track which groups we've processed
        processed_groups = set()

        for experiment_series in experiment_series_list:
            # Generate series-specific graphs
            generate_graphs_after_experiments(experiment_series)

            # Generate aggregate graphs for this group (only once per group)
            if experiment_series.group_name and experiment_series.group_name not in processed_groups:
                generate_aggregate_graphs_for_group(session, experiment_series.group_name)
                processed_groups.add(experiment_series.group_name)

        print("\nAll graphs generated successfully!")
