import pychrono as chrono
import pychrono.pardisomkl as mkl
import pychrono.fea as fea

from physics_model import create_braid_mesh, create_braid_material, create_floor_material

system = chrono.ChSystemSMC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))  # gravity

braid_mesh = create_braid_mesh()
braid_material = create_braid_material(material_radius = 0.008)
floor_material = create_floor_material()

system.Add(braid_mesh)

from structures import create_floor, create_braid_structure

floor = create_floor(system, floor_material)
layers, top_nodes, node_positions = create_braid_structure(braid_mesh, braid_material)


from forces import apply_force_to_all_nodes, apply_force_to_top_nodes, place_box

# apply_force_to_all_nodes(layers)
# apply_force_to_top_nodes(top_nodes, force_in_y_direction=-90)

place_box(top_nodes, system, floor_material)


from visualization import create_visualization

will_visualize = True
visualization = None

if (will_visualize):
    visualization = create_visualization(system, floor, braid_mesh, node_positions)

# Changes the solver from the default SOR to the MKL Pardiso, more precise for fea.
linear_solver = mkl.ChSolverPardisoMKL()
linear_solver.LockSparsityPattern(True)
system.SetSolver(linear_solver)

# Simulation loop
timestep = 0.01

while not will_visualize or visualization.Run():
 
	system.DoStepDynamics(timestep)

	if will_visualize:
		visualization.BeginScene()
		visualization.Render()
		# visualization.WriteImageToFile("braid" + f'{int(system.GetChTime() / timestep):05d}' + ".jpg")
		visualization.EndScene()

