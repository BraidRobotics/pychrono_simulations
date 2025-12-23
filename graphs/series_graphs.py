import plotly.graph_objects as go
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from graphs.graph_constants import TARGET_HEIGHT_REDUCTION_PERCENT

GRAPHS_DIR = Path(__file__).parent.parent / "experiments_server" / "assets" / "graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

# Font configuration for LaTeX compatibility
LATEX_FONT_CONFIG = {
    'family': 'Computer Modern, serif',
    'size': 18,
    'color': 'black'
}

TITLE_FONT_SIZE = 22
AXIS_TITLE_FONT_SIZE = 20
AXIS_TICK_FONT_SIZE = 16
LEGEND_FONT_SIZE = 16

def apply_latex_font_theme(fig):
    """Apply LaTeX-compatible font settings to a plotly figure"""
    fig.update_layout(
        font=LATEX_FONT_CONFIG,
        title_font_size=TITLE_FONT_SIZE,
        legend=dict(font_size=LEGEND_FONT_SIZE)
    )

    # Update all axes (works for both 2D plots)
    if hasattr(fig, 'update_xaxes'):
        fig.update_xaxes(title_font_size=AXIS_TITLE_FONT_SIZE, tickfont_size=AXIS_TICK_FONT_SIZE)
        fig.update_yaxes(title_font_size=AXIS_TITLE_FONT_SIZE, tickfont_size=AXIS_TICK_FONT_SIZE)

    return fig


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
        title=f'Force vs. Experiment ID - {safe_name}',
        xaxis_title='Experiment ID',
        yaxis_title='Force in Y Direction (N)',
        height=500,
        hovermode='closest',
        showlegend=True
    )
    apply_latex_font_theme(fig)

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

        if len(df_no_explosion) >= 3:
            X = df_no_explosion['force_in_y_direction'].abs().values.reshape(-1, 1)
            y = df_no_explosion['height_reduction_pct'].values

            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            model = LinearRegression()
            model.fit(X_poly, y)

            X_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
            X_range_poly = poly_features.transform(X_range)
            y_pred = model.predict(X_range_poly)

            r2 = r2_score(y, model.predict(X_poly))

            fig.add_trace(go.Scatter(
                x=X_range.flatten(),
                y=y_pred,
                mode='lines',
                name=f'Polynomial Fit (R²={r2:.3f})',
                line=dict(color='blue', width=2, dash='dash'),
                hovertemplate='<b>Force: %{x:.3f} N</b><br>Predicted: %{y:.1f}%<extra></extra>'
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
        fig.add_hline(
            y=TARGET_HEIGHT_REDUCTION_PERCENT,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"{TARGET_HEIGHT_REDUCTION_PERCENT:.0f}% Target",
            annotation_position="right"
        )

    fig.update_layout(
        title=f'Height Reduction vs. Force - {safe_name}',
        xaxis_title='Force in Y Direction (N)',
        yaxis_title='Height Reduction (%)',
        height=500,
        hovermode='closest',
        showlegend=True
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / f"series_{safe_name}_height.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"series_{safe_name}_height.html"


def generate_experiment_series_elastic_recovery_graph(session, safe_name, experiments, reset_force_after_seconds, initial_height):
    if not experiments or reset_force_after_seconds is None:
        return None

    # Import the filter function for force_no_force experiments
    from database.queries.graph_queries import filter_force_no_force_experiments

    # Apply comprehensive filtering including monotonicity check
    valid_experiments = filter_force_no_force_experiments(experiments, initial_height)

    if not valid_experiments:
        return None

    df = _prepare_experiments_dataframe(valid_experiments)

    if df.empty:
        return None

    # Calculate recovery ratio: 1.0 = full recovery, 0 = stayed compressed
    # recovery = (final_height - height_under_load) / (initial_height - height_under_load)
    df['recovery'] = (df['final_height'] - df['height_under_load']) / (initial_height - df['height_under_load'])

    fig = go.Figure()

    # All experiments in df are valid (no explosions, passed monotonicity check)
    fig.add_trace(go.Scatter(
        x=df['height_under_load'],
        y=df['recovery'],
        mode='markers',
        name='Valid Data',
        marker=dict(size=10, color='blue'),
        hovertemplate='<b>Height Under Load: %{x:.4f} m</b><br>Recovery: %{y:.2%}<extra></extra>'
    ))

    # Show filtered out experiments as invalid
    all_experiments_df = _prepare_experiments_dataframe(experiments)
    invalid_experiments_df = all_experiments_df[~all_experiments_df['experiment_id'].isin(df['experiment_id'])]
    invalid_experiments_df = invalid_experiments_df[invalid_experiments_df['height_under_load'].notna() & invalid_experiments_df['final_height'].notna()]

    if not invalid_experiments_df.empty:
        invalid_experiments_df['recovery'] = (invalid_experiments_df['final_height'] - invalid_experiments_df['height_under_load']) / (initial_height - invalid_experiments_df['height_under_load'])
        fig.add_trace(go.Scatter(
            x=invalid_experiments_df['height_under_load'],
            y=invalid_experiments_df['recovery'],
            mode='markers',
            name='Filtered (Anomalous)',
            marker=dict(size=12, color='red', symbol='x'),
            hovertemplate='<b>Height Under Load: %{x:.4f} m</b><br>Recovery: %{y:.2%}<br>(Filtered: Structural Compromise)<extra></extra>'
        ))

    # Add horizontal line at 1.0 (perfect recovery)
    if not df.empty:
        fig.add_hline(
            y=1.0,
            line_dash="dot",
            line_color="gray",
            annotation_text="Full Recovery (100%)",
            annotation_position="right"
        )

    fig.update_layout(
        title=f'Elastic Recovery - {safe_name}',
        xaxis_title='Height Under Load (m)',
        yaxis_title='Recovery Ratio',
        yaxis=dict(range=[0, 1.1], tickformat='.0%'),
        height=500,
        hovermode='closest',
        showlegend=True
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / f"series_{safe_name}_elastic_recovery.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"series_{safe_name}_elastic_recovery.html"
