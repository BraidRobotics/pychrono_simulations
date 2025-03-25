import pychrono as chrono
import pychrono.pardisomkl as mkl
import pychrono.fea as fea

from physics_mesh_material import setup_system, create_braid_mesh, create_braid_material, create_surface_material

system = setup_system()

braid_mesh = create_braid_mesh()
braid_material = create_braid_material()
surface_material = create_surface_material()

from structures import create_floor, create_braided_structure

# layers, top_nodes = create_braided_structure(braid_mesh, braid_material)


######################################################################################################
#### parameters for the braid ########################################################################
######################################################################################################
######################################################################################################
import math

num_rods = 12   # has to be an even number
radius = 0.15
pitch = 1.13
num_layers = 10

# generate points
num_intersections = int(num_rods / 2)   # two rods insect at each point

######################################################################################################
######################################################################################################
######################################################################################################

layers= []
for layer_no in range(num_layers):
    current_layer = []
    for point_no in range(num_intersections):
        current_angle = layer_no*2*math.pi/(2*num_intersections) + point_no/num_intersections * 2 * math.pi
        current_point = chrono.ChVector3d(radius * math.cos(current_angle), layer_no * pitch / num_rods, radius * math.sin(current_angle))
        current_node = fea.ChNodeFEAxyzrot( chrono.ChFramed( current_point ) )       
        braid_mesh.AddNode( current_node )
        if layer_no == 0:
            current_node.SetFixed( True )  
        current_layer.append( current_node )
    layers.append( current_layer )



topnodes = []

for rods in range(int(num_rods/2)):

    # counter clock-wise
    builderccw = fea.ChBuilderBeamEuler()
    for layer_no in range(num_layers-1):
        builderccw.BuildBeam(braid_mesh,
                            braid_material,
                            10,
                            layers[layer_no][rods],
                            layers[layer_no+1][rods],
                            chrono.ChVector3d( 0,1,0 ) )
    
        
    # clock-wise
    buildercw = fea.ChBuilderBeamEuler()
    if rods > 0:
        for layer_no in range(0,num_layers-1):
            buildercw.BuildBeam(braid_mesh,
                                braid_material,
                                10,
                                layers[layer_no][rods],
                                layers[layer_no+1][rods-1],
                                chrono.ChVector3d( 0,1,0 ) )
    else:
        for layer_no in range(0,num_layers-1):
            buildercw.BuildBeam(braid_mesh,
                                braid_material,
                                10,
                                layers[layer_no][rods],
                                layers[layer_no+1][int(num_rods/2)-1],
                                chrono.ChVector3d( 0,1,0 ) )
    topnodes.append( buildercw.GetLastBeamNodes()[-1] )


#for node in top_nodes:
#    print(node.GetPos())
#    node.SetForce( chrono.ChVector3d( 0, 0.02, 0 ))
        
floor = create_floor(system, surface_material)

# small box 
#box = chrono.ChBodyEasyBox(0.2,0.2,0.2, 2700, True, True, surfacematerial)
#box.SetPos( chrono.ChVector3d( 0,1,0))
#system.Add( box )

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

