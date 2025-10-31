import plotly.express as px
from pathlib import Path
import pandas as pd

from database.queries.graph_queries import (
    get_material_thickness_vs_weight_chart_values,
    get_load_capacity_ratio_y_chart_values
)

# Define where graphs will be saved (experiments_server/assets/graphs/)
GRAPHS_DIR = Path(__file__).parent.parent / "assets" / "graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)


def generate_load_capacity_ratio_graph(session, force_direction='y'):
    # Get data from database
    data = get_load_capacity_ratio_y_chart_values(session)

    if not data:
        return None

    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)

    # Create scatter plot with trendline
    fig = px.scatter(
        df,
        x='force',
        y='load_capacity_ratio',
        hover_data=['experiment_series_name'],
        labels={
            'force': 'Force (N)',
            'load_capacity_ratio': 'Payload to Weight Ratio',
            'experiment_series_name': 'Experiment Series'
        },
        title='Load Capacity Ratio',
        trendline='ols',
        trendline_color_override='red'
    )

    # Update marker size
    fig.update_traces(marker=dict(size=10))

    # Add subtitle with note
    fig.add_annotation(
        text="Note: This finds experiments with 10% height reduction that did not explode.<br>"
             "Filters out series where all experiments exploded or none did.",
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=10, color="gray"),
        align="center"
    )

    # Get R² value from trendline
    try:
        results = px.get_trendline_results(fig)
        # Handle both DataFrame and list return types
        if hasattr(results, 'empty'):
            # It's a DataFrame
            if not results.empty:
                r_squared = results.iloc[0]["px_fit_results"].rsquared
                # Add R² annotation
                fig.add_annotation(
                    text=f"R² = {r_squared:.3f}",
                    xref="paper", yref="paper",
                    x=0.05, y=0.95,
                    showarrow=False,
                    font=dict(size=12),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="gray",
                    borderwidth=1
                )
        elif isinstance(results, list) and len(results) > 0:
            # It's a list
            r_squared = results[0].rsquared
            # Add R² annotation
            fig.add_annotation(
                text=f"R² = {r_squared:.3f}",
                xref="paper", yref="paper",
                x=0.05, y=0.95,
                showarrow=False,
                font=dict(size=12),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="gray",
                borderwidth=1
            )
    except Exception as e:
        print(f"Could not calculate R²: {e}")

    # Update layout for better appearance
    fig.update_layout(
        height=500,
        margin=dict(b=100),  # More bottom margin for the note
        hovermode='closest'
    )

    # Save as HTML
    output_path = GRAPHS_DIR / f"load_capacity_ratio_{force_direction}.html"
    fig.write_html(
        str(output_path),
        include_plotlyjs='cdn',  # Use CDN for smaller file size
        config={'displayModeBar': True, 'displaylogo': False}
    )

    return f"load_capacity_ratio_{force_direction}.html"


def generate_material_thickness_weight_graph(session):
    # Get data from database
    data = get_material_thickness_vs_weight_chart_values(session)

    if not data:
        return None

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Convert thickness to mm for better readability
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    # Create scatter plot
    fig = px.scatter(
        df,
        x='material_thickness_mm',
        y='weight_kg',
        hover_data=['experiment_series_name'],
        labels={
            'material_thickness_mm': 'Material Thickness (mm)',
            'weight_kg': 'Weight (kg)',
            'experiment_series_name': 'Experiment Series'
        },
        title='Material Thickness vs Weight',
        trendline='ols',
        trendline_color_override='red'
    )

    # Update marker size
    fig.update_traces(marker=dict(size=10, color='blue'))

    # Get R² value
    try:
        results = px.get_trendline_results(fig)
        # Handle both DataFrame and list return types
        if hasattr(results, 'empty'):
            # It's a DataFrame
            if not results.empty:
                r_squared = results.iloc[0]["px_fit_results"].rsquared
                fig.add_annotation(
                    text=f"R² = {r_squared:.3f}",
                    xref="paper", yref="paper",
                    x=0.05, y=0.95,
                    showarrow=False,
                    font=dict(size=12),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="gray",
                    borderwidth=1
                )
        elif isinstance(results, list) and len(results) > 0:
            # It's a list
            r_squared = results[0].rsquared
            fig.add_annotation(
                text=f"R² = {r_squared:.3f}",
                xref="paper", yref="paper",
                x=0.05, y=0.95,
                showarrow=False,
                font=dict(size=12),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="gray",
                borderwidth=1
            )
    except Exception as e:
        print(f"Could not calculate R² for material thickness graph: {e}")

    # Update layout
    fig.update_layout(
        height=500,
        hovermode='closest'
    )

    # Save as HTML
    output_path = GRAPHS_DIR / "material_thickness_vs_weight.html"
    fig.write_html(
        str(output_path),
        include_plotlyjs='cdn',
        config={'displayModeBar': True, 'displaylogo': False}
    )

    return "material_thickness_vs_weight.html"
