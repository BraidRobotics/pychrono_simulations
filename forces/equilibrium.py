from dataclasses import dataclass

@dataclass
class EquilibriumThresholds:
	# todo remember to change the target strain if I change the material
	# Nylon typically has a yield strain between 2–10%, with elastic deformation typically below 1%
	target_strain: float = 0.01          # 1%, typical elastic limit for Nylon 
	strain_tolerance: float = 1e-6       # minimal strain change per timestep
	stability_timesteps: int = 1000        # must maintain thresholds for 1000 steps

thresholds = EquilibriumThresholds()

if thresholds.stability_timesteps < 1:
	thresholds.stability_timesteps = 1
	
def is_in_equilibrium(max_beam_strain, _max_node_velocity):
	if not hasattr(is_in_equilibrium, "previous_strain"):
		is_in_equilibrium.previous_strain = max_beam_strain
		is_in_equilibrium.consecutive_stable_steps = 0

	'''
		Equilibrium criterion based on strain rate:
		|(ε_current - ε_previous) / Δt| ≤ strain_tolerance
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


