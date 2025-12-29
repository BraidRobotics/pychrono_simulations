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

    # Compute trade-offs for each category
    _compute_trade_offs(session, recommendations, compression_data, recovery_data,
                        thickness_force + layer_force + strand_force,
                        thickness_efficiency + layer_efficiency + strand_efficiency)

    return recommendations


MAJOR_EXPERIMENT_GROUPS = ['force_no_force', 'number_of_strands', 'number_of_layers', 'strand_thickness']


def _is_major_series(session, series_name):
    """Check if a series belongs to one of the 4 major experiment groups"""
    series = session.query(ExperimentSeries).filter_by(
        experiment_series_name=series_name
    ).first()
    if not series or not series.group_name:
        return False
    return any(group in series.group_name for group in MAJOR_EXPERIMENT_GROUPS)


def _find_similar_compression(compression_data, strands, layers, material_mm):
    """Find a similar configuration in compression data based on parameters.
    Returns the max_compression_pct of the closest match, or None if no data."""
    if not compression_data:
        return None

    # Try exact match first
    for c in compression_data:
        c_material_mm = c.get('strand_radius', 0) * 1000 if c.get('strand_radius') else None
        if (c['num_strands'] == strands and c['num_layers'] == layers and
            c_material_mm is not None and material_mm is not None and
            abs(c_material_mm - material_mm) < 0.1):
            return c['max_compression_pct']

    # Try matching strands and layers only
    for c in compression_data:
        if c['num_strands'] == strands and c['num_layers'] == layers:
            return c['max_compression_pct']

    # Try matching just strands (most important factor)
    matches = [c for c in compression_data if c['num_strands'] == strands]
    if matches:
        return np.mean([c['max_compression_pct'] for c in matches])

    return None


def _compute_trade_offs(session, recommendations, compression_data, recovery_data, force_data, efficiency_data):
    """Compute how each recommendation fares on other metrics.
    Only includes data from the 4 major experiment groups:
    force_no_force, number_of_strands, number_of_layers, strand_thickness
    """

    # Build lookup maps by series name (filtered to major groups)
    compression_map = {c['experiment_series_name']: c for c in compression_data
                       if _is_major_series(session, c['experiment_series_name'])} if compression_data else {}

    # Build recovery map with normalized efficiency (filtered to major groups)
    recovery_map = {}
    for config in recovery_data or []:
        if not _is_major_series(session, config['experiment_series_name']):
            continue
        series = session.query(ExperimentSeries).filter_by(
            experiment_series_name=config['experiment_series_name']
        ).first()
        if series and series.final_force_in_y_direction:
            applied_force = abs(series.final_force_in_y_direction)
            normalized_efficiency = config['recovery_percent'] / applied_force if applied_force > 0 else 0
            recovery_map[config['experiment_series_name']] = {
                'recovery_percent': config['recovery_percent'],
                'normalized_efficiency': normalized_efficiency,
                'applied_force': applied_force
            }

    # Filter force and efficiency data to major groups only
    force_map = {f['experiment_series_name']: f['force'] for f in force_data
                 if _is_major_series(session, f['experiment_series_name'])} if force_data else {}
    efficiency_map = {e['experiment_series_name']: e['specific_load_capacity'] for e in efficiency_data
                      if _is_major_series(session, e['experiment_series_name'])} if efficiency_data else {}

    # Also add force/efficiency from compression_data (force_no_force experiments)
    # These have target_force which is the applied force
    for c in compression_data or []:
        series_name = c['experiment_series_name']
        if not _is_major_series(session, series_name):
            continue
        if series_name not in force_map and 'target_force' in c:
            force_map[series_name] = c['target_force']
        # Calculate efficiency for force_no_force if not already present
        if series_name not in efficiency_map:
            series = session.query(ExperimentSeries).filter_by(
                experiment_series_name=series_name
            ).first()
            if series and series.weight_kg and 'target_force' in c:
                weight_force = series.weight_kg * 9.81
                if weight_force > 0:
                    efficiency_map[series_name] = c['target_force'] / weight_force

    # Calculate averages for comparison (using only major groups data)
    major_compression = [c for c in compression_data if _is_major_series(session, c['experiment_series_name'])] if compression_data else []
    avg_compression = np.mean([c['max_compression_pct'] for c in major_compression]) if major_compression else 0
    avg_force = np.mean(list(force_map.values())) if force_map else 0
    avg_efficiency = np.mean(list(efficiency_map.values())) if efficiency_map else 0
    avg_recovery_eff = np.mean([r['normalized_efficiency'] for r in recovery_map.values()]) if recovery_map else 0

    # Flexibility trade-offs (how it performs on load-bearing and efficiency)
    if recommendations['flexibility']['top_configs']:
        top_flex = recommendations['flexibility']['top_configs'][0]
        series_name = top_flex['series_name']
        force_val = force_map.get(series_name)
        eff_val = efficiency_map.get(series_name)
        rec_val = recovery_map.get(series_name)

        recommendations['flexibility']['trade_offs'] = {
            'load_bearing': {
                'value': force_val,
                'avg': avg_force,
                'pct_of_avg': (force_val / avg_force * 100) if force_val and avg_force else None
            },
            'efficiency': {
                'value': eff_val,
                'avg': avg_efficiency,
                'pct_of_avg': (eff_val / avg_efficiency * 100) if eff_val and avg_efficiency else None
            },
            'recovery': {
                'value': rec_val['normalized_efficiency'] if rec_val else None,
                'avg': avg_recovery_eff,
                'pct_of_avg': (rec_val['normalized_efficiency'] / avg_recovery_eff * 100) if rec_val and avg_recovery_eff else None
            }
        }

    # Recovery trade-offs
    if recommendations['recovery']['top_configs']:
        top_rec = recommendations['recovery']['top_configs'][0]
        series_name = top_rec['series_name']
        force_val = force_map.get(series_name)
        eff_val = efficiency_map.get(series_name)
        comp_val = compression_map.get(series_name, {}).get('max_compression_pct')

        recommendations['recovery']['trade_offs'] = {
            'load_bearing': {
                'value': force_val,
                'avg': avg_force,
                'pct_of_avg': (force_val / avg_force * 100) if force_val and avg_force else None
            },
            'efficiency': {
                'value': eff_val,
                'avg': avg_efficiency,
                'pct_of_avg': (eff_val / avg_efficiency * 100) if eff_val and avg_efficiency else None
            },
            'flexibility': {
                'value': comp_val,
                'avg': avg_compression,
                'pct_of_avg': (comp_val / avg_compression * 100) if comp_val and avg_compression else None
            }
        }

    # Load-bearing trade-offs
    if recommendations['high_load_bearing']['top_configs']:
        top_load = recommendations['high_load_bearing']['top_configs'][0]
        series_name = top_load['series_name']
        comp_val = compression_map.get(series_name, {}).get('max_compression_pct')
        # If not found in compression_map, try to find similar config
        if comp_val is None:
            comp_val = _find_similar_compression(
                compression_data,
                top_load['strands'],
                top_load['layers'],
                top_load.get('material_thickness_mm')
            )
        eff_val = efficiency_map.get(series_name)
        rec_val = recovery_map.get(series_name)

        recommendations['high_load_bearing']['trade_offs'] = {
            'flexibility': {
                'value': comp_val,
                'avg': avg_compression,
                'pct_of_avg': (comp_val / avg_compression * 100) if comp_val and avg_compression else None
            },
            'efficiency': {
                'value': eff_val,
                'avg': avg_efficiency,
                'pct_of_avg': (eff_val / avg_efficiency * 100) if eff_val and avg_efficiency else None
            },
            'recovery': {
                'value': rec_val['normalized_efficiency'] if rec_val else None,
                'avg': avg_recovery_eff,
                'pct_of_avg': (rec_val['normalized_efficiency'] / avg_recovery_eff * 100) if rec_val and avg_recovery_eff else None
            }
        }

    # Efficiency trade-offs
    if recommendations['best_efficiency']['top_configs']:
        top_eff = recommendations['best_efficiency']['top_configs'][0]
        series_name = top_eff['series_name']
        force_val = force_map.get(series_name)
        comp_val = compression_map.get(series_name, {}).get('max_compression_pct')
        # If not found in compression_map, try to find similar config
        if comp_val is None:
            comp_val = _find_similar_compression(
                compression_data,
                top_eff['strands'],
                top_eff['layers'],
                top_eff.get('material_thickness_mm')
            )
        rec_val = recovery_map.get(series_name)

        recommendations['best_efficiency']['trade_offs'] = {
            'load_bearing': {
                'value': force_val,
                'avg': avg_force,
                'pct_of_avg': (force_val / avg_force * 100) if force_val and avg_force else None
            },
            'flexibility': {
                'value': comp_val,
                'avg': avg_compression,
                'pct_of_avg': (comp_val / avg_compression * 100) if comp_val and avg_compression else None
            },
            'recovery': {
                'value': rec_val['normalized_efficiency'] if rec_val else None,
                'avg': avg_recovery_eff,
                'pct_of_avg': (rec_val['normalized_efficiency'] / avg_recovery_eff * 100) if rec_val and avg_recovery_eff else None
            }
        }


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
