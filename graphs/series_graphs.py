import plotly.graph_objects as go
from pathlib import Path
import pandas as pd

GRAPHS_DIR = Path(__file__).parent.parent / "experiments_server" / "assets" / "graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)


def _prepare_experiments_dataframe(experiments):
    experiments_dicts = [{k: v for k, v in exp.__dict__.items() if k != "_sa_instance_state"} for exp in experiments]
    return pd.DataFrame(experiments_dicts)


def generate_experiment_series_force_graph(session, safe_name, experiments):
    if not experiments:
        return None

    df = _prepare_experiments_dataframe(experiments)
    df = df[df['force_in_y_direction'].notna()]

    if df.empty:
        return None

    fig = go.Figure()

    df_no_explosion = df[df['time_to_bounding_box_explosion'].isna()]
    if not df_no_explosion.empty:
        fig.add_trace(go.Scatter(
            x=df_no_explosion['experiment_id'],
            y=df_no_explosion['force_in_y_direction'].abs(),
            mode='lines+markers',
            name='No Explosion',
            marker=dict(size=8, color='green'),
            line=dict(color='green', width=2),
            hovertemplate='<b>Experiment %{x}</b><br>Force: %{y:.3f} N<extra></extra>'
        ))

    df_exploded = df[df['time_to_bounding_box_explosion'].notna()]
    if not df_exploded.empty:
        fig.add_trace(go.Scatter(
            x=df_exploded['experiment_id'],
            y=df_exploded['force_in_y_direction'].abs(),
            mode='markers',
            name='Exploded',
            marker=dict(size=10, color='red', symbol='x'),
            hovertemplate='<b>Experiment %{x}</b><br>Force: %{y:.3f} N<br>(Exploded)<extra></extra>'
        ))

    fig.update_layout(
        title=f'Force vs Experiment ID - {safe_name}',
        xaxis_title='Experiment ID',
        yaxis_title='Force in Y Direction (N)',
        height=500,
        hovermode='closest',
        showlegend=True
    )

    output_path = GRAPHS_DIR / f"series_{safe_name}_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"series_{safe_name}_force.html"


def generate_experiment_series_height_graph(session, safe_name, experiments, initial_height):
    if not experiments or not initial_height:
        return None

    df = _prepare_experiments_dataframe(experiments)
    df = df[df['height_under_load'].notna() & df['force_in_y_direction'].notna()]

    if df.empty:
        return None

    df['height_reduction_pct'] = ((initial_height - df['height_under_load']) / initial_height) * 100

    fig = go.Figure()

    df_no_explosion = df[df['time_to_bounding_box_explosion'].isna()]
    if not df_no_explosion.empty:
        fig.add_trace(go.Scatter(
            x=df_no_explosion['force_in_y_direction'].abs(),
            y=df_no_explosion['height_reduction_pct'],
            mode='markers',
            name='No Explosion',
            marker=dict(size=10, color='green'),
            hovertemplate='<b>Force: %{x:.3f} N</b><br>Height Reduction: %{y:.1f}%<extra></extra>'
        ))

    df_exploded = df[df['time_to_bounding_box_explosion'].notna()]
    if not df_exploded.empty:
        fig.add_trace(go.Scatter(
            x=df_exploded['force_in_y_direction'].abs(),
            y=df_exploded['height_reduction_pct'],
            mode='markers',
            name='Exploded',
            marker=dict(size=12, color='red', symbol='x'),
            hovertemplate='<b>Force: %{x:.3f} N</b><br>Height Reduction: %{y:.1f}%<br>(Exploded)<extra></extra>'
        ))

    if not df.empty:
        fig.add_hline(y=10, line_dash="dash", line_color="orange", annotation_text="10% Target", annotation_position="right")

    fig.update_layout(
        title=f'Height Reduction vs Force - {safe_name}',
        xaxis_title='Force in Y Direction (N)',
        yaxis_title='Height Reduction (%)',
        height=500,
        hovermode='closest',
        showlegend=True
    )

    output_path = GRAPHS_DIR / f"series_{safe_name}_height.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"series_{safe_name}_height.html"
