from dataclasses import dataclass

@dataclass
class EquilibriumThresholds:
	# todo remember to change the target strain if I change the material
	# Nylon typically has a yield strain between 2–10%, with elastic deformation typically below 1%
	target_strain: float = 0.01          # 1%, typical elastic limit for Nylon 
	strain_tolerance: float = 1e-6       # minimal strain change per timestep
	max_node_velocity: float = 0.1       # meters but without time step
	stability_timesteps: int = 10        # must maintain thresholds for 10 steps

thresholds = EquilibriumThresholds()
	
def is_in_equilibrium(max_beam_strain, max_node_velocity):
	if not hasattr(is_in_equilibrium, "previous_strain"):
		is_in_equilibrium.previous_strain = max_beam_strain
		is_in_equilibrium.velocity_history = [max_node_velocity] * thresholds.stability_timesteps

	'''
	Strain and Strain rate: Bathe, Klaus-Jürgen. Finite Element Procedures. MIT, 2014.
		Equilibrium criterion based on strain rate:
		|(ε_current - ε_previous) / Δt| ≤ strain_tolerance
	'''
	strain_rate = abs(max_beam_strain - is_in_equilibrium.previous_strain)
	strain_stable = (
		max_beam_strain <= thresholds.target_strain and 
		strain_rate <= thresholds.strain_tolerance
	)

	is_in_equilibrium.velocity_history.append(max_node_velocity)
	if len(is_in_equilibrium.velocity_history) > thresholds.stability_timesteps:
		is_in_equilibrium.velocity_history.pop(0)

	'''
	Velocity criterion: Chopra, Anil K. Dynamics of Structures: Theory and Applications to Earthquake Engineering. Pearson, 2016.
		Equilibrium criterion based on velocity:
		max(v_node) ≤ max_node_velocity for stability_timesteps consecutive steps.
	'''
	velocity_stable = all(
		timesteps_max_node_velocity <= thresholds.max_node_velocity
		for timesteps_max_node_velocity in is_in_equilibrium.velocity_history
	)

	is_in_equilibrium.previous_strain = max_beam_strain

	return strain_stable and velocity_stable
