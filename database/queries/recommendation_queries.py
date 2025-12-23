"""
Queries for generating design recommendations based on experiment results.
"""
from sqlalchemy.orm import Session
from collections import defaultdict
import numpy as np

from database.models.experiment_series_model import ExperimentSeries
from database.models.experiment_model import Experiment
from database.queries.graph_queries import (
    get_force_no_force_recovery_data,
    get_force_no_force_compression_data,
    get_load_bearing_parameter_importance_data,
    get_strand_radius_vs_efficiency_chart_values,
    get_layer_count_vs_efficiency_chart_values,
    get_strand_count_vs_efficiency_chart_values,
    get_strand_radius_vs_force_chart_values,
    get_layer_count_vs_force_chart_values,
    get_strand_count_vs_force_chart_values
)


def get_design_recommendations(session: Session):
    """
    Generate design recommendations based on different objectives.

    Returns a dict with four recommendation categories:
    - flexibility: Best configurations for compression percentage
    - recovery: Best configurations for elastic recovery
    - high_load_bearing: Best configurations for maximum force capacity
    - best_efficiency: Best configurations for weight-to-payload ratio
    """

    # Get all relevant data
    recovery_data = get_force_no_force_recovery_data(session)
    compression_data = get_force_no_force_compression_data(session)
    load_bearing_data = get_load_bearing_parameter_importance_data(session)

    # Get efficiency data from different experiment series
    thickness_efficiency = get_strand_radius_vs_efficiency_chart_values(session)
    layer_efficiency = get_layer_count_vs_efficiency_chart_values(session)
    strand_efficiency = get_strand_count_vs_efficiency_chart_values(session)

    # Get force data
    thickness_force = get_strand_radius_vs_force_chart_values(session)
    layer_force = get_layer_count_vs_force_chart_values(session)
    strand_force = get_strand_count_vs_force_chart_values(session)

    recommendations = {
        'flexibility': _get_compression_recommendations(session, compression_data),
        'recovery': _get_recovery_recommendations(session, recovery_data),
        'high_load_bearing': _get_load_bearing_recommendations(session, load_bearing_data,
                                                               thickness_force, layer_force, strand_force),
        'best_efficiency': _get_efficiency_recommendations(session, thickness_efficiency,
                                                           layer_efficiency, strand_efficiency)
    }

    return recommendations


def _get_compression_recommendations(session: Session, compression_data):
    """Get top configurations for flexibility (compression percentage)"""
    if not compression_data:
        return {
            'parameter': 'Flexibility (Compression)',
            'metric': 'Maximum Compression Percentage',
            'top_configs': [],
            'general_guidance': 'No data available'
        }

    # Sort by maximum compression percentage
    sorted_data = sorted(compression_data, key=lambda x: x['max_compression_pct'], reverse=True)

    # Get top 5 configurations
    top_configs = []
    for config in sorted_data[:5]:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=config['experiment_series_name']
        ).first()

        top_configs.append({
            'strands': config['num_strands'],
            'layers': config['num_layers'],
            'material_thickness_mm': series.strand_radius * 1000 if series and series.strand_radius else None,
            'value': config['max_compression_pct'],
            'weight_kg': series.weight_kg if series else None,
            'series_name': config['experiment_series_name']
        })

    # Analyze patterns
    avg_compression = np.mean([c['max_compression_pct'] for c in compression_data])

    # Determine optimal parameters
    strands_list = [c['num_strands'] for c in sorted_data[:10]]
    layers_list = [c['num_layers'] for c in sorted_data[:10]]

    most_common_strands = max(set(strands_list), key=strands_list.count) if strands_list else None
    most_common_layers = max(set(layers_list), key=layers_list.count) if layers_list else None

    guidance = f"For maximum compression flexibility, aim for {most_common_strands} strands and {most_common_layers} layers. "
    guidance += f"Average max compression across all configs: {avg_compression:.1f}%"

    return {
        'parameter': 'Flexibility (Compression)',
        'metric': 'Maximum Compression Percentage (%)',
        'top_configs': top_configs,
        'general_guidance': guidance,
        'optimal_strands': most_common_strands,
        'optimal_layers': most_common_layers
    }


def _get_recovery_recommendations(session: Session, recovery_data):
    """Get top configurations for elastic recovery (normalized by applied force)"""
    if not recovery_data:
        return {
            'parameter': 'Elastic Recovery',
            'metric': 'Normalized Recovery Efficiency',
            'top_configs': [],
            'general_guidance': 'No data available'
        }

    # Enrich recovery data with force information and calculate normalized metric
    enriched_data = []
    for config in recovery_data:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=config['experiment_series_name']
        ).first()

        if series and series.final_force_in_y_direction:
            applied_force = abs(series.final_force_in_y_direction)
            # Normalized recovery efficiency: recovery % per Newton of applied force
            # Higher is better - means more recovery per unit force applied
            normalized_efficiency = config['recovery_percent'] / applied_force if applied_force > 0 else 0

            enriched_data.append({
                'experiment_series_name': config['experiment_series_name'],
                'num_strands': config['num_strands'],
                'num_layers': config['num_layers'],
                'strand_radius': config['strand_radius'],
                'recovery_percent': config['recovery_percent'],
                'weight_kg': config['weight_kg'],
                'applied_force': applied_force,
                'normalized_efficiency': normalized_efficiency
            })

    if not enriched_data:
        return {
            'parameter': 'Elastic Recovery',
            'metric': 'Normalized Recovery Efficiency',
            'top_configs': [],
            'general_guidance': 'No force data available for normalization'
        }

    # Sort by normalized efficiency (recovery per Newton)
    sorted_data = sorted(enriched_data, key=lambda x: x['normalized_efficiency'], reverse=True)

    # Get top 5 configurations
    top_configs = []
    for config in sorted_data[:5]:
        top_configs.append({
            'strands': config['num_strands'],
            'layers': config['num_layers'],
            'material_thickness_mm': config['strand_radius'] * 1000,
            'value': config['normalized_efficiency'],
            'recovery_percent': config['recovery_percent'],
            'applied_force': config['applied_force'],
            'weight_kg': config['weight_kg'],
            'series_name': config['experiment_series_name']
        })

    # Analyze patterns
    avg_normalized = np.mean([c['normalized_efficiency'] for c in enriched_data])
    avg_recovery = np.mean([c['recovery_percent'] for c in enriched_data])

    # Determine optimal parameters based on normalized efficiency
    strands_list = [c['num_strands'] for c in sorted_data[:10]]
    layers_list = [c['num_layers'] for c in sorted_data[:10]]

    most_common_strands = max(set(strands_list), key=strands_list.count) if strands_list else None
    most_common_layers = max(set(layers_list), key=layers_list.count) if layers_list else None

    guidance = f"For best elastic recovery efficiency (normalized by force), aim for {most_common_strands} strands and {most_common_layers} layers. "
    guidance += f"Average normalized efficiency: {avg_normalized:.2f}% per Newton. Average raw recovery: {avg_recovery:.1f}%"

    return {
        'parameter': 'Elastic Recovery',
        'metric': 'Normalized Recovery Efficiency (% per Newton)',
        'top_configs': top_configs,
        'general_guidance': guidance,
        'optimal_strands': most_common_strands,
        'optimal_layers': most_common_layers
    }


def _get_load_bearing_recommendations(session: Session, load_bearing_data, thickness_force, layer_force, strand_force):
    """Get top configurations for load-bearing capability"""

    # Combine all force data
    all_force_data = []

    # Add thickness data
    for item in thickness_force:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=item['experiment_series_name']
        ).first()
        if series:
            all_force_data.append({
                'series_name': item['experiment_series_name'],
                'force': item['force'],
                'strands': series.num_strands,
                'layers': series.num_layers,
                'material_thickness_mm': series.strand_radius * 1000 if series.strand_radius else None,
                'weight_kg': series.weight_kg
            })

    # Add layer data
    for item in layer_force:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=item['experiment_series_name']
        ).first()
        if series:
            all_force_data.append({
                'series_name': item['experiment_series_name'],
                'force': item['force'],
                'strands': series.num_strands,
                'layers': item['num_layers'],
                'material_thickness_mm': series.strand_radius * 1000 if series.strand_radius else None,
                'weight_kg': series.weight_kg
            })

    # Add strand data
    for item in strand_force:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=item['experiment_series_name']
        ).first()
        if series:
            all_force_data.append({
                'series_name': item['experiment_series_name'],
                'force': item['force'],
                'strands': item['num_strands'],
                'layers': series.num_layers,
                'material_thickness_mm': series.strand_radius * 1000 if series.strand_radius else None,
                'weight_kg': series.weight_kg
            })

    # Sort by force
    sorted_data = sorted(all_force_data, key=lambda x: x['force'], reverse=True)

    # Get top 5 unique configurations
    top_configs = []
    seen = set()
    for config in sorted_data:
        key = (config['strands'], config['layers'], config.get('material_thickness_mm'))
        if key not in seen and len(top_configs) < 5:
            top_configs.append({
                'strands': config['strands'],
                'layers': config['layers'],
                'material_thickness_mm': config.get('material_thickness_mm'),
                'value': config['force'],
                'weight_kg': config['weight_kg'],
                'series_name': config['series_name']
            })
            seen.add(key)

    # Analyze patterns
    if all_force_data:
        avg_force = np.mean([c['force'] for c in all_force_data])

        # Find optimal parameters from top performers
        strands_list = [c['strands'] for c in sorted_data[:10]]
        layers_list = [c['layers'] for c in sorted_data[:10]]

        max_strands = max(strands_list) if strands_list else None
        max_layers = max(layers_list) if layers_list else None

        guidance = f"For maximum load-bearing, use thicker materials ({max([c.get('material_thickness_mm', 0) for c in sorted_data[:5]]):.1f}mm), "
        guidance += f"more strands (~{max_strands}), and more layers (~{max_layers}). "
        guidance += f"Average force capacity: {avg_force:.2f}N"
    else:
        guidance = "No data available"
        max_strands = None
        max_layers = None

    return {
        'parameter': 'Load-Bearing Capability',
        'metric': 'Force at 10% Height Reduction (N)',
        'top_configs': top_configs,
        'general_guidance': guidance,
        'optimal_strands': max_strands,
        'optimal_layers': max_layers
    }


def _get_efficiency_recommendations(session: Session, thickness_efficiency, layer_efficiency, strand_efficiency):
    """Get top configurations for weight-to-payload ratio (structural efficiency)"""

    # Combine all efficiency data
    all_efficiency_data = []

    # Add thickness data
    for item in thickness_efficiency:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=item['experiment_series_name']
        ).first()
        if series:
            all_efficiency_data.append({
                'series_name': item['experiment_series_name'],
                'efficiency': item['specific_load_capacity'],
                'strands': series.num_strands,
                'layers': series.num_layers,
                'material_thickness_mm': item['strand_radius'] * 1000,
                'weight_kg': series.weight_kg
            })

    # Add layer data
    for item in layer_efficiency:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=item['experiment_series_name']
        ).first()
        if series:
            all_efficiency_data.append({
                'series_name': item['experiment_series_name'],
                'efficiency': item['specific_load_capacity'],
                'strands': series.num_strands,
                'layers': item['num_layers'],
                'material_thickness_mm': series.strand_radius * 1000 if series.strand_radius else None,
                'weight_kg': series.weight_kg
            })

    # Add strand data
    for item in strand_efficiency:
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=item['experiment_series_name']
        ).first()
        if series:
            all_efficiency_data.append({
                'series_name': item['experiment_series_name'],
                'efficiency': item['specific_load_capacity'],
                'strands': item['num_strands'],
                'layers': series.num_layers,
                'material_thickness_mm': series.strand_radius * 1000 if series.strand_radius else None,
                'weight_kg': series.weight_kg
            })

    # Sort by efficiency
    sorted_data = sorted(all_efficiency_data, key=lambda x: x['efficiency'], reverse=True)

    # Get top 5 unique configurations
    top_configs = []
    seen = set()
    for config in sorted_data:
        key = (config['strands'], config['layers'], config.get('material_thickness_mm'))
        if key not in seen and len(top_configs) < 5:
            top_configs.append({
                'strands': config['strands'],
                'layers': config['layers'],
                'material_thickness_mm': config.get('material_thickness_mm'),
                'value': config['efficiency'],
                'weight_kg': config['weight_kg'],
                'series_name': config['series_name']
            })
            seen.add(key)

    # Analyze patterns
    if all_efficiency_data:
        avg_efficiency = np.mean([c['efficiency'] for c in all_efficiency_data])

        # Find optimal parameters
        strands_list = [c['strands'] for c in sorted_data[:10]]
        layers_list = [c['layers'] for c in sorted_data[:10]]
        thickness_list = [c.get('material_thickness_mm') for c in sorted_data[:10] if c.get('material_thickness_mm')]

        # Efficiency often peaks at moderate values
        avg_strands = int(np.mean(strands_list)) if strands_list else None
        avg_layers = int(np.mean(layers_list)) if layers_list else None
        avg_thickness = np.mean(thickness_list) if thickness_list else None

        guidance = f"For best efficiency (payload/weight ratio), use moderate configurations: "
        if avg_thickness:
            guidance += f"~{avg_thickness:.1f}mm material, "
        guidance += f"~{avg_strands} strands, ~{avg_layers} layers. "
        guidance += f"Average efficiency: {avg_efficiency:.2f}× own weight"
    else:
        guidance = "No data available"
        avg_strands = None
        avg_layers = None

    return {
        'parameter': 'Structural Efficiency',
        'metric': 'Specific Load Capacity (× own weight)',
        'top_configs': top_configs,
        'general_guidance': guidance,
        'optimal_strands': avg_strands,
        'optimal_layers': avg_layers
    }
