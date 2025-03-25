import pychrono as chrono
import pychrono.fea as fea
import pychrono.pardisomkl as mkl
import pychrono.irrlicht as irr
import math

# parameters for the braid
num_rods = 12   #has to be an even number
radius = 0.15
pitch = 1.13
num_layers = 10

# Create a Chrono physical system
system = chrono.ChSystemSMC()
system.SetCollisionSystemType( chrono.ChCollisionSystem.Type_BULLET )

# Create a mesh, that is a container for groups of elements and nodes
mesh = fea.ChMesh()
mesh.SetAutomaticGravity(True)

# Create a material for the braid
material_radius = 0.002
braidmaterial = fea.ChBeamSectionEulerSimple()
braidmaterial.SetAsCircularSection( material_radius )
braidmaterial.SetYoungModulus( 1.72e10 ) # Glass-reinforced polyester (GRP) - https://en.wikipedia.org/wiki/Young%27s_modulus
braidmaterial.SetDensity( 1200 )  # 1.2 g/cm^3 = 1200kg/m^3  
#material.SetShearModulus(0.01e9 * 0.3)
#material.SetRayleighDamping(0.000)

# create material for floor
surfacematerial = chrono.ChContactMaterialSMC()

# generate points
num_intersections = int( num_rods/2 )   # two rods insect at each point

layers= []
for layer_no in range(num_layers):
    current_layer = []
    for point_no in range(num_intersections):
        current_angle = layer_no*2*math.pi/(2*num_intersections) + point_no/num_intersections * 2 * math.pi
        current_point = chrono.ChVector3d(radius * math.cos(current_angle), layer_no * pitch / num_rods, radius * math.sin(current_angle))
        current_node = fea.ChNodeFEAxyzrot( chrono.ChFramed( current_point ) )       
        mesh.AddNode( current_node )
        if layer_no == 0:
            current_node.SetFixed( True )  
        current_layer.append( current_node )
    layers.append( current_layer )



topnodes = []

for rods in range(int(num_rods/2)):

    # counter clock-wise
    builderccw = fea.ChBuilderBeamEuler()
    for layer_no in range(num_layers-1):
        builderccw.BuildBeam( mesh,
                              braidmaterial,
                              10,
                              layers[layer_no][rods],
                              layers[layer_no+1][rods],
                              chrono.ChVector3d( 0,1,0 ) )
    
        
    # clock-wise
    buildercw = fea.ChBuilderBeamEuler()
    if rods > 0:
        for layer_no in range(0,num_layers-1):
            buildercw.BuildBeam( mesh,
                                 braidmaterial,
                                 10,
                                 layers[layer_no][rods],
                                 layers[layer_no+1][rods-1],
                                 chrono.ChVector3d( 0,1,0 ) )
    else:
        for layer_no in range(0,num_layers-1):
            buildercw.BuildBeam( mesh,
                                 braidmaterial,
                                 10,
                                 layers[layer_no][rods],
                                 layers[layer_no+1][int(num_rods/2)-1],
                                 chrono.ChVector3d( 0,1,0 ) )
    topnodes.append( buildercw.GetLastBeamNodes()[-1] )

#for node in topnodes:
#    print(node.GetPos())
#    node.SetForce( chrono.ChVector3d( 0, 0.02, 0 ))
        
# create floor
floor = chrono.ChBodyEasyBox(5,0.1,5, 2700, True, True, surfacematerial)
floor.SetFixed( True )
floor.SetPos( chrono.ChVector3d( 0,-0.1,0))
system.Add( floor )

# small box 
#box = chrono.ChBodyEasyBox(0.2,0.2,0.2, 2700, True, True, surfacematerial)
#box.SetPos( chrono.ChVector3d( 0,1,0))
#system.Add( box )

# Add the mesh to the system
system.Add(mesh)

visualization = True

if (visualization):
    # create visualization for mesh
    visualizemesh = chrono.ChVisualShapeFEA(mesh)
    visualizemesh.SetFEMdataType(chrono.ChVisualShapeFEA.DataType_ELEM_BEAM_TY)
    visualizemesh.SetColorscaleMinMax(-0.5, 0.5)
    visualizemesh.SetSmoothFaces(True)
    visualizemesh.SetWireframe(False)
    mesh.AddVisualShapeFEA(visualizemesh)

    visualizefloor = chrono.ChVisualShapeBox( chrono.ChVector3d( 5,0.1,5) )
    visualizefloor.SetColor( chrono.ChColor( 0.2, 0.2, 0.2 ))
    floor.AddVisualShape( visualizefloor )

    # Create a visualization system
    vis = irr.ChVisualSystemIrrlicht()
    vis.AttachSystem(system)
    vis.SetWindowSize(600, 1200)
    vis.SetWindowTitle("Biaxial Braid Simulation")
    vis.SetShadows( True )
    vis.Initialize()
    vis.AddSkyBox()
    #vis.AddGrid( 0.1, 0.1, 2, 20 )
    vis.AddCamera(chrono.ChVector3d(0.5, 1, 0.5), chrono.ChVector3d(0, 0.5, 0))
    vis.AddTypicalLights()

# Change the solver form the default SOR to the MKL Pardiso, more precise for fea.
msolver = mkl.ChSolverPardisoMKL()
# msolver.LockSparsityPattern( True )
system.SetSolver(msolver)

# Simulation loop
index = 0
while (not visualization and index < 600) or (visualization and vis.Run()):

    system.DoStepDynamics(0.01)
    if (visualization):
        vis.BeginScene()
        vis.Render()
        #vis.WriteImageToFile("braid" + f'{index:05d}' + ".jpg")
        vis.EndScene()    
    
    index = index + 1

