import matplotlib.pyplot as plt
import numpy as np
from database.queries.experiment_series_queries import select_all_experiment_series, select_experiment_series_by_name
from database.queries.experiments_queries import select_all_experiments_by_series_name
from database.session import SessionLocal

def extract_failure_data():
    """Extract material thickness vs first failure force data"""
    session = SessionLocal()
    
    # Get all experiment series for thickness experiments
    series_names = [f"strand_thickness_experiment__{i:02d}" for i in range(6)]
    
    thickness_data = []
    failure_data = []
    
    for series_name in series_names:
        # Get experiment series to get material thickness
        series = select_experiment_series_by_name(session, series_name)
        if not series:
            continue
            
        # Get all experiments for this series
        experiments = select_all_experiments_by_series_name(session, series_name)
        
        # Find first failure force
        first_failure_force = None
        for exp in experiments:
            if (exp.time_to_beam_strain_exceed_explosion is not None or 
                exp.time_to_bounding_box_explosion is not None):
                if first_failure_force is None or abs(exp.force_in_y_direction) < abs(first_failure_force):
                    first_failure_force = abs(exp.force_in_y_direction)
        
        if first_failure_force is not None:
            thickness_data.append(series.material_thickness)
            failure_data.append(first_failure_force)
    
    session.close()
    return thickness_data, failure_data

def plot_thickness_force_relationship():
    """Create plots showing relationship between material thickness and force capacity"""
    thickness_data, failure_data = extract_failure_data()
    
    # Convert to numpy arrays for easier manipulation
    thickness = np.array(thickness_data)
    force = np.array(failure_data)
    
    # Create figure with subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot 1: Linear scale
    ax1.scatter(thickness, force, color='blue', s=100, alpha=0.7)
    ax1.plot(thickness, force, color='blue', alpha=0.5, linestyle='--')
    ax1.set_xlabel('Material Thickness (m)')
    ax1.set_ylabel('First Failure Force (N)')
    ax1.set_title('Force Capacity vs Thickness\n(Linear Scale)')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Log-log scale to see power law relationship
    ax2.loglog(thickness, force, 'bo-', markersize=8)
    ax2.set_xlabel('Material Thickness (m)')
    ax2.set_ylabel('First Failure Force (N)')
    ax2.set_title('Force Capacity vs Thickness\n(Log-Log Scale)')
    ax2.grid(True, alpha=0.3)
    
    # Fit power law on log-log scale
    log_thickness = np.log(thickness)
    log_force = np.log(force)
    coeffs = np.polyfit(log_thickness, log_force, 1)
    power_exponent = coeffs[0]
    
    # Plot fitted line
    thickness_fit = np.linspace(thickness.min(), thickness.max(), 100)
    force_fit = np.exp(coeffs[1]) * thickness_fit**power_exponent
    ax2.plot(thickness_fit, force_fit, 'r--', linewidth=2, 
             label=f'Power Law Fit: F ∝ t^{power_exponent:.2f}')
    ax2.legend()
    
    # Plot 3: Thickness ratio vs force ratio
    thickness_ratio = thickness / thickness[0]  # Normalize to thinnest
    force_ratio = force / force[0]  # Normalize to weakest
    
    ax3.scatter(thickness_ratio, force_ratio, color='green', s=100, alpha=0.7)
    ax3.plot(thickness_ratio, force_ratio, color='green', alpha=0.5, linestyle='--')
    
    # Add reference lines
    ax3.plot(thickness_ratio, thickness_ratio, 'k--', alpha=0.5, label='Linear (1:1)')
    ax3.plot(thickness_ratio, thickness_ratio**2, 'r--', alpha=0.5, label='Quadratic (t²)')
    ax3.plot(thickness_ratio, thickness_ratio**3, 'm--', alpha=0.5, label='Cubic (t³)')
    
    ax3.set_xlabel('Thickness Ratio (relative to thinnest)')
    ax3.set_ylabel('Force Capacity Ratio (relative to weakest)')
    ax3.set_title('Scaling Relationship:\nThickness vs Force Capacity')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Print summary statistics
    print(f"Power law exponent: {power_exponent:.2f}")
    print(f"R² correlation: {np.corrcoef(log_thickness, log_force)[0,1]**2:.3f}")
    print("\nThickness -> Force scaling:")
    for i, (t, f) in enumerate(zip(thickness, force)):
        print(f"  {t:.4f}m ({thickness_ratio[i]:.1f}x) -> {f:.3f}N ({force_ratio[i]:.1f}x)")
    
    plt.show()

if __name__ == "__main__":
    plot_thickness_force_relationship()
