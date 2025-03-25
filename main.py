import pychrono as chrono
import pychrono.pardisomkl as mkl
import pychrono.fea as fea

from physics_mesh_material import setup_system, create_braid_mesh, create_braid_material, create_floor_material

system = setup_system()

braid_mesh = create_braid_mesh()
braid_material = create_braid_material()
floor_material = create_floor_material()

from structures import create_floor, create_braid_structure

layers, top_nodes = create_braid_structure(braid_mesh, braid_material)


# for node in top_nodes:
#    print(node.GetPos())
#    node.SetForce(chrono.ChVector3d(0, 0.2, 0))
        
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
    visualization = create_visualization(system, floor, braid_mesh)

# Change the solver form the default SOR to the MKL Pardiso, more precise for fea.
msolver = mkl.ChSolverPardisoMKL()
# msolver.LockSparsityPattern( True )
system.SetSolver(msolver)

# Simulation loop
index = 0
while (not will_visualize and index < 600) or (will_visualize and visualization.Run()):

    system.DoStepDynamics(0.01)

    if (will_visualize):
        visualization.BeginScene()
        visualization.Render()
        #vis.WriteImageToFile("braid" + f'{index:05d}' + ".jpg")
        visualization.EndScene()    
    
    index = index + 1

