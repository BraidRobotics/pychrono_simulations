import plotly.express as px
from pathlib import Path
import pandas as pd

from database.queries.graph_queries import (
    get_material_thickness_vs_weight_chart_values,
    get_material_thickness_vs_force_chart_values,
    get_load_capacity_ratio_y_chart_values,
    get_material_thickness_vs_efficiency_chart_values,
    get_layer_count_vs_height_chart_values,
    get_layer_count_vs_force_chart_values,
    get_layer_count_vs_efficiency_chart_values,
    get_strand_count_vs_weight_chart_values,
    get_strand_count_vs_force_chart_values,
    get_strand_count_vs_efficiency_chart_values,
    get_force_no_force_recovery_data
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
            'specific_load_capacity': 'Specific Load Capacity (×own weight)',
            'experiment_series_name': 'Experiment Series',
            'force': 'Force (N)'
        },
        title='Structural Efficiency: Specific Load Capacity vs Weight',
        trendline='ols',
        trendline_color_override='red'
    )

    fig.update_traces(marker=dict(size=10))

    _add_r_squared_annotation(fig)

    fig.update_layout(height=500, hovermode='closest')

    output_path = GRAPHS_DIR / f"load_capacity_ratio_{force_direction}.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return f"load_capacity_ratio_{force_direction}.html"


def generate_material_thickness_weight_graph(session):
    import numpy as np
    import plotly.graph_objects as go

    data = get_material_thickness_vs_weight_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['material_thickness_mm'],
        y=df['weight_kg'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='green'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Thickness: %{x:.2f} mm<br>Weight: %{y:.4f} kg<extra></extra>'
    ))

    # Add theoretical linear scaling (Weight ∝ thickness)
    if len(df) > 1:
        t_min, t_max = df['material_thickness_mm'].min(), df['material_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Normalize to first data point
        t0 = df['material_thickness_mm'].iloc[0]
        w0 = df['weight_kg'].iloc[0]

        # Linear scaling: W ∝ t (expected from W = ρ × V ∝ t)
        w_linear = w0 * (t_range / t0)
        fig.add_trace(go.Scatter(
            x=t_range,
            y=w_linear,
            mode='lines',
            name='Theoretical Linear (W ∝ t)',
            line=dict(dash='dash', color='red', width=2),
            hovertemplate='Expected linear scaling<extra></extra>'
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

    output_path = GRAPHS_DIR / "material_thickness_vs_weight.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "material_thickness_vs_weight.html"


def generate_material_thickness_force_graph(session):
    import numpy as np
    import plotly.graph_objects as go

    data = get_material_thickness_vs_force_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['material_thickness_mm'],
        y=df['force'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='blue'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Thickness: %{x:.2f} mm<br>Force: %{y:.3f} N<extra></extra>'
    ))

    # Add theoretical scaling curves
    if len(df) > 1:
        t_min, t_max = df['material_thickness_mm'].min(), df['material_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Normalize to first data point for comparison
        t0 = df['material_thickness_mm'].iloc[0]
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
        title='Force Capacity vs Material Thickness (with Theoretical Scaling)',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Force at 10% Height Reduction (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    output_path = GRAPHS_DIR / "material_thickness_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "material_thickness_vs_force.html"


def generate_material_thickness_efficiency_graph(session):
    import numpy as np
    import plotly.graph_objects as go

    data = get_material_thickness_vs_efficiency_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    fig = go.Figure()

    # Add actual data points
    fig.add_trace(go.Scatter(
        x=df['material_thickness_mm'],
        y=df['specific_load_capacity'],
        mode='markers',
        name='Experimental Data',
        marker=dict(size=10, color='darkgreen'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Thickness: %{x:.2f} mm<br>Efficiency: %{y:.2f}×<extra></extra>'
    ))

    # Add theoretical cubic scaling (Efficiency ∝ t³)
    # If F ∝ t⁴ and W ∝ t, then F/W ∝ t³
    if len(df) > 1:
        t_min, t_max = df['material_thickness_mm'].min(), df['material_thickness_mm'].max()
        t_range = np.linspace(t_min, t_max, 100)

        # Normalize to first data point
        t0 = df['material_thickness_mm'].iloc[0]
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
        title='Structural Efficiency vs Material Thickness',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Specific Load Capacity (×own weight)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    output_path = GRAPHS_DIR / "material_thickness_vs_efficiency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "material_thickness_vs_efficiency.html"


def generate_layer_count_height_graph(session):
    import numpy as np
    import plotly.graph_objects as go

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

        # Calculate pitch from first data point
        n0 = df['num_layers'].iloc[0]
        h0 = df['height_m'].iloc[0]
        pitch = h0 / n0

        # Linear scaling: H = pitch × n
        h_linear = pitch * n_range
        fig.add_trace(go.Scatter(
            x=n_range,
            y=h_linear,
            mode='lines',
            name=f'Theoretical Linear (pitch={pitch:.3f}m)',
            line=dict(dash='dash', color='red', width=2),
            hovertemplate=f'Expected: pitch × layers<extra></extra>'
        ))

    fig.update_layout(
        title='Height vs Layer Count Validation',
        xaxis_title='Number of Layers',
        yaxis_title='Height (m)',
        height=500,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    output_path = GRAPHS_DIR / "layer_count_vs_height.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_count_vs_height.html"


def generate_layer_count_force_graph(session):
    import numpy as np
    import plotly.graph_objects as go

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
        title='Force Capacity vs Layer Count',
        xaxis_title='Number of Layers',
        yaxis_title='Force at 10% Height Reduction (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    output_path = GRAPHS_DIR / "layer_count_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_count_vs_force.html"


def generate_layer_count_efficiency_graph(session):
    import numpy as np
    import plotly.graph_objects as go

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
        title='Structural Efficiency vs Layer Count',
        xaxis_title='Number of Layers',
        yaxis_title='Specific Load Capacity (×own weight)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )

    output_path = GRAPHS_DIR / "layer_count_vs_efficiency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "layer_count_vs_efficiency.html"


def generate_strand_count_weight_graph(session):
    import numpy as np
    import plotly.graph_objects as go

    data = get_strand_count_vs_weight_chart_values(session)
    if not data:
        return None

    df = pd.DataFrame(data)

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

        # Normalize to first data point
        n0 = df['num_strands'].iloc[0]
        w0 = df['weight_kg'].iloc[0]

        # Linear scaling: W ∝ n (expected from W = ρ × V ∝ n)
        w_linear = w0 * (n_range / n0)
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

    output_path = GRAPHS_DIR / "strand_count_vs_weight.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_count_vs_weight.html"


def generate_strand_count_force_graph(session):
    import numpy as np
    import plotly.graph_objects as go

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

    # Add theoretical scaling curves
    if len(df) > 1:
        n_min, n_max = df['num_strands'].min(), df['num_strands'].max()
        n_range = np.linspace(n_min, n_max, 100)

        # Normalize to first data point
        n0 = df['num_strands'].iloc[0]
        f0 = df['force'].iloc[0]

        # Linear scaling: F ∝ n (material quantity dominates)
        f_linear = f0 * (n_range / n0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=f_linear,
            mode='lines',
            name='Linear (F ∝ n)',
            line=dict(dash='dot', color='gray', width=1),
            hovertemplate='Linear scaling<extra></extra>'
        ))

        # Quadratic scaling: F ∝ n² (structural stiffness dominates)
        f_quadratic = f0 * (n_range / n0) ** 2
        fig.add_trace(go.Scatter(
            x=n_range,
            y=f_quadratic,
            mode='lines',
            name='Quadratic (F ∝ n²)',
            line=dict(dash='dash', color='orange', width=2),
            hovertemplate='Quadratic scaling<extra></extra>'
        ))

    fig.update_layout(
        title='Force Capacity vs Strand Count',
        xaxis_title='Number of Strands',
        yaxis_title='Force at 10% Height Reduction (N)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    output_path = GRAPHS_DIR / "strand_count_vs_force.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_count_vs_force.html"


def generate_strand_count_efficiency_graph(session):
    import numpy as np
    import plotly.graph_objects as go

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

    # Add theoretical scaling curves
    if len(df) > 1:
        n_min, n_max = df['num_strands'].min(), df['num_strands'].max()
        n_range = np.linspace(n_min, n_max, 100)

        # Normalize to first data point
        n0 = df['num_strands'].iloc[0]
        e0 = df['specific_load_capacity'].iloc[0]

        # Constant efficiency (F ∝ W ∝ n)
        e_constant = np.full_like(n_range, e0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=e_constant,
            mode='lines',
            name='Constant (E ∝ n⁰)',
            line=dict(dash='dot', color='gray', width=1),
            hovertemplate='Constant efficiency<extra></extra>'
        ))

        # Linear efficiency: E ∝ n (if F ∝ n², W ∝ n)
        e_linear = e0 * (n_range / n0)
        fig.add_trace(go.Scatter(
            x=n_range,
            y=e_linear,
            mode='lines',
            name='Linear (E ∝ n)',
            line=dict(dash='dash', color='purple', width=2),
            hovertemplate='Linear scaling<extra></extra>'
        ))

    fig.update_layout(
        title='Structural Efficiency vs Strand Count',
        xaxis_title='Number of Strands',
        yaxis_title='Specific Load Capacity (×own weight)',
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    output_path = GRAPHS_DIR / "strand_count_vs_efficiency.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "strand_count_vs_efficiency.html"


def generate_recovery_by_thickness_graph(session):
    import plotly.graph_objects as go

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['material_thickness_mm'],
        y=df['recovery_percent'],
        mode='markers',
        marker=dict(size=10, color='blue'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Thickness: %{x:.2f} mm<br>Recovery: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Elastic Recovery vs Material Thickness',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Recovery (%)',
        height=550,
        hovermode='closest'
    )

    output_path = GRAPHS_DIR / "recovery_by_thickness.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_by_thickness.html"


def generate_recovery_by_layers_graph(session):
    import plotly.graph_objects as go

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['num_layers'],
        y=df['recovery_percent'],
        mode='markers',
        marker=dict(size=10, color='green'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Layers: %{x}<br>Recovery: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Elastic Recovery vs Layer Count',
        xaxis_title='Number of Layers',
        yaxis_title='Recovery (%)',
        height=550,
        hovermode='closest'
    )

    output_path = GRAPHS_DIR / "recovery_by_layers.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_by_layers.html"


def generate_recovery_by_strands_graph(session):
    import plotly.graph_objects as go

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['num_strands'],
        y=df['recovery_percent'],
        mode='markers',
        marker=dict(size=10, color='orange'),
        customdata=df['experiment_series_name'],
        hovertemplate='<b>%{customdata}</b><br>Strands: %{x}<br>Recovery: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Elastic Recovery vs Strand Count',
        xaxis_title='Number of Strands',
        yaxis_title='Recovery (%)',
        height=550,
        hovermode='closest'
    )

    output_path = GRAPHS_DIR / "recovery_by_strands.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_by_strands.html"


def generate_recovery_heatmap_thickness_layers(session):
    import plotly.graph_objects as go
    import numpy as np

    data = get_force_no_force_recovery_data(session)
    if not data:
        return None

    df = pd.DataFrame(data)
    df['material_thickness_mm'] = df['material_thickness'] * 1000

    # Create pivot table for heatmap
    pivot = df.pivot_table(
        values='recovery_percent',
        index='num_layers',
        columns='material_thickness_mm',
        aggfunc='mean'
    )

    if pivot.empty:
        return None

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Viridis',
        hovertemplate='Thickness: %{x:.2f} mm<br>Layers: %{y}<br>Recovery: %{z:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Recovery Heatmap: Thickness vs Layers',
        xaxis_title='Material Thickness (mm)',
        yaxis_title='Number of Layers',
        height=600
    )

    output_path = GRAPHS_DIR / "recovery_heatmap_thickness_layers.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_heatmap_thickness_layers.html"


def generate_recovery_parameter_importance_graph(session):
    import plotly.graph_objects as go
    import numpy as np

    data = get_force_no_force_recovery_data(session)
    if not data or len(data) < 3:
        return None

    df = pd.DataFrame(data)

    # Calculate correlation coefficients
    correlations = {}

    if df['material_thickness'].std() > 0:
        correlations['Thickness'] = abs(np.corrcoef(df['material_thickness'], df['recovery_percent'])[0, 1])

    if df['num_layers'].std() > 0:
        correlations['Layers'] = abs(np.corrcoef(df['num_layers'], df['recovery_percent'])[0, 1])

    if df['num_strands'].std() > 0:
        correlations['Strands'] = abs(np.corrcoef(df['num_strands'], df['recovery_percent'])[0, 1])

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
            hovertemplate='%{x}<br>Correlation: %{y:.3f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='Parameter Importance for Elastic Recovery',
        xaxis_title='Parameter',
        yaxis_title='Absolute Correlation with Recovery',
        yaxis=dict(range=[0, 1]),
        height=550
    )

    output_path = GRAPHS_DIR / "recovery_parameter_importance.html"
    fig.write_html(str(output_path), include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    return "recovery_parameter_importance.html"
