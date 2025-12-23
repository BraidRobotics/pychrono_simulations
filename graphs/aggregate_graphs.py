import plotly.express as px
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from database.queries.graph_queries import (
    get_strand_radius_vs_weight_chart_values,
    get_strand_radius_vs_force_chart_values,
    get_load_capacity_ratio_y_chart_values,
    get_strand_radius_vs_efficiency_chart_values,
    get_thickness_height_reduction_vs_force_data,
    get_layer_count_vs_height_chart_values,
    get_layer_count_vs_force_chart_values,
    get_layer_count_vs_efficiency_chart_values,
    get_layer_height_reduction_vs_force_data,
    get_strand_count_vs_weight_chart_values,
    get_strand_count_vs_force_chart_values,
    get_strand_count_vs_efficiency_chart_values,
    get_strand_height_reduction_vs_force_data,
    get_force_no_force_recovery_data,
    get_force_no_force_equilibrium_data,
    get_force_no_force_compression_data,
    get_force_no_force_stiffness_data,
    get_force_no_force_recovery_consistency_data,
    get_strand_count_stiffness_vs_compression_data,
    get_strand_count_force_vs_displacement_data,
    get_load_bearing_parameter_importance_data
)
from database.queries.experiment_series_queries import select_experiment_series_by_name

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

    # For 3D plots - update scene axes
    if 'scene' in fig.layout:
        fig.update_layout(
            scene=dict(
                xaxis=dict(title_font_size=AXIS_TITLE_FONT_SIZE, tickfont_size=AXIS_TICK_FONT_SIZE),
                yaxis=dict(title_font_size=AXIS_TITLE_FONT_SIZE, tickfont_size=AXIS_TICK_FONT_SIZE),
                zaxis=dict(title_font_size=AXIS_TITLE_FONT_SIZE, tickfont_size=AXIS_TICK_FONT_SIZE)
            )
        )

    return fig



def generate_load_capacity_ratio_graph(session, force_direction='y'):
    data = get_load_capacity_ratio_y_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    # Add weight in kg for x-axis
    from database.queries.graph_queries import get_weight_for_series
    df['weight_kg'] = df['experiment_series_name'].apply(lambda name: get_weight_for_series(session, name))

    fig = px.scatter(
        df,
        x='weight_kg',
        y='specific_load_capacity',
        hover_data=['experiment_series_name', 'force'],
        labels={
            'weight_kg': 'Structure Weight (kg)',
            'specific_load_capacity': 'Force / (Weight × g) where g=9.81 m/s²',
            'experiment_series_name': 'Experiment Series',
            'force': 'Force (N)'
        },
        title='Structural Efficiency: Specific Load Capacity vs. Weight'
    )

    fig.update_traces(marker=dict(size=10))

    fig.update_layout(height=500, hovermode='closest')
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / f"load_capacity_ratio_{force_direction}.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"load_capacity_ratio_{force_direction}.html"


def generate_strand_thickness_weight_graph(session):

    data = get_strand_radius_vs_weight_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['strand_thickness_mm'],
        y=df['weight_kg'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='green'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Material Thickness: %{x:.2f} mm<br>Weight: %{y:.4f} kg<extra></extra>'
    ))

    # Add theoretical quadratic scaling (Weight ∝ thickness²)
    if len(df) > 1:
        t_min, t_max = df['strand_thickness_mm'].min(), df['strand_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Fit a quadratic through the origin: W = k*t² (since W ∝ t² from cross-sectional area)
        # Using least squares: k = sum(t²*w) / sum(t⁴)
        k = np.sum(df['strand_thickness_mm']**2 * df['weight_kg']) / np.sum(df['strand_thickness_mm']**4)
        w_quadratic = k * t_range**2

        fig.add_trace(go.Scatter(
            x=t_range,
            y=w_quadratic,
            mode='lines',
            name='Theoretical Quadratic (W ∝ t²)',
            line=dict(dash='dash', color='red', width=2),
            hovertemplate='Expected quadratic scaling (cross-sectional area)<extra></extra>'
        ))

    fig.update_layout(
        title='Weight Scaling with Material Thickness',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Weight (kg)',
        height=500,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_thickness_vs_weight.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_thickness_vs_weight.html"


def generate_strand_thickness_force_graph(session):

    data = get_strand_radius_vs_force_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['strand_thickness_mm'],
        y=df['force'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='blue'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Material Thickness: %{x:.2f} mm<br>Force: %{y:.3f} N<extra></extra>'
    ))

    # Add theoretical scaling curves
    if len(df) > 1:
        t_min, t_max = df['strand_thickness_mm'].min(), df['strand_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Normalize to first data point for comparison
        t0 = df['strand_thickness_mm'].iloc[0]
        f0 = df['force'].iloc[0]

        # Linear scaling: F ∝ t
        f_linear = f0 * (t_range / t0)
        fig.add_trace(go.Scatter(
            x=t_range,
            y=f_linear,
            mode='lines',
            name='Linear (F ∝ t)',
            line=dict(dash='dot', color='gray', width=1),
            hovertemplate='Linear scaling<extra></extra>'
        ))

        # Quadratic scaling: F ∝ t²
        f_quadratic = f0 * (t_range / t0) ** 2
        fig.add_trace(go.Scatter(
            x=t_range,
            y=f_quadratic,
            mode='lines',
            name='Quadratic (F ∝ t²)',
            line=dict(dash='dash', color='orange', width=2),
            hovertemplate='Quadratic scaling<extra></extra>'
        ))

        # Quartic scaling: F ∝ t⁴ (from I = πr⁴/4)
        f_quartic = f0 * (t_range / t0) ** 4
        fig.add_trace(go.Scatter(
            x=t_range,
            y=f_quartic,
            mode='lines',
            name='Quartic (F ∝ t⁴)',
            line=dict(dash='dashdot', color='purple', width=2),
            hovertemplate='Quartic scaling (beam theory)<extra></extra>'
        ))

    fig.update_layout(
        title='Load-Bearing Capacity vs. Material Thickness (with Theoretical Scaling)',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Force at 10% Height Reduction (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_thickness_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_thickness_vs_force.html"


def generate_strand_thickness_efficiency_graph(session):

    data = get_strand_radius_vs_efficiency_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['strand_thickness_mm'],
        y=df['specific_load_capacity'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='darkgreen'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Material Thickness: %{x:.2f} mm<br>Efficiency: %{y:.2f}×<extra></extra>'
    ))

    # Add theoretical cubic scaling (Efficiency ∝ t³)
    # If F ∝ t⁴ and W ∝ t, then F/W ∝ t³
    if len(df) > 1:
        t_min, t_max = df['strand_thickness_mm'].min(), df['strand_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Normalize to first data point
        t0 = df['strand_thickness_mm'].iloc[0]
        e0 = df['specific_load_capacity'].iloc[0]

        # Cubic scaling: Efficiency ∝ t³ (if buckling-dominated)
        e_cubic = e0 * (t_range / t0) ** 3
        fig.add_trace(go.Scatter(
            x=t_range,
            y=e_cubic,
            mode='lines',
            name='Theoretical Cubic (E ∝ t³)',
            line=dict(dash='dash', color='purple', width=2),
            hovertemplate='Cubic scaling (buckling)<extra></extra>'
        ))

        # Linear scaling: Efficiency ∝ t (if bending-dominated)
        e_linear = e0 * (t_range / t0)
        fig.add_trace(go.Scatter(
            x=t_range,
            y=e_linear,
            mode='lines',
            name='Theoretical Linear (E ∝ t)',
            line=dict(dash='dot', color='orange', width=2),
            hovertemplate='Linear scaling (bending)<extra></extra>'
        ))

        # Constant efficiency (if axial-dominated)
        e_constant = np.full_like(t_range, e0)
        fig.add_trace(go.Scatter(
            x=t_range,
            y=e_constant,
            mode='lines',
            name='Constant (E ∝ t⁰)',
            line=dict(dash='dashdot', color='gray', width=1),
            hovertemplate='Constant efficiency (axial)<extra></extra>'
        ))

    fig.update_layout(
        title='Structural Efficiency vs. Material Thickness',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Specific Load Capacity (×own weight)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_thickness_vs_efficiency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_thickness_vs_efficiency.html"


def generate_thickness_height_reduction_vs_force_graph(session):
    data = get_thickness_height_reduction_vs_force_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    fig = go.Figure()

    thickness_values = sorted(df['strand_thickness_mm'].unique())
    colors = px.colors.qualitative.Plotly

    df_no_explosion = df[df['exploded'] == False]
    df_exploded = df[df['exploded'] == True]

    for i, thickness in enumerate(thickness_values):
        color = colors[i % len(colors)]

        df_thickness_no_exp = df_no_explosion[df_no_explosion['strand_thickness_mm'] == thickness]
        if not df_thickness_no_exp.empty:
            fig.add_trace(go.Scatter(
                x=df_thickness_no_exp['force'],
                y=df_thickness_no_exp['height_reduction_pct'],
                mode='markers',
                name=f'{thickness:.1f} mm',
                marker=dict(size=8, color=color),
                legendgroup=f'{thickness}',
                hovertemplate=f'<b>{thickness:.1f} mm</b><br>Force: %{{x:.3f}} N<br>Height Reduction: %{{y:.1f}}%<extra></extra>'
            ))

        df_thickness_exp = df_exploded[df_exploded['strand_thickness_mm'] == thickness]
        if not df_thickness_exp.empty:
            fig.add_trace(go.Scatter(
                x=df_thickness_exp['force'],
                y=df_thickness_exp['height_reduction_pct'],
                mode='markers',
                name=f'{thickness:.1f} mm (exploded)',
                marker=dict(size=10, color=color, symbol='x', line=dict(width=2)),
                legendgroup=f'{thickness}',
                showlegend=False,
                hovertemplate=f'<b>{thickness:.1f} mm</b><br>Force: %{{x:.3f}} N<br>Height Reduction: %{{y:.1f}}%<br>(Exploded)<extra></extra>'
            ))

    from graphs.graph_constants import TARGET_HEIGHT_REDUCTION_PERCENT
    if not df.empty:
        fig.add_hline(
            y=TARGET_HEIGHT_REDUCTION_PERCENT,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"{TARGET_HEIGHT_REDUCTION_PERCENT:.0f}% Target",
            annotation_position="right"
        )

    fig.update_layout(
        title='Height Reduction vs. Force - All Material Thickness Configurations',
        xaxis_title='Force in Y Direction (N)',
        yaxis_title='Height Reduction (%)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        margin=dict(r=120)  # Add right margin for annotation text
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "thickness_height_reduction_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "thickness_height_reduction_vs_force.html"


def generate_strand_thickness_max_survivable_force_graph(session):
    """Graph showing maximum force survived before explosion for each thickness"""
    from database.queries.graph_queries import get_strand_thickness_max_survivable_force_data

    data = get_strand_thickness_max_survivable_force_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['strand_thickness_mm'],
        y=df['max_force_survived'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='darkblue'),
        customdata=df[['experiment_series_name', 'max_compression_pct']],
        hovertemplate='<b>%{customdata[0]}</b><br>Material Thickness: %{x:.2f} mm<br>Max Force Survived: %{y:.3f} N<br>Max Compression: %{customdata[1]:.1f}%<extra></extra>'
    ))

    # Add theoretical scaling curves
    if len(df) > 1:
        t_min, t_max = df['strand_thickness_mm'].min(), df['strand_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Use the thickest strand as reference for best fit
        t_ref = df['strand_thickness_mm'].iloc[-1]
        f_ref = df['max_force_survived'].iloc[-1]

        # Quartic scaling: F ∝ t⁴ (Euler buckling)
        f_quartic = f_ref * (t_range / t_ref) ** 4
        fig.add_trace(go.Scatter(
            x=t_range,
            y=f_quartic,
            mode='lines',
            name='Quartic (F ∝ t⁴)',
            line=dict(dash='solid', color='red', width=2),
            hovertemplate='Euler buckling theory<extra></extra>'
        ))

        # Quadratic scaling: F ∝ t²
        f_quadratic = f_ref * (t_range / t_ref) ** 2
        fig.add_trace(go.Scatter(
            x=t_range,
            y=f_quadratic,
            mode='lines',
            name='Quadratic (F ∝ t²)',
            line=dict(dash='dash', color='orange', width=2),
            hovertemplate='Quadratic scaling<extra></extra>'
        ))

        # Linear scaling: F ∝ t
        f_linear = f_ref * (t_range / t_ref)
        fig.add_trace(go.Scatter(
            x=t_range,
            y=f_linear,
            mode='lines',
            name='Linear (F ∝ t)',
            line=dict(dash='dot', color='gray', width=1),
            hovertemplate='Linear scaling<extra></extra>'
        ))

    fig.update_layout(
        title='Maximum Survivable Load vs. Material Thickness (Before Structural Failure)',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Maximum Force Survived (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_thickness_max_survivable_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_thickness_max_survivable_force.html"


def generate_layer_count_height_graph(session):

    data = get_layer_count_vs_height_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['num_layers'],
        y=df['height_m'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='blue'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Layers: %{x}<br>Height: %{y:.2f} m<extra></extra>'
    ))

    # Add theoretical linear scaling (Height ∝ num_layers)
    if len(df) > 1:
        n_min, n_max = df['num_layers'].min(), df['num_layers'].max()
        n_range = np.linspace(n_min, n_max, 100)

        # Fit linear through all data points: H = pitch × n + offset
        # Using least squares to find best fit
        slope = np.sum((df['num_layers'] - df['num_layers'].mean()) * (df['height_m'] - df['height_m'].mean())) / np.sum((df['num_layers'] - df['num_layers'].mean())**2)
        intercept = df['height_m'].mean() - slope * df['num_layers'].mean()

        h_linear = slope * n_range + intercept
        fig.add_trace(go.Scatter(
            x=n_range,
            y=h_linear,
            mode='lines',
            name=f'Linear Fit (slope={slope:.4f}m/layer)',
            line=dict(dash='dash', color='red', width=2),
            hovertemplate=f'Linear fit through data<extra></extra>'
        ))

    fig.update_layout(
        title='Height vs. Layer Count Validation',
        xaxis_title='Number of Layers',
        yaxis_title='Height (m)',
        height=500,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "layer_count_vs_height.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_count_vs_height.html"


def generate_layer_count_force_graph(session):

    data = get_layer_count_vs_force_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['num_layers'],
        y=df['force'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='darkblue'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Layers: %{x}<br>Force: %{y:.3f} N<extra></extra>'
    ))

    # Add theoretical scaling curves
    if len(df) > 1:
        n_min, n_max = df['num_layers'].min(), df['num_layers'].max()
        n_range = np.linspace(n_min, n_max, 100)

        # Normalize to first data point
        n0 = df['num_layers'].iloc[0]
        f0 = df['force'].iloc[0]

        # Linear scaling: F ∝ n (material dominates)
        f_linear = f0 * (n_range / n0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=f_linear,
            mode='lines',
            name='Linear (F ∝ n)',
            line=dict(dash='dot', color='gray', width=1),
            hovertemplate='Linear scaling<extra></extra>'
        ))

        # Square root scaling: F ∝ √n (buckling starts to dominate)
        f_sqrt = f0 * np.sqrt(n_range / n0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=f_sqrt,
            mode='lines',
            name='Sublinear (F ∝ √n)',
            line=dict(dash='dash', color='orange', width=2),
            hovertemplate='Square root scaling<extra></extra>'
        ))

        # Constant: F stays the same (buckling fully dominates)
        f_constant = np.full_like(n_range, f0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=f_constant,
            mode='lines',
            name='Constant (buckling limit)',
            line=dict(dash='dashdot', color='red', width=1),
            hovertemplate='Constant (buckling dominates)<extra></extra>'
        ))

    fig.update_layout(
        title='Load-Bearing Capacity vs. Layer Count',
        xaxis_title='Number of Layers',
        yaxis_title='Force at 10% Height Reduction (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "layer_count_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_count_vs_force.html"


def generate_layer_count_efficiency_graph(session):

    data = get_layer_count_vs_efficiency_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['num_layers'],
        y=df['specific_load_capacity'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='darkgreen'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Layers: %{x}<br>Efficiency: %{y:.2f}×<extra></extra>'
    ))

    # Add theoretical scaling curves
    if len(df) > 1:
        n_min, n_max = df['num_layers'].min(), df['num_layers'].max()
        n_range = np.linspace(n_min, n_max, 100)

        # Normalize to first data point
        n0 = df['num_layers'].iloc[0]
        e0 = df['specific_load_capacity'].iloc[0]

        # Constant efficiency (F ∝ W ∝ n)
        e_constant = np.full_like(n_range, e0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=e_constant,
            mode='lines',
            name='Constant (F ∝ n)',
            line=dict(dash='dot', color='gray', width=1),
            hovertemplate='Constant efficiency<extra></extra>'
        ))

        # Decreasing efficiency: E ∝ 1/√n (buckling starts dominating)
        e_sqrt_inv = e0 / np.sqrt(n_range / n0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=e_sqrt_inv,
            mode='lines',
            name='Decreasing (E ∝ 1/√n)',
            line=dict(dash='dash', color='orange', width=2),
            hovertemplate='Inverse square root<extra></extra>'
        ))

        # Strong decrease: E ∝ 1/n (full buckling dominance)
        e_inv = e0 / (n_range / n0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=e_inv,
            mode='lines',
            name='Strong decrease (E ∝ 1/n)',
            line=dict(dash='dashdot', color='red', width=2),
            hovertemplate='Inverse linear<extra></extra>'
        ))

    fig.update_layout(
        title='Structural Efficiency vs. Layer Count',
        xaxis_title='Number of Layers',
        yaxis_title='Specific Load Capacity (×own weight)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "layer_count_vs_efficiency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_count_vs_efficiency.html"


def generate_layer_height_reduction_vs_force_graph(session):
    data = get_layer_height_reduction_vs_force_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    layer_counts = sorted(df['num_layers'].unique())
    colors = px.colors.qualitative.Plotly

    df_no_explosion = df[df['exploded'] == False]
    df_exploded = df[df['exploded'] == True]

    for i, num_layers in enumerate(layer_counts):
        color = colors[i % len(colors)]

        df_layer_no_exp = df_no_explosion[df_no_explosion['num_layers'] == num_layers]
        if not df_layer_no_exp.empty:
            fig.add_trace(go.Scatter(
                x=df_layer_no_exp['force'],
                y=df_layer_no_exp['height_reduction_pct'],
                mode='markers',
                name=f'{num_layers} layers',
                marker=dict(size=8, color=color),
                legendgroup=f'{num_layers}',
                hovertemplate=f'<b>{num_layers} layers</b><br>Force: %{{x:.3f}} N<br>Height Reduction: %{{y:.1f}}%<extra></extra>'
            ))

        df_layer_exp = df_exploded[df_exploded['num_layers'] == num_layers]
        if not df_layer_exp.empty:
            fig.add_trace(go.Scatter(
                x=df_layer_exp['force'],
                y=df_layer_exp['height_reduction_pct'],
                mode='markers',
                name=f'{num_layers} layers (exploded)',
                marker=dict(size=10, color=color, symbol='x', line=dict(width=2)),
                legendgroup=f'{num_layers}',
                showlegend=False,
                hovertemplate=f'<b>{num_layers} layers</b><br>Force: %{{x:.3f}} N<br>Height Reduction: %{{y:.1f}}%<br>(Exploded)<extra></extra>'
            ))

    from graphs.graph_constants import TARGET_HEIGHT_REDUCTION_PERCENT
    if not df.empty:
        fig.add_hline(
            y=TARGET_HEIGHT_REDUCTION_PERCENT,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"{TARGET_HEIGHT_REDUCTION_PERCENT:.0f}% Target",
            annotation_position="right"
        )

    fig.update_layout(
        title='Height Reduction vs. Force - All Layer Configurations',
        xaxis_title='Force in Y Direction (N)',
        yaxis_title='Height Reduction (%)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        margin=dict(r=120)  # Add right margin for annotation text
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "layer_height_reduction_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_height_reduction_vs_force.html"


def generate_strand_count_weight_graph(session):
    data = get_strand_count_vs_weight_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    # Check if any series are missing weight_kg and run non-experiment for them
    for row in data:
        if row['weight_kg'] is None:
            # Lazy import to avoid circular dependency
            from experiments import run_non_experiment
            run_non_experiment(row['experiment_series_name'], will_visualize=False)

    # Refresh data after running non-experiments
    data = get_strand_count_vs_weight_chart_values(session)
    df = pd.DataFrame(data)

    # Filter out rows with None/NaN weight values
    df = df.dropna(subset=['weight_kg'])

    if df.empty:
        return None

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['num_strands'],
        y=df['weight_kg'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='green'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Strands: %{x}<br>Weight: %{y:.4f} kg<extra></extra>'
    ))

    # Add theoretical linear scaling (Weight ∝ num_strands)
    if len(df) > 1:
        n_min, n_max = df['num_strands'].min(), df['num_strands'].max()
        n_range = np.linspace(n_min, n_max, 100)

        # Fit linear with intercept: W = slope*n + intercept
        # Using least squares linear regression
        slope = np.sum((df['num_strands'] - df['num_strands'].mean()) * (df['weight_kg'] - df['weight_kg'].mean())) / np.sum((df['num_strands'] - df['num_strands'].mean())**2)
        intercept = df['weight_kg'].mean() - slope * df['num_strands'].mean()
        w_linear = slope * n_range + intercept

        fig.add_trace(go.Scatter(
            x=n_range,
            y=w_linear,
            mode='lines',
            name='Theoretical Linear (W ∝ n)',
            line=dict(dash='dash', color='red', width=2),
            hovertemplate='Expected linear scaling<extra></extra>'
        ))

    fig.update_layout(
        title='Weight Scaling with Strand Count',
        xaxis_title='Number of Strands',
        yaxis_title='Weight (kg)',
        height=500,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_count_vs_weight.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_count_vs_weight.html"


def generate_strand_count_force_graph(session):

    data = get_strand_count_vs_force_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['num_strands'],
        y=df['force'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='blue'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Strands: %{x}<br>Force: %{y:.3f} N<extra></extra>'
    ))

    # Theoretical scaling curves removed per user request

    fig.update_layout(
        title='Load-Bearing Capacity vs. Strand Count',
        xaxis_title='Number of Strands',
        yaxis_title='Force at 10% Height Reduction (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_count_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_count_vs_force.html"


def generate_strand_count_efficiency_graph(session):

    data = get_strand_count_vs_efficiency_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['num_strands'],
        y=df['specific_load_capacity'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='darkgreen'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Strands: %{x}<br>Efficiency: %{y:.2f}×<extra></extra>'
    ))

    # Theoretical scaling curves removed per user request

    fig.update_layout(
        title='Structural Efficiency vs. Strand Count',
        xaxis_title='Number of Strands',
        yaxis_title='Specific Load Capacity (×own weight)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_count_vs_efficiency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_count_vs_efficiency.html"


def generate_strand_height_reduction_vs_force_graph(session):
    data = get_strand_height_reduction_vs_force_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    strand_counts = sorted(df['num_strands'].unique())
    colors = px.colors.qualitative.Plotly

    df_no_explosion = df[df['exploded'] == False]
    df_exploded = df[df['exploded'] == True]

    for i, num_strands in enumerate(strand_counts):
        color = colors[i % len(colors)]

        df_strand_no_exp = df_no_explosion[df_no_explosion['num_strands'] == num_strands]
        if not df_strand_no_exp.empty:
            fig.add_trace(go.Scatter(
                x=df_strand_no_exp['force'],
                y=df_strand_no_exp['height_reduction_pct'],
                mode='markers',
                name=f'{num_strands} strands',
                marker=dict(size=8, color=color),
                legendgroup=f'{num_strands}',
                customdata=df_strand_no_exp['num_layers'],
                hovertemplate=f'<b>{num_strands} strands</b><br>Layers: %{{customdata}}<br>Force: %{{x:.3f}} N<br>Height Reduction: %{{y:.1f}}%<extra></extra>'
            ))

        df_strand_exp = df_exploded[df_exploded['num_strands'] == num_strands]
        if not df_strand_exp.empty:
            fig.add_trace(go.Scatter(
                x=df_strand_exp['force'],
                y=df_strand_exp['height_reduction_pct'],
                mode='markers',
                name=f'{num_strands} strands (exploded)',
                marker=dict(size=10, color=color, symbol='x', line=dict(width=2)),
                legendgroup=f'{num_strands}',
                showlegend=False,
                customdata=df_strand_exp['num_layers'],
                hovertemplate=f'<b>{num_strands} strands</b><br>Layers: %{{customdata}}<br>Force: %{{x:.3f}} N<br>Height Reduction: %{{y:.1f}}%<br>(Exploded)<extra></extra>'
            ))

    from graphs.graph_constants import TARGET_HEIGHT_REDUCTION_PERCENT
    if not df.empty:
        fig.add_hline(
            y=TARGET_HEIGHT_REDUCTION_PERCENT,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"{TARGET_HEIGHT_REDUCTION_PERCENT:.0f}% Target",
            annotation_position="right"
        )

    fig.update_layout(
        title='Height Reduction vs. Force - All Strand Configurations',
        xaxis_title='Force in Y Direction (N)',
        yaxis_title='Height Reduction (%)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        margin=dict(r=120)  # Add right margin for annotation text
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_height_reduction_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_height_reduction_vs_force.html"


def generate_recovery_by_thickness_graph(session):
    """3D scatter plot showing recovered height as a function of all three parameters"""

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Prepare data for 3D plot
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'strand_thickness_mm': row['strand_radius'] * 1000,
            'num_layers': row['num_layers'],
            'num_strands': row['num_strands'],
            'final_height': row['avg_final_height'],
            'experiment_series_name': row['experiment_series_name']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # 3D scatter with recovered height as color
    fig = go.Figure(data=[go.Scatter3d(
        x=df_normalized['strand_thickness_mm'],
        y=df_normalized['num_layers'],
        z=df_normalized['num_strands'],
        mode='markers',
        marker=dict(
            size=8,
            color=df_normalized['final_height'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Recovered Height (m)"),
            line=dict(width=0.5, color='DarkSlateGrey')
        ),
        text=df_normalized['experiment_series_name'],
        customdata=df_normalized[['final_height']],
        hovertemplate='<b>%{text}</b><br>Material Thickness: %{x:.2f} mm<br>Layers: %{y}<br>Strands: %{z}<br>Recovered Height: %{marker.color:.4f} m<extra></extra>'
    )])

    fig.update_layout(
        title='3D Recovered Height Analysis: Thickness × Layers × Strands',
        scene=dict(
            xaxis_title='Material Thickness (mm)',
            yaxis_title='Number of Layers',
            zaxis_title='Number of Strands'
        ),
        height=600,
        hovermode='closest'
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_by_thickness.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_by_thickness.html"


def generate_recovery_by_layers_graph(session):
    """Scatter plot showing recovered height vs. layers, colored by strand count"""

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Prepare data for plotting
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'num_layers': row['num_layers'],
            'num_strands': row['num_strands'],
            'strand_thickness_mm': row['strand_thickness_mm'],
            'final_height': row['avg_final_height'],
            'experiment_series_name': row['experiment_series_name']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # Create scatter plot with color by strands
    fig = px.scatter(
        df_normalized,
        x='num_layers',
        y='final_height',
        color='num_strands',
        size='strand_thickness_mm',
        hover_data=['experiment_series_name', 'strand_thickness_mm'],
        labels={
            'num_layers': 'Number of Layers',
            'final_height': 'Recovered Height (m)',
            'num_strands': 'Strands',
            'strand_thickness_mm': 'Thickness (mm)',
            'experiment_series_name': 'Experiment Series'
        },
        title='Recovered Height vs. Layers (colored by Strands, sized by Thickness)',
        color_continuous_scale='Viridis'
    )

    fig.update_traces(marker=dict(line=dict(width=0.5, color='DarkSlateGrey')))
    fig.update_layout(height=600, hovermode='closest', yaxis=dict(autorange="reversed"))
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_by_layers.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_by_layers.html"


def generate_recovery_by_strands_graph(session):
    """Scatter plot showing recovered height vs. strands, colored by layers"""
    from database.models.experiment_series_model import ExperimentSeries

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Prepare data for plotting
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'num_strands': row['num_strands'],
            'num_layers': row['num_layers'],
            'strand_thickness_mm': row['strand_thickness_mm'],
            'final_height': row['avg_final_height'],
            'experiment_series_name': row['experiment_series_name']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # Create scatter plot with color by layers
    fig = px.scatter(
        df_normalized,
        x='num_strands',
        y='final_height',
        color='num_layers',
        size='strand_thickness_mm',
        hover_data=['experiment_series_name', 'strand_thickness_mm'],
        labels={
            'num_strands': 'Number of Strands',
            'final_height': 'Recovered Height (m)',
            'num_layers': 'Layers',
            'strand_thickness_mm': 'Thickness (mm)',
            'experiment_series_name': 'Experiment Series'
        },
        title='Recovered Height vs. Strands (colored by Layers, sized by Thickness)',
        color_continuous_scale='Plasma'
    )

    fig.update_traces(marker=dict(line=dict(width=0.5, color='DarkSlateGrey')))
    fig.update_layout(height=600, hovermode='closest', yaxis=dict(autorange="reversed"))
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_by_strands.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_by_strands.html"


def generate_recovery_heatmap_thickness_layers(session):
    """Heatmap showing recovered height across thickness and layers"""

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Prepare data for heatmap
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'num_layers': row['num_layers'],
            'strand_thickness_mm': row['strand_radius'] * 1000,
            'final_height': row['avg_final_height']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # Create pivot table for heatmap
    pivot = df_normalized.pivot_table(
        values='final_height',
        index='num_layers',
        columns='strand_thickness_mm',
        aggfunc='mean'
    )

    if pivot.empty:
        return None

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Viridis',
        hovertemplate='Material Thickness: %{x:.2f} mm<br>Layers: %{y}<br>Recovered Height: %{z:.4f} m<extra></extra>',
        colorbar=dict(title="Recovered Height (m)")
    ))

    fig.update_layout(
        title='Recovered Height Heatmap: Thickness vs. Layers',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Number of Layers',
        height=600
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_heatmap_thickness_layers.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_heatmap_thickness_layers.html"


def generate_recovery_parameter_importance_graph(session):
    """Parameter importance analysis based on recovered height"""

    data = get_force_no_force_recovery_data(session)
    if not data or len(data) < 3:
        return None

    df = pd.DataFrame(data)

    # Prepare data for correlation analysis
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'num_strands': row['num_strands'],
            'num_layers': row['num_layers'],
            'final_height': row['avg_final_height']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # Calculate correlation coefficients
    correlations = {}

    if df_normalized['num_layers'].std() > 0:
        correlations['Layers'] = abs(np.corrcoef(df_normalized['num_layers'], df_normalized['final_height'])[0, 1])

    if df_normalized['num_strands'].std() > 0:
        correlations['Strands'] = abs(np.corrcoef(df_normalized['num_strands'], df_normalized['final_height'])[0, 1])

    if not correlations:
        return None

    # Sort by importance
    sorted_params = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    params, values = zip(*sorted_params)

    fig = go.Figure(data=[
        go.Bar(
            x=list(params),
            y=list(values),
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'][:len(params)],
            text=[f'{v:.3f}' for v in values],
            textposition='auto',
            hovertemplate='%{x}<br>Correlation: %{y:.3f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='Parameter Importance: Recovered Height (Linear Correlation)',
        xaxis_title='Parameter',
        yaxis_title='Absolute Correlation with Recovered Height (m)',
        yaxis=dict(range=[0, 1]),
        height=550
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_parameter_importance.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_parameter_importance.html"


def generate_recovery_heatmap_strands_layers(session):
    """Heatmap showing recovered height across strands and layers"""

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    # Prepare data for heatmap
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'num_strands': row['num_strands'],
            'num_layers': row['num_layers'],
            'final_height': row['avg_final_height']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # Create pivot table for heatmap
    pivot = df_normalized.pivot_table(
        values='final_height',
        index='num_layers',
        columns='num_strands',
        aggfunc='mean'
    )

    if pivot.empty:
        return None

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        hovertemplate='Strands: %{x}<br>Layers: %{y}<br>Recovered Height: %{z:.4f} m<extra></extra>',
        colorbar=dict(title="Recovered Height (m)")
    ))

    fig.update_layout(
        title='Recovered Height Heatmap: Strands vs. Layers',
        xaxis_title='Number of Strands',
        yaxis_title='Number of Layers',
        height=600
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_heatmap_strands_layers.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_heatmap_strands_layers.html"


def generate_recovery_heatmap_strands_thickness(session):
    """Heatmap showing recovered height across strands and thickness"""

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Prepare data for heatmap
    normalized_data = []
    for _, row in df.iterrows():
        normalized_data.append({
            'num_strands': row['num_strands'],
            'strand_thickness_mm': row['strand_radius'] * 1000,
            'final_height': row['avg_final_height']
        })

    if not normalized_data:
        return None

    df_normalized = pd.DataFrame(normalized_data)

    # Create pivot table for heatmap
    pivot = df_normalized.pivot_table(
        values='final_height',
        index='num_strands',
        columns='strand_thickness_mm',
        aggfunc='mean'
    )

    if pivot.empty:
        return None

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        hovertemplate='Material Thickness: %{x:.2f} mm<br>Strands: %{y}<br>Recovered Height: %{z:.4f} m<extra></extra>',
        colorbar=dict(title="Recovered Height (m)")
    ))

    fig.update_layout(
        title='Recovered Height Heatmap: Strands vs. Thickness',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Number of Strands',
        height=600
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_heatmap_strands_thickness.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_heatmap_strands_thickness.html"


def generate_equilibrium_time_graph(session):
    """Line plot showing equilibrium time trends across layers for each strand count"""
    data = get_force_no_force_equilibrium_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Filter to only experiments with material thickness 0.007m (7mm)
    df_filtered = df[df['strand_thickness_mm'].between(6.9, 7.1)]

    if df_filtered.empty:
        df_filtered = df  # Fall back to all data if filtering removes everything

    # Sort by strands and layers for proper line plotting
    df_filtered = df_filtered.sort_values(['num_strands', 'num_layers'])

    # Create line plot with one trace per strand count
    fig = go.Figure()

    # Color palette for different strand counts
    colors = {
        4: '#1f77b4',   # Blue
        6: '#ff7f0e',   # Orange
        8: '#2ca02c',   # Green
        10: '#d62728',  # Red
        12: '#9467bd'   # Purple
    }

    # Get unique strand counts
    strand_counts = sorted(df_filtered['num_strands'].unique())

    for strands in strand_counts:
        strand_data = df_filtered[df_filtered['num_strands'] == strands]

        # Add line with markers
        fig.add_trace(go.Scatter(
            x=strand_data['num_layers'],
            y=strand_data['avg_equilibrium_time'],
            mode='lines+markers',
            name=f'{int(strands)} strands',
            line=dict(width=2.5, color=colors.get(strands, '#000000')),
            marker=dict(size=10, symbol='circle', line=dict(width=1, color='white')),
            hovertemplate='<b>%{fullData.name}</b><br>Layers: %{x}<br>Equilibrium Time: %{y:.2f}s<extra></extra>'
        ))

    fig.update_layout(
        title='Equilibrium Time vs Layer Count (by Strand Count)',
        xaxis=dict(
            title='Number of Layers',
            tickmode='linear',
            tick0=2,
            dtick=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='Equilibrium Time (s)',
            gridcolor='lightgray'
        ),
        height=600,
        hovermode='closest',
        plot_bgcolor='white',
        legend=dict(
            title='Strand Count',
            x=0.02,
            y=0.98,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "equilibrium_time.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "equilibrium_time.html"


def generate_equilibrium_time_by_strands_graph(session):
    """Line plot showing equilibrium time trends across strands for each layer count"""
    data = get_force_no_force_equilibrium_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['strand_thickness_mm'] = df['strand_radius'] * 1000

    # Filter to only experiments with material thickness 0.007m (7mm)
    df_filtered = df[df['strand_thickness_mm'].between(6.9, 7.1)]

    if df_filtered.empty:
        df_filtered = df  # Fall back to all data if filtering removes everything

    # Sort by layers and strands for proper line plotting
    df_filtered = df_filtered.sort_values(['num_layers', 'num_strands'])

    # Create line plot with one trace per layer count
    fig = go.Figure()

    # Color palette for different layer counts
    colors = {
        2: '#e74c3c',   # Red
        3: '#3498db',   # Blue
        4: '#2ecc71'    # Green
    }

    # Get unique layer counts
    layer_counts = sorted(df_filtered['num_layers'].unique())

    for layers in layer_counts:
        layer_data = df_filtered[df_filtered['num_layers'] == layers]

        # Add line with markers
        fig.add_trace(go.Scatter(
            x=layer_data['num_strands'],
            y=layer_data['avg_equilibrium_time'],
            mode='lines+markers',
            name=f'{int(layers)} layers',
            line=dict(width=2.5, color=colors.get(layers, '#000000')),
            marker=dict(size=10, symbol='circle', line=dict(width=1, color='white')),
            hovertemplate='<b>%{fullData.name}</b><br>Strands: %{x}<br>Equilibrium Time: %{y:.2f}s<extra></extra>'
        ))

    fig.update_layout(
        title='Equilibrium Time vs Strand Count (by Layer Count)',
        xaxis=dict(
            title='Number of Strands',
            tickmode='linear',
            tick0=4,
            dtick=2,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='Equilibrium Time (s)',
            gridcolor='lightgray'
        ),
        height=600,
        hovermode='closest',
        plot_bgcolor='white',
        legend=dict(
            title='Layer Count',
            x=0.02,
            y=0.98,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "equilibrium_time_by_strands.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "equilibrium_time_by_strands.html"


def generate_compression_validation_graph(session):
    """Bar chart showing compression achieved by each configuration"""
    data = get_force_no_force_compression_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['config'] = df['num_strands'].astype(str) + 's, ' + df['num_layers'].astype(str) + 'l'
    df = df.sort_values(['num_strands', 'num_layers'])

    fig = go.Figure()

    # Add optimal compression bars (maximum compression from all experiments)
    fig.add_trace(go.Bar(
        x=df['config'],
        y=df['max_compression_pct'],
        name='Optimal Compression Performance',
        marker_color=df['num_strands'],
        marker=dict(
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Strand Count")
        ),
        text=[f"{val:.1f}%" for val in df['max_compression_pct']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Optimal Compression: %{y:.1f}%<br>Target Force: %{customdata:.1f}N<extra></extra>',
        customdata=df['target_force']
    ))

    fig.update_layout(
        title='Best Performing Compression',
        xaxis_title='Configuration (Strands, Layers)',
        yaxis_title='Compression (%)',
        height=600,
        showlegend=False,
        xaxis={'tickangle': -45}
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "compression_validation.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "compression_validation.html"


def generate_stiffness_comparison_graph(session):
    """Heatmap showing effective stiffness across configurations"""
    data = get_force_no_force_stiffness_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    # Create pivot table for heatmap
    pivot = df.pivot_table(
        values='avg_stiffness',
        index='num_layers',
        columns='num_strands',
        aggfunc='mean'
    )

    if pivot.empty:
        return None

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='YlOrRd',
        hovertemplate='Strands: %{x}<br>Layers: %{y}<br>Stiffness: %{z:.1f} N/m<extra></extra>',
        colorbar=dict(title="Stiffness (N/m)")
    ))

    fig.update_layout(
        title='Effective Stiffness Comparison (k = F/Δx)',
        xaxis_title='Number of Strands',
        yaxis_title='Number of Layers',
        height=600
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "stiffness_comparison.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "stiffness_comparison.html"


def generate_recovery_consistency_graph(session):
    """Box plot showing recovery consistency across configurations"""
    data = get_force_no_force_recovery_consistency_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['config'] = df['num_strands'].astype(str) + 's, ' + df['num_layers'].astype(str) + 'l'
    df = df.sort_values(['num_strands', 'num_layers'])

    fig = go.Figure()

    # Create error bars showing variability
    fig.add_trace(go.Bar(
        x=df['config'],
        y=df['avg_recovery'],
        name='Average Recovered Height',
        marker_color=df['num_strands'],
        marker=dict(
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Strand Count")
        ),
        error_y=dict(
            type='data',
            array=df['std_recovery'],
            visible=True,
            color='rgba(0,0,0,0.3)',
            thickness=1.5,
            width=4
        ),
        text=[f"{avg:.4f}±{std:.4f}m" for avg, std in zip(df['avg_recovery'], df['std_recovery'])],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Recovered Height: %{y:.4f} m<br>Std Dev: %{customdata:.4f} m<br>Range: %{text}<extra></extra>',
        customdata=df['std_recovery']
    ))

    fig.update_layout(
        title='Recovered Height Consistency: Average ± Standard Deviation',
        xaxis_title='Configuration (Strands, Layers)',
        yaxis_title='Recovered Height (m)',
        height=600,
        showlegend=False,
        xaxis={'tickangle': -45}
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "recovery_consistency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_consistency.html"


def generate_strand_stiffness_vs_compression_graph(session):
    """Stiffness vs. compression percentage for different strand counts"""
    data = get_strand_count_stiffness_vs_compression_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    strand_counts = sorted(df['num_strands'].unique())
    colors = px.colors.qualitative.Plotly

    for i, num_strands in enumerate(strand_counts):
        color = colors[i % len(colors)]
        df_strand = df[df['num_strands'] == num_strands]

        fig.add_trace(go.Scatter(
            x=df_strand['compression_pct'],
            y=df_strand['stiffness'],
            mode='lines+markers',
            name=f'{num_strands} strands',
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>{num_strands} strands</b><br>Compression: %{{x:.1f}}%<br>Stiffness: %{{y:.1f}} N/m<extra></extra>'
        ))

    fig.update_layout(
        title='Apparent Stiffness vs. Compression (Non-Linear Spring Behavior)',
        xaxis_title='Compression (%)',
        yaxis_title='Apparent Stiffness k (N/m)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_stiffness_vs_compression.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_stiffness_vs_compression.html"


def generate_strand_force_vs_displacement_graph(session):
    """Force vs. displacement for different strand counts with linear spring comparison"""
    data = get_strand_count_force_vs_displacement_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    strand_counts = sorted(df['num_strands'].unique())
    colors = px.colors.qualitative.Plotly

    # Plot experimental data for each strand count
    for i, num_strands in enumerate(strand_counts):
        color = colors[i % len(colors)]
        df_strand = df[df['num_strands'] == num_strands]

        fig.add_trace(go.Scatter(
            x=df_strand['displacement'] * 1000,  # Convert to mm
            y=df_strand['force'],
            mode='lines+markers',
            name=f'{num_strands} strands',
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>{num_strands} strands</b><br>Displacement: %{{x:.2f}} mm<br>Force: %{{y:.3f}} N<extra></extra>'
        ))

    # Add linear spring reference lines for comparison
    for i, num_strands in enumerate(strand_counts):
        color = colors[i % len(colors)]
        df_strand = df[df['num_strands'] == num_strands].copy()

        if len(df_strand) < 2:
            continue

        # Calculate initial stiffness from first few points (linear approximation)
        df_early = df_strand.nsmallest(5, 'displacement')
        if len(df_early) >= 2:
            # Linear fit: k = F/x (average of early data points)
            k_initial = (df_early['force'] / df_early['displacement']).mean()

            # Create linear spring line
            max_displacement = df_strand['displacement'].max()
            x_linear = np.linspace(0, max_displacement, 50)
            y_linear = k_initial * x_linear

            fig.add_trace(go.Scatter(
                x=x_linear * 1000,  # Convert to mm
                y=y_linear,
                mode='lines',
                name=f'{num_strands} strands (linear)',
                line=dict(color=color, width=1, dash='dash'),
                opacity=0.5,
                showlegend=False,
                hovertemplate=f'<b>{num_strands} strands (linear spring)</b><br>Displacement: %{{x:.2f}} mm<br>Force: %{{y:.3f}} N<br>k={k_initial:.1f} N/m<extra></extra>'
            ))

    fig.update_layout(
        title='Force vs. Displacement (Solid: Experimental, Dashed: Linear Spring)',
        xaxis_title='Displacement Δx (mm)',
        yaxis_title='Force F (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "strand_force_vs_displacement.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_force_vs_displacement.html"


def generate_load_bearing_parameter_importance_graph(session):
    """Parameter importance analysis for load-bearing capability"""
    data = get_load_bearing_parameter_importance_data(session)
    if not data or len(data) < 3:
        return None

    df = pd.DataFrame(data)

    # Calculate correlation coefficients for load capacity
    correlations = {}

    if 'num_layers' in df.columns and df['num_layers'].std() > 0:
        correlations['Layers'] = abs(np.corrcoef(df['num_layers'], df['specific_load_capacity'])[0, 1])

    if 'num_strands' in df.columns and df['num_strands'].std() > 0:
        correlations['Strands'] = abs(np.corrcoef(df['num_strands'], df['specific_load_capacity'])[0, 1])

    if not correlations:
        return None

    # Sort by importance
    sorted_params = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    params, values = zip(*sorted_params)

    fig = go.Figure(data=[
        go.Bar(
            x=list(params),
            y=list(values),
            marker_color=['#d62728', '#ff7f0e'][:len(params)],
            text=[f'{v:.3f}' for v in values],
            textposition='auto',
            hovertemplate='%{x}<br>Correlation: %{y:.3f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='Parameter Importance: Load-Bearing Capability (Linear Correlation)',
        xaxis_title='Parameter',
        yaxis_title='Absolute Correlation with Specific Load Capacity',
        yaxis=dict(range=[0, 1]),
        height=550
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "load_bearing_parameter_importance.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "load_bearing_parameter_importance.html"


def generate_compression_parameter_importance_graph(session):
    """Parameter importance analysis for compression performance"""
    data = get_force_no_force_compression_data(session)
    if not data or len(data) < 3:
        return None

    df = pd.DataFrame(data)

    # Calculate correlation coefficients for compression percentage
    correlations = {}

    if 'num_layers' in df.columns and df['num_layers'].std() > 0:
        correlations['Layers'] = abs(np.corrcoef(df['num_layers'], df['max_compression_pct'])[0, 1])

    if 'num_strands' in df.columns and df['num_strands'].std() > 0:
        correlations['Strands'] = abs(np.corrcoef(df['num_strands'], df['max_compression_pct'])[0, 1])

    if not correlations:
        return None

    # Sort by importance
    sorted_params = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    params, values = zip(*sorted_params)

    fig = go.Figure(data=[
        go.Bar(
            x=list(params),
            y=list(values),
            marker_color=['#d62728', '#ff7f0e'][:len(params)],
            text=[f'{v:.3f}' for v in values],
            textposition='auto',
            hovertemplate='%{x}<br>Correlation: %{y:.3f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='Parameter Importance: Compression Performance (Linear Correlation)',
        xaxis_title='Parameter',
        yaxis_title='Absolute Correlation with Compression Percentage',
        yaxis=dict(range=[0, 1]),
        height=550
    )
    apply_latex_font_theme(fig)

    output_path = GRAPHS_DIR / "compression_parameter_importance.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "compression_parameter_importance.html"


# Mapping of group_name to their aggregate graph functions
GROUP_AGGREGATE_GRAPHS = {
    'strand_thickness': [
        generate_strand_thickness_weight_graph,
        generate_strand_thickness_force_graph,
        generate_strand_thickness_efficiency_graph,
        generate_thickness_height_reduction_vs_force_graph,
        generate_strand_thickness_max_survivable_force_graph,
        generate_strand_stiffness_vs_compression_graph,
        generate_strand_force_vs_displacement_graph,
    ],
    'number_of_layers': [
        generate_layer_count_height_graph,
        generate_layer_count_force_graph,
        generate_layer_count_efficiency_graph,
        generate_layer_height_reduction_vs_force_graph,
    ],
    'number_of_strands': [
        generate_strand_count_weight_graph,
        generate_strand_count_force_graph,
        generate_strand_count_efficiency_graph,
        generate_strand_height_reduction_vs_force_graph,
    ],
    'force_no_force': [
        generate_recovery_by_thickness_graph,
        generate_recovery_by_layers_graph,
        generate_recovery_by_strands_graph,
        generate_recovery_heatmap_thickness_layers,
        generate_recovery_heatmap_strands_layers,
        generate_recovery_heatmap_strands_thickness,
        generate_recovery_parameter_importance_graph,
        generate_equilibrium_time_graph,
        generate_equilibrium_time_by_strands_graph,
        generate_compression_validation_graph,
        generate_stiffness_comparison_graph,
        generate_recovery_consistency_graph,
        generate_load_bearing_parameter_importance_graph,
        generate_compression_parameter_importance_graph,
    ]
}

# Graphs that aggregate across all experiments regardless of group
ALL_EXPERIMENTS_GRAPHS = [
    generate_load_capacity_ratio_graph,
]


def generate_aggregate_graphs_for_group(session, group_name):
    """Generate aggregate graphs for a specific group_name"""
    graphs = GROUP_AGGREGATE_GRAPHS.get(group_name, [])

    if not graphs:
        # If no specific group match, generate all-experiments graphs
        print(f"  No specific aggregate graphs for group '{group_name}', generating all-experiments graphs...")
        for graph_func in ALL_EXPERIMENTS_GRAPHS:
            try:
                print(f"    - {graph_func.__name__}...")
                graph_func(session)
            except Exception as e:
                print(f"      Error generating {graph_func.__name__}: {e}")
        return

    print(f"  Generating aggregate graphs for group '{group_name}'...")
    for graph_func in graphs:
        try:
            print(f"    - {graph_func.__name__}...")
            graph_func(session)
        except Exception as e:
            print(f"      Error generating {graph_func.__name__}: {e}")
