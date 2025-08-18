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
    """Create simplified visualization showing thickness-force relationship"""
    thickness_data, failure_data = extract_failure_data()
    
    # Convert to numpy arrays for easier manipulation
    thickness = np.array(thickness_data)
    force = np.array(failure_data)
    
    # Fit power law relationship
    log_thickness = np.log(thickness)
    log_force = np.log(force)
    coeffs = np.polyfit(log_thickness, log_force, 1)
    power_exponent = coeffs[0]
    r_squared = np.corrcoef(log_thickness, log_force)[0,1]**2
    
    # Create simplified figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Main plot with both data and fit
    thickness_mm = thickness * 1000  # Convert to mm for readability
    ax.scatter(thickness_mm, force, color='blue', s=150, alpha=0.8, 
               label='Experimental Data', zorder=3)
    
    # Plot power law fit
    thickness_fit = np.linspace(thickness.min(), thickness.max(), 100)
    force_fit = np.exp(coeffs[1]) * thickness_fit**power_exponent
    thickness_fit_mm = thickness_fit * 1000
    ax.plot(thickness_fit_mm, force_fit, 'red', linewidth=3, 
            label=f'Power Law: F ∝ t^{power_exponent:.1f}', zorder=2)
    
    # Formatting
    ax.set_xlabel('Strand Thickness (mm)', fontsize=14)
    ax.set_ylabel('First Failure Force (N)', fontsize=14)
    ax.set_title('Braided Structure Strength vs Strand Thickness', fontsize=16, pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12, loc='upper left')
    
    # Add equation text box
    equation_text = f'F = k × t^{power_exponent:.1f}\nR² = {r_squared:.3f}'
    ax.text(0.95, 0.05, equation_text, transform=ax.transAxes, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
            fontsize=12, verticalalignment='bottom', horizontalalignment='right')
    
    plt.tight_layout()
    plt.show()
    
    # Simplified summary
    thickness_ratio = thickness / thickness[0]
    force_ratio = force / force[0]
    
    print("=== BRAIDED STRUCTURE STRENGTH ANALYSIS ===")
    print(f"Relationship: Power Law (F ∝ t^{power_exponent:.1f})")
    print(f"R² fit quality: {r_squared:.3f}")
    print()
    print("Key Finding: When strand thickness doubles (2x), force capacity increases by ~{:.1f}x".format(2**power_exponent))
    print()
    print("Thickness (mm)  →  Force (N)  →  Strength Multiplier")
    print("=" * 50)
    for i, (t, f, tr, fr) in enumerate(zip(thickness_mm, force, thickness_ratio, force_ratio)):
        print(f"{t:6.1f}mm      →  {f:6.3f}N  →  {fr:5.1f}x stronger")
    print()
    print(f"Mathematical formula: F = {np.exp(coeffs[1]):.3f} × t^{power_exponent:.1f}")
    print("(where F = force in Newtons, t = thickness in meters)")

if __name__ == "__main__":
    plot_thickness_force_relationship()
