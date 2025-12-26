from dataclasses import dataclass

@dataclass
class EquilibriumThresholds:
	# todo remember to adjust these if simulating different materials
	# Target strain should match the material's elastic limit
	# Rubber-like material (E=100 MPa) has elastic limit around 5-10%
	target_strain: float = 0.05          # 5%, typical elastic limit for rubber-like materials 
	strain_tolerance: float = 1e-6       # minimal strain change per timestep
	stability_timesteps: int = 1000        # must maintain below the thresholds for 10 seconds with a 0.1 simulation time step

thresholds = EquilibriumThresholds()

if thresholds.stability_timesteps < 1:
	thresholds.stability_timesteps = 1
	
def is_in_equilibrium(max_beam_strain):
	if not hasattr(is_in_equilibrium, "previous_strain"):
		is_in_equilibrium.previous_strain = max_beam_strain
		is_in_equilibrium.consecutive_stable_steps = 0

	'''
		Equilibrium criteria:
		1. Maximum strain within elastic limit: ε_max ≤ ε_target
		2. Strain change per timestep negligible: |ε_current - ε_previous| ≤ ε_tolerance
	'''
	strain_delta = abs(max_beam_strain - is_in_equilibrium.previous_strain)
	strain_stable = (
		max_beam_strain <= thresholds.target_strain and 
		strain_delta <= thresholds.strain_tolerance
	)

	if strain_stable:
		is_in_equilibrium.consecutive_stable_steps += 1
	else:
		is_in_equilibrium.consecutive_stable_steps = 0

	consecutive_steps_met = is_in_equilibrium.consecutive_stable_steps >= thresholds.stability_timesteps

	is_in_equilibrium.previous_strain = max_beam_strain

	return strain_stable and consecutive_steps_met

def reset_equilibrium_state():
	"""Reset the equilibrium detection state between experiments"""
	if hasattr(is_in_equilibrium, "previous_strain"):
		delattr(is_in_equilibrium, "previous_strain")
	if hasattr(is_in_equilibrium, "consecutive_stable_steps"):
		delattr(is_in_equilibrium, "consecutive_stable_steps")


