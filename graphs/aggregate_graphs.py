import plotly.express as px
from pathlib import Path
import pandas as pd

from database.queries.graph_queries import (
    get_material_thickness_vs_weight_chart_values,
    get_material_thickness_vs_force_chart_values,
    get_load_capacity_ratio_y_chart_values
)

GRAPHS_DIR = Path(__file__).parent.parent / "experiments_server" / "assets" / "graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)


def _add_r_squared_annotation(fig):
    try:
        results = px.get_trendline_results(fig)
        if hasattr(results, 'empty'):
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
        print(f"Could not calculate R²: {e}")


def generate_load_capacity_ratio_graph(session, force_direction='y'):
    data = get_load_capacity_ratio_y_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = px.scatter(
        df,
        x='force',
        y='specific_load_capacity',
        hover_data=['experiment_series_name'],
        labels={
            'force': 'Force at 10% Compression (N)',
            'specific_load_capacity': 'Load Capacity (times its own weight)',
            'experiment_series_name': 'Experiment Series'
        },
        title='Specific Load Capacity at 10% Compression',
        trendline='ols',
        trendline_color_override='red'
    )

    fig.update_traces(marker=dict(size=10))

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=10, color="gray"),
        align="center"
    )

    _add_r_squared_annotation(fig)

    fig.update_layout(height=500, margin=dict(b=100), hovermode='closest')

    output_path = GRAPHS_DIR / f"load_capacity_ratio_{force_direction}.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"load_capacity_ratio_{force_direction}.html"


def generate_material_thickness_weight_graph(session):
    data = get_material_thickness_vs_weight_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

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

    fig.update_traces(marker=dict(size=10, color='blue'))
    _add_r_squared_annotation(fig)
    fig.update_layout(height=500, hovermode='closest')

    output_path = GRAPHS_DIR / "material_thickness_vs_weight.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "material_thickness_vs_weight.html"


def generate_material_thickness_force_graph(session):
    data = get_material_thickness_vs_force_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    fig = px.scatter(
        df,
        x='material_thickness_mm',
        y='force',
        hover_data=['experiment_series_name'],
        labels={
            'material_thickness_mm': 'Material Thickness (mm)',
            'force': 'Force at 10% Height Reduction (N)',
            'experiment_series_name': 'Experiment Series'
        },
        title='Material Thickness vs Force Capacity',
        trendline='ols',
        trendline_color_override='red'
    )

    fig.update_traces(marker=dict(size=10, color='blue'))
    _add_r_squared_annotation(fig)
    fig.update_layout(height=500, hovermode='closest')

    output_path = GRAPHS_DIR / "material_thickness_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "material_thickness_vs_force.html"
