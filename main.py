import pychrono as chrono
import pychrono.pardisomkl as mkl
import pychrono.fea as fea

from physics_model import create_braid_mesh, create_braid_material, create_floor_material

system = chrono.ChSystemSMC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

braid_mesh = create_braid_mesh()
braid_material = create_braid_material(material_radius = 0.002)
floor_material = create_floor_material()

from structures import create_floor, create_braid_structure

layers, top_nodes, node_positions = create_braid_structure(braid_mesh, braid_material)


for node in top_nodes:
   node.SetForce(chrono.ChVector3d(0, 0.2, 0))
        
floor = create_floor(system, floor_material)

# small box 
# box = chrono.ChBodyEasyBox(0.2,0.2,0.2, 2700, True, True, surface_material)
# box.SetPos( chrono.ChVector3d( 0,1,0))
# system.Add( box )

# Add the mesh to the system
system.Add(braid_mesh)


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

