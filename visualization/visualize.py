import pychrono as chrono
import pychrono.irrlicht as irr

def create_visualization(system, floor, braided_mesh):
    # create visualization for mesh
    visualizemesh = chrono.ChVisualShapeFEA(braided_mesh)
    visualizemesh.SetFEMdataType(chrono.ChVisualShapeFEA.DataType_ELEM_BEAM_TY)
    visualizemesh.SetColorscaleMinMax(-0.5, 0.5)
    visualizemesh.SetSmoothFaces(True)
    visualizemesh.SetWireframe(False)
    braided_mesh.AddVisualShapeFEA(visualizemesh)

    visualizefloor = chrono.ChVisualShapeBox(chrono.ChVector3d(5, 0.1, 5))
    visualizefloor.SetColor(chrono.ChColor(0.2, 0.2, 0.2))
    floor.AddVisualShape(visualizefloor)

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

    return vis